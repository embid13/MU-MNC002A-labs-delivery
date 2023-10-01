"""FastAPI router definitions."""
import logging
from fastapi import APIRouter, Depends, status
from app.sql import crud, schemas
from .delivery_router_utils import raise_and_log_error
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy.orm import Session
from app.dependencies import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/delivery/{delivery_id}",
    summary="Retrieve single delivery by id",
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
async def get_single_delivery(
        delivery_id: int,
        db: Session = Depends(get_db)
):
    """Retrieve single order by id"""
    logger.debug("GET '/delivery/%i' endpoint called.", delivery_id)
    delivery = await crud.get_delivery_by_id(db, delivery_id)
    if not delivery:
        raise_and_log_error(logger, status.HTTP_404_NOT_FOUND, f"Delivery {delivery_id} not found")
    return delivery


@router.get(
    "/delivery",
    summary="Retrieve all deliveries by id",
    response_model=List[schemas.deliveryBase],
    tags=['Delivery', 'List']
)
async def view_deliveries(db: AsyncSession = Depends(get_db)):
    logger.debug("GET '/delivery' endpoint called.")
    delivery_list = await crud.get_delivery_list(db)
    return delivery_list

