import os
import aio_pika


async def create_connection():
    # Crear una conexión a RabbitMQ con SSL
    connection = await aio_pika.connect_robust(
        host=os.environ.get("RABBITMQ_IP"),
        port=5671,  # El puerto para SSL suele ser 5671
        login=os.environ.get("RABBITMQ_USER"),
        password=os.environ.get("RABBITMQ_PASS"),
        ssl=True,  # Especificamos que queremos una conexión SSL
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