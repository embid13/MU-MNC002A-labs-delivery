# -*- coding: utf-8 -*-
"""Functions that interact with the database."""
import logging
import json
from sqlalchemy.ext.asyncio import AsyncSession
from . import models
from sqlalchemy.future import select
from ..routers.delivery_router_utils import raise_and_log_error
from fastapi import status
from app.routers.delivery_publisher import publish_msg

logger = logging.getLogger(__name__)


async def deliver_delivery_by_id(db: AsyncSession, delivery_id, user_id):
    """Deliver a delivery by id"""
    content = {}
    db_delivery = await get_delivery_by_id(db, delivery_id, user_id)
    """If there is no delivery created with that id"""
    if db_delivery is None:
        logger.debug("delivery does not exist.")
    elif db_delivery.status == "READY":
        # If already exists a delivery with that ID, update it
        db_delivery.status = "DELIVERED"
        await db.commit()
        await db.refresh(db_delivery)
        # Publish the new status
        content['delivery_id'] = delivery_id
        content['status'] = "DELIVERED"
        # Convert the content to JSON
        json_content = json.dumps(content)
        await publish_msg('delivery.delivered', json_content)
        logger.debug("delivery delivered")
    else:
        logger.debug("delivery is not ready!")
        return "delivery not ready yet"
    return db_delivery


async def get_delivery_by_id(db: AsyncSession, delivery_id, user_id):
    """Retrieve a delivery by id if the user has permission."""
    if delivery_id is None or user_id is None:
        return None
    delivery = await db.get(models.Delivery, delivery_id)
    if delivery is not None:
        # Verificar si el user_id coincide con el user_id asociado al delivery
        if delivery.user_id == user_id:
            return delivery
        else:
            # El user_id no tiene permiso para acceder a esta entrega
            raise_and_log_error(logger, status.HTTP_403_FORBIDDEN, f"El user_id no tiene permiso para acceder a"
                                                                   f" esta entrega")
    else:
        # La entrega no se encontró en la base de datos
        raise_and_log_error(logger, status.HTTP_403_FORBIDDEN, f"La entrega no se encontró en la base de datos")


async def add_new_delivery(db: AsyncSession, delivery):
    """Adds a new delivery to the database"""
    delivery_base = models.Delivery(
        delivery_id=delivery.delivery_id,
        status=delivery.status,
        location=delivery.location,
        user_id=delivery.user_id
    )
    db.add(delivery_base)
    await db.commit()
    await db.refresh(delivery_base)
    logger.debug("New delivery created")
    return delivery_base

"""
async def get_list(db: AsyncSession, model):
    # Retrieve a list of elements from database.
    result = await db.execute(select(model))
    item_list = result.unique().scalars().all()
    return item_list
"""


async def get_delivery_list(db: AsyncSession, user_id):
    """Load all the orders from the database for a specific user."""
    try:
        # Filtra las entregas por el user_id
        result = await db.execute(select(models.Delivery).filter(models.Delivery.user_id == user_id))
        item_list = result.unique().scalars().all()
        if not item_list:
            raise_and_log_error(logger, status.HTTP_403_FORBIDDEN, f"No tienes ninguna delivery pendiente.")
        else:
            return item_list
    except Exception as e:
        # Puedes manejar la excepción de la forma que consideres adecuada
        raise_and_log_error(logger, status.HTTP_403_FORBIDDEN, f"Error al conseguir la lista de deliveries.")
        return []  # In case of error, return an empty list


async def get_delivery_by_id_without_checking(db: AsyncSession, delivery_id):
    # Retrieve a delivery by id without checking the user permissions.
    delivery = await db.get(models.Delivery, delivery_id)
    return delivery


async def update_delivery(db: AsyncSession, delivery):
    db_delivery = await get_delivery_by_id_without_checking(db, delivery.delivery_id)
    # If there is no delivery created with that id
    if db_delivery is None:
        logger.debug("There is no delivery with that id.")
    else:
        db_delivery.status = delivery.status
        await db.commit()
        await db.refresh(db_delivery)
        logger.debug("delivery updated")
