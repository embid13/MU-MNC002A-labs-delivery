import aio_pika
import logging
import asyncio


logger = logging.getLogger(__name__)


async def publish_msg(routing_key, message):

    logger.debug("enter publish_msg")

    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@192.168.17.46/",
        port=5671,
        loop=asyncio.get_event_loop(),
        ssl=True
    )

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)  # Recibir un mensaje a la vez
        exchange = await channel.declare_exchange("event_exchange", type=aio_pika.ExchangeType.TOPIC)

        try:
            await exchange.publish(
                aio_pika.Message(body=message.encode()),
                routing_key=routing_key,
            )
        except Exception as e:
            logger.debug(e)

    logger.debug(f" [x] Sent delivery.delivered:{message}")
