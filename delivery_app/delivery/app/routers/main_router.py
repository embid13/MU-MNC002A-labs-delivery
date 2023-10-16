"""FastAPI router definitions."""
import logging
import requests
from fastapi import APIRouter, Depends, status
from app.sql import crud, schemas
from .delivery_router_utils import raise_and_log_error
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.dependencies import get_db


logger = logging.getLogger(__name__)
router = APIRouter()


#TODO
@router.get(
    "/delivery/{delivery_id}",
    summary="Deliver the delivery with delivery_id",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.deliveryBase,
            "description": "Requested Delivery."
        },
        status.HTTP_404_NOT_FOUND: {
            "model": schemas.Message, "description": "Delivery not found"
        }
    },
    tags=['Delivery']
)
async def deliver_single_delivery(
        delivery_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Retrieve single order by id"""
    logger.debug("GET '/delivery/%i' endpoint called.", delivery_id)
    try:
        delivery = await crud.deliver_delivery_by_id(db, delivery_id)
        if not delivery:
            raise_and_log_error(logger, status.HTTP_404_NOT_FOUND, f"Delivery {delivery_id} not found")
        return delivery
    except Exception as exc:
        raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error getting the delivery: {exc}")


#TODO
#Respecto al user_id, recibir TUS deliveries.
@router.get(
    "/delivery",
    summary="Retrieve all YOUR deliveries by id",
    response_model=List[schemas.deliveryBase],
    tags=['Delivery', 'List']
)
async def view_deliveries(db: AsyncSession = Depends(get_db)):
    logger.debug("GET '/delivery' endpoint called.")
    try:
        delivery_list = await crud.get_delivery_list(db)
        return delivery_list
    except Exception as exc:
        raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error getting the deliveries: {exc}")
