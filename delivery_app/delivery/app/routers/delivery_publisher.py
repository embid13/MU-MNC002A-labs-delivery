import asyncio
import aio_pika
from os import environ

# Get the variables from environment.
class Config:
    RABBITMQ_IP = environ.get("RABBITMQ_IP")
    RABBITMQ_USER = environ.get("RABBITMQ_USER")
    RABBITMQ_PASS = environ.get("RABBITMQ_PASS")

#TODO
#RABBITMQ + SSL
async def create_connection():
    # Crear una conexión a RabbitMQ sin SSL
    connection = await aio_pika.connect_robust(
        host=Config.RABBITMQ_IP,
        port=5672,  # El puerto predeterminado sin SSL es 5672
        login=Config.RABBITMQ_USER,
        password=Config.RABBITMQ_PASS
    )
    return connection


async def create_channel(connection):
    # Crear un canal en la conexión
    channel = await connection.channel()
    return channel


async def declare_exchange(channel, exchange_name, exchange_type):
    # Declarar un intercambio en el canal
    await channel.exchange_declare(
        exchange=exchange_name,
        exchange_type=exchange_type
    )


async def publish_msg(exchange_name, routing_key, message):
    connection = await create_connection()
    channel = await create_channel(connection)

    # Declarar el intercambio si no existe
    await declare_exchange(channel, exchange_name, 'topic')

    # Publicar el mensaje
    await channel.publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=message.encode()
    )

    print(f"[x] Sent {routing_key}:{message}")

    # Cerrar la conexión y el canal
    await channel.close()
    await connection.close()


async def publish_log(message):
    exchange = 'logger_exchange'
    routing_key = f"{message['microservice']}.{message['type']}"

    connection = await create_connection()
    channel = await create_channel(connection)

    # Declarar el intercambio si no existe
    await declare_exchange(channel, exchange, 'topic')

    # Publicar el mensaje
    await channel.publish(
        exchange=exchange,
        routing_key=routing_key,
        body=message['message'].encode()
    )

    # Cerrar la conexión y el canal
    await channel.close()
    await connection.close()
