# -*- coding: utf-8 -*-
"""Main file to start FastAPI application."""
import logging
import os
import asyncio
from fastapi import FastAPI
from app.routers import main_router
from app.sql import models, database
from app.routers.delivery_consumer import AsyncConsumer
from app.routers.keys import RSAKeys

# Configure logging ################################################################################
logger = logging.getLogger(__name__)

# OpenAPI Documentation ############################################################################
APP_VERSION = os.getenv("APP_VERSION", "2.0.0")
logger.info("Running app version %s", APP_VERSION)
DESCRIPTION = """
Monolithic manufacturing order application - Delivery Microservice.
"""

tag_metadata = [

    {
        "name": "Delivery",
        "description": "Endpoints related to deliveries.",
    },

]

app = FastAPI(
    redoc_url=None,  # disable redoc documentation.
    title="FastAPI - Deliveries app",
    description=DESCRIPTION,
    version=APP_VERSION,
    servers=[
        {"url": "/", "description": "Development"}
    ],
    license_info={
        "name": "MIT License",
        "url": "https://choosealicense.com/licenses/mit/"
    },
    openapi_tags=tag_metadata,

)

app.include_router(main_router.router)

rabbitmq_consumer = AsyncConsumer('event_exchange', 'order.created',
                                  AsyncConsumer.on_delivery_received)

rabbitmq_consumer2 = AsyncConsumer('event_exchange', 'order.ready',
                                   AsyncConsumer.on_delivery_ready)

rabbitmq_consumer3 = AsyncConsumer('event_exchange', 'auth.publickey',
                                   AsyncConsumer.ask_public_key)

RSAKeys.get_public_key()


@app.on_event("startup")
async def startup_event():
    """Configuration to be executed when fastapi server starts."""
    logger.info("Creating database tables")
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    logger.info("Waiting for RabbitMQ")
    logger.debug("WAITING FOR RABBITMQ")
    consumer_tasks = [
        asyncio.create_task(rabbitmq_consumer.start_consuming()),
        asyncio.create_task(rabbitmq_consumer2.start_consuming())
    ]
    asyncio.gather(*consumer_tasks)


# Main #############################################################################################
# If application is run as script, execute uvicorn on port 8000
if __name__ == "__main__":
    import uvicorn

    logger.debug("App run as script")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config='logging.yml'
    )
    logger.debug("App finished as script")
