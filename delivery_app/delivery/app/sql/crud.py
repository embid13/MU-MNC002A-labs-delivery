# -*- coding: utf-8 -*-
"""Functions that interact with the database."""
import logging
import jwt
import requests
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from . import models
from . import schemas
from sqlalchemy.future import select
from ..routers.delivery_router_utils import raise_and_log_error
from fastapi import status


logger = logging.getLogger(__name__)


#TODO
def validate_jwt_token(token):
    public_key = requests.get('https://{os.environ["RABBITMQ_IP"]}/public-key')  # La misma clave pública que se utiliza para firmar el token
    try:
        payload = jwt.decode(token, public_key, algorithms=['RS256'])
        return payload
    except jwt.ExpiredSignatureError as exc:
        # Token caducado
        raise_and_log_error(logger, status.HTTP_401_UNAUTHORIZED, f"Error {exc}")
        return None
    except jwt.InvalidTokenError as exc:
        # Token inválido
        raise_and_log_error(logger, status.HTTP_403_FORBIDDEN, f"Error {exc}")
        return None


async def deliver_delivery_by_id(db: AsyncSession, delivery_id):
    """Deliver a delivery by id"""
    if delivery_id is None:
        return None


async def get_delivery_by_id(db: AsyncSession, delivery_id):
    """Retrieve any delivery by id."""
    if delivery_id is None:
        return None

    delivery = await db.get(models.Delivery, delivery_id)
    return delivery


async def add_new_delivery(db: AsyncSession, delivery):
    """Adds a new delivery to the database"""
    delivery_base = models.Delivery(
        delivery_id=delivery.user_id,
        status=delivery.status,
        location=delivery.location
    )
    db.add(delivery_base)
    await db.commit()
    await db.refresh(delivery_base)
    logger.debug("New delivery created")
    return delivery_base


async def update_delivery(db: AsyncSession, delivery):
    db_delivery = get_delivery_by_id(db, delivery.delivery_id)
    """If there is no delivery created with that id"""
    if db_delivery is None:
        await add_new_delivery(db, delivery)
        logger.debug("delivery created")
    else:
        """If already exists a delivery with that ID, update it"""
        db_delivery.status = delivery.status
        db_delivery.delivery_id = delivery.delivery_id
        db_delivery.location = delivery.location
        await db.commit()
        await db.refresh(db_delivery)
        logger.debug("delivery updated")
        delivery_base = schemas.deliveryBase(
            delivery_id=db_delivery.delivery_id,
            status=db_delivery.status,
            location=db_delivery.location
        )
        return delivery_base


async def get_list(db: AsyncSession, model):
    """Retrieve a list of elements from database"""
    result = await db.execute(select(model))
    item_list = result.unique().scalars().all()
    return item_list


async def get_delivery_list(db: AsyncSession):
    """Load all the orders from the database."""
    return await get_list(db, models.Delivery)

