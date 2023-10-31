import logging
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.sql import crud, schemas
from .delivery_router_utils import raise_and_log_error
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.dependencies import get_db
from app.routers.keys import RSAKeys


logger = logging.getLogger(__name__)
router = APIRouter()


@router.put(
    "/delivery/deliver/{delivery_id}",
    summary="Deliver the delivery with delivery_id only if you have permission.",
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
        request: Request,
        delivery_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Retrieve single order by id"""
    logger.debug("PUT '/delivery/deliver/%i' endpoint called.", delivery_id)
    try:
        token = get_jwt_from_request(request)
        keys = RSAKeys()
        user_id = keys.verify_jwt_and_get_id_from_token(token)
        logger.info("tokens verified")
        delivery = await crud.deliver_delivery_by_id(db, delivery_id, user_id)
        logger.info("delivery updated")
        if not delivery:
            raise_and_log_error(logger, status.HTTP_404_NOT_FOUND, f"Delivery {delivery_id} not found")
        if delivery.status == "DELIVERED":
            delivery_as_dict = {
                "delivery_id": delivery.delivery_id,
                "status": delivery.status,
                "location": delivery.location,
                "user_id": delivery.user_id
            }
            return JSONResponse(delivery_as_dict)
        else:
            print("Delivery not ready yet.")

    except Exception as exc:
        raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error getting the delivery: {exc}")


@router.get(
    "/delivery/deliveries",
    summary="Retrieve all YOUR deliveries by id",
    response_model=List[schemas.deliveryBase],
    tags=['Delivery', 'List']
)
async def view_deliveries(request: Request, db: AsyncSession = Depends(get_db)):
    logger.debug("GET '/delivery' endpoint called.")
    try:
        token = get_jwt_from_request(request)
        keys = RSAKeys()
        user_id = keys.verify_jwt_and_get_id_from_token(token)
        delivery_list = await crud.get_delivery_list(db, user_id)
        deliveries_as_dict = [
            {
                "delivery_id": item.delivery_id,
                "status": item.status,
                "location": item.location,
                "user_id": item.user_id
            }
            for item in delivery_list
        ]
        return JSONResponse(deliveries_as_dict)
    except Exception as exc:
        raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error getting the deliveries: {exc}")


@router.get(
    "/delivery/prueba",
)
async def prueba():
    logger.debug("GET '/prueba' endpoint called.")
    return "OLE"


def get_jwt_from_request(request):
    auth = request.headers.get('Authorization')
    if auth is None:
        raise_and_log_error(logger, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "NO JWT PROVIDED")
    jwt_token = auth.split(" ")[1]
    return jwt_token
