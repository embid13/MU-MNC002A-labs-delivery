# -*- coding: utf-8 -*-
"""Classes for Request/Response schema definitions."""
# pylint: disable=too-few-public-methods
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

class Message(BaseModel):
    """Message schema definition."""
    detail: Optional[str] = Field(example="error or success message")

class deliveryBase(BaseModel):
    delivery_id: int = Field(
        description="Identificador de la delivery",
        example=1
    )
    status: str = Field(
        description="Estado de la entrega.",
        example="Iniciado, Finalizado."
    )
    location: str = Field(
        description="Ubicación de la delivery de un order, indica a dónde hay que entregar el pedido.",
        example="Goiru Kalea, 2, 20500 Arrasate, Gipuzkoa"
    )
    user_id: int = Field(
        description="Usuario del delivery",
        example=1
    )
