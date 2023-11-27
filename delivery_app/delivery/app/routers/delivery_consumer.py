import json
import asyncio
import aio_pika
import logging
import os
import requests
from app.sql.database import SessionLocal
from app.sql import crud, schemas
from .delivery_router_utils import raise_and_log_error
from fastapi import status
from app.routers.keys import RSAKeys
from app.routers.delivery_publisher import publish_msg
from app.routers.log_publisher import publish_log_msg


logger = logging.getLogger(__name__)


"""
example:
{
    "order_id": 2,
    "status": "ASD",
    "location": "asdasda 16",
    "user_id": 2,
    "postal_code": 20230
}

logs: si es error del cliente, WARNING, si es error de la app, ERROR.

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
    async def on_delivery_received(body, exchange):
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
            await publish_log_msg(exc, "ERROR", os.path.basename(__file__))
        print("Successful operation.")


    @staticmethod
    async def update_delivery_status(body, exchange):
        logger.debug("on_delivery_ready called")
        logger.debug("Getting database SessionLocal")
        db = SessionLocal()

        # Decode the JSON message
        content = json.loads(body.decode('utf-8'))
        delivery_schema = schemas.deliveryUpdateStatus(delivery_id=content['order_id'], status=content['status'])
        try:
            await crud.update_delivery(db, delivery_schema)
        except Exception as exc:
            raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error {exc}")
            await publish_log_msg(exc, "ERROR", os.path.basename(__file__))
        print("Successful operation.")



    @staticmethod
    async def reserve_delivery(body, exchange):
        logger.info("reserve_delivery called")

        # Decode the JSON message
        content = json.loads(body.decode('utf-8'))
        logger.info(content)
        if validate_postal_code(content['postal_code']):
            delivery_schema = schemas.deliveryBase(delivery_id=content['order_id'], status="RESERVED",
                                               location=content['location'], user_id=content['user_id'],
                                                postal_code=content['postal_code'])
            db = SessionLocal()
            logger.info("SCHEMA:")
            logger.info(delivery_schema)
            try:
                await crud.add_new_delivery(db, delivery_schema)
            except Exception as exc:
                await publish_log_msg(exc, "ERROR", os.path.basename(__file__))
                raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error {exc}")
            await publish_msg('sagas_exchange', 'delivery.valid', "Correct postal code. ;-)")
            logger.info("Postal code successful")
        else:
            logger.info("Bad postal code.")
            await publish_msg('sagas_exchange', 'delivery.reject', "Wrong postal code.")

    @staticmethod
    async def release_delivery(body, exchange):
        logger.info("release_delivery called")

        content = json.loads(body.decode('utf-8'))
        delivery_schema = schemas.deliveryUpdateStatus(delivery_id=content['order_id'], status="REJECTED")
        db = SessionLocal()
        try:
            await crud.update_delivery(db, delivery_schema)
        except Exception as exc:
            raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error {exc}")
            await publish_log_msg(exc, "ERROR", os.path.basename(__file__))
        print("Successful operation.")

    @staticmethod
    async def ask_public_key(body, exchange):
        logger.debug("GETTING PUBLIC KEY")
        endpoint = "http://192.168.17.11/auth/public-key"

        try:
            response = requests.get(endpoint)

            if response.status_code == 200:
                x = response.json()["public_key"]
                RSAKeys.set_public_key(x)
            else:
                print(f"Error al obtener la clave pública. Código de respuesta: {response.status_code}")
        except requests.exceptions.RequestException as e:
            await publish_log_msg(e, "ERROR", os.path.basename(__file__))
            print(f"Error de solicitud: {e}")


def validate_postal_code(postal_code):
    valid_prefixes = ['48', '01', '20']  # Códigos de Bizkaia (48), Álava (01) y Gipuzkoa (20).
    logger.info("validate_postal_code called")

    postal_code_str = str(postal_code)  # Convert integer to string

    if postal_code_str[:2] in valid_prefixes and postal_code_str.isdigit() and len(postal_code_str) == 5:
        return True
    else:
        return False