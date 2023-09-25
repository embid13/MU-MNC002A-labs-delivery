"""FastAPI router definitions."""
import logging
from fastapi import APIRouter, Depends, status
from app.sql import crud, schemas
from .router_utils import raise_and_log_error

# TODO
"""Un delivery por cada order"""
"""Delivery espera a recibir delivery info:
    - ubicación a dónde enviar el delivery.
    - id del order
    - estado del order"""
"""Ubicación del delivery se envía con un json (GET) """
"""En el main se genera la base de datos, en el models las tablas, en crud toda la MUGRE (funciones)."""
"""Respond """


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/delivery/{delivery_id}",
    summary="Retrieve single delivery by id",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Delivery,
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
        db: AsyncSession = Depends(get_db)
):
    """Retrieve single order by id"""
    logger.debug("GET '/delivery/%i' endpoint called.", delivery_id)
    delivery = await crud.get_delivery(db, delivery_id)
    if not delivery:
        raise_and_log_error(logger, status.HTTP_404_NOT_FOUND, f"Delivery {delivery_id} not found")
    return delivery