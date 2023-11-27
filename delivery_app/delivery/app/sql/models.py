# -*- coding: utf-8 -*-
"""Database models definitions. Table representations as class."""
from sqlalchemy import Column, DateTime, Integer, Boolean, String
from sqlalchemy.sql import func
from .database import Base


class BaseModel(Base):
    """Base database table representation to reuse."""
    __abstract__ = True
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    update_date = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        fields = ""
        for column in self.__table__.columns:
            if fields == "":
                fields = f"{column.name}='{getattr(self, column.name)}'"
                # fields = "{}='{}'".format(column.name, getattr(self, column.name))
            else:
                fields = f"{fields}, {column.name}='{getattr(self, column.name)}'"
                # fields = "{}, {}='{}'".format(fields, column.name, getattr(self, column.name))
        return f"<{self.__class__.__name__}({fields})>"
        # return "<{}({})>".format(self.__class__.__name__, fields)


class Delivery(BaseModel):
    __tablename__ = "delivery"
    delivery_id = Column(Integer, primary_key=True)
    status = Column(String, nullable=False)
    location = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False)
    postal_code = Column(Integer, nullable=False)


