# -*- coding: utf-8 -*-
"""Classes for Request/Response schema definitions."""
# pylint: disable=too-few-public-methods
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

class deliveryBase(BaseModel):
    id: int = Field(
        description="Id de la delivery",
        example=1
    )
    location: str = Field(
        description="Ubicación de la delivery, para dónde es.",
        example="Mondragón"
    )
