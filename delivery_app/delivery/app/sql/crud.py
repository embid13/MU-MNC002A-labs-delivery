# -*- coding: utf-8 -*-
"""Functions that interact with the database."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from . import models
from . import schemas
from sqlalchemy.orm import Session
from sqlalchemy.future import select

logger = logging.getLogger(__name__)


async def get_delivery_by_id(db: Session, delivery_id):
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
        """If already exists a delivery with that ID, update STATUS"""
        db_delivery.status = delivery.status
        await db.commit()
        await db.refresh(db_delivery)
        logger.debug("delivery updated")
        delivery_base = schemas.deliveryBase(
            delivery_id=db_delivery.delivery_id,
            status=db_delivery.status,
            location=db_delivery.location
        )
    return delivery_base


async def get_delivery_list(db: AsyncSession):
    """Load all the orders from the database."""
    return await get_list(db, models.Delivery)


async def get_list(db: AsyncSession, model):
    """Retrieve a list of elements from database"""
    result = await db.execute(select(model))
    item_list = result.unique().scalars().all()
    return item_list
