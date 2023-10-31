import json
import asyncio
import aio_pika
import logging
import os
import requests
import jwt
from app.sql.database import SessionLocal
from app.sql import crud, schemas
from .delivery_router_utils import raise_and_log_error
from fastapi import status
from app.routers.keys import RSAKeys


logger = logging.getLogger(__name__)

"""
    El cliente manda usuario y contraseña a AUTH, AUTH le responde con un JWT firmado. 
    AUTH mandará el public key a todos los microservicios.
    En cada solicitud, Delivery va a recibir un JWT, NUNCA UN REFRESH TOKEN.
    Comprobar si está caducado o no, en caso de estar caducado HTTP 401 (No autorizado).
    Comprobar si tiene los permisos necesarios en cada caso, si no los tiene HTTP 403 (Prohibido.)
"""


class AsyncConsumer:
    def __init__(self, exchange_name, routing_key, callback_func):
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.callback_func = callback_func

    async def start_consuming(self):
        logger.info("Waiting for RabbitMQ")
        connection = await aio_pika.connect_robust(
            "amqp://guest:guest@192.168.17.46/",
            port=5671,
            ssl=True,
            loop=asyncio.get_event_loop()
        )

        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)  # Recibir un mensaje a la vez
            exchange = await channel.declare_exchange(self.exchange_name, type=aio_pika.ExchangeType.TOPIC)
            queue = await channel.declare_queue("", exclusive=True)
            await queue.bind(exchange, routing_key=self.routing_key)

            async with queue.iterator() as queue_iterator:
                async for message in queue_iterator:
                    async with message.process():
                        await self.callback_func(message.body, exchange)

    @staticmethod
    async def on_delivery_received(body):
        logger.debug("on_delivery_received called")
        logger.debug("Getting database SessionLocal")
        db = SessionLocal()

        # Decode the JSON message
        content = json.loads(body.decode('utf-8'))
        delivery_schema = schemas.deliveryBase(delivery_id=content['order_id'], status=content['status'],
                                               location=content['location'], user_id=content['user_id'])
        logger.debug("delivery_schema:")
        logger.debug(delivery_schema)

        try:
            await crud.add_new_delivery(db, delivery_schema)
        except Exception as exc:
            raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error {exc}")
        print("Successful operation.")

    @staticmethod
    async def on_delivery_ready(body):
        logger.debug("on_delivery_ready called")
        logger.debug("Getting database SessionLocal")
        db = SessionLocal()

        # Decode the JSON message
        content = json.loads(body.decode('utf-8'))
        delivery_schema = schemas.deliveryReady(delivery_id=content['order_id'], status=content['status'])
        try:
            await crud.update_delivery(db, delivery_schema)
        except Exception as exc:
            raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error {exc}")
        print("Successful operation.")

    @staticmethod
    async def ask_public_key(body, exchange):
        logger.debug("GETTING PUBLIC KEY")
        endpoint = "http://192.168.17.11/auth/public-key"

        try:
            response = requests.get(endpoint)

            if response.status_code == 200:
                x = response.json()["public_key"]
                RSAKeys.public_key = x
            else:
                print(f"Error al obtener la clave pública. Código de respuesta: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error de solicitud: {e}")
