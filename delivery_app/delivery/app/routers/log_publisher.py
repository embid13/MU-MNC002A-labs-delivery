import aio_pika
import logging
import asyncio
import json
from datetime import datetime


logger = logging.getLogger(__name__)


async def publish_log_msg(body, log_level, cls):
    logger.debug("enter publish_msg")

    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@192.168.17.46/",
        port=5671,
        loop=asyncio.get_event_loop(),
        ssl=True
    )

    async with connection:
        message = {
            "body": str(body),
            "datetime": datetime.now().isoformat(),
            "cls": cls
        }

        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)  # Recibir un mensaje a la vez
        exchange = await channel.declare_exchange("logs_exchange", type=aio_pika.ExchangeType.TOPIC)

        try:
            await exchange.publish(
                aio_pika.Message(body=json.dumps(message).encode()),
                routing_key=f"auth.{log_level}",
            )
        except Exception as e:
            logger.debug(e)

    logger.debug(f" [x] Sent auth.{log_level}:{message}")