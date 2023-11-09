import os
import jwt
import logging
import requests
from datetime import datetime
from ..routers.delivery_router_utils import raise_and_log_error
from fastapi import status

logger = logging.getLogger(__name__)

public_key = None

class RSAKeys(object):
    
    @staticmethod
    def get_public_key():
        return public_key

    @staticmethod
    def set_public_key(new_public_key):
        global public_key
        public_key = new_public_key

    @staticmethod
    def get_id_from_token(token_jwt):
        try:
            # Decodificar el token JWT
            payload = jwt.decode(token_jwt, public_key, algorithms='RS256')

            # Comprobar si el campo "sub" está presente en el token
            if "sub" in payload:
                return payload["sub"]
            else:
                return None  # El campo "sub" no está presente en el token
        except Exception as e:
            return f"Error desconocido: {str(e)}"

    @staticmethod
    def verify_jwt_and_get_id_from_token(token):
        try:
            payload = jwt.decode(token, public_key, algorithms='RS256')
            if payload['exp'] < datetime.timestamp(datetime.utcnow()):
                raise_and_log_error(logger, status.HTTP_403_FORBIDDEN, "JWT Token expired")
            user_id = RSAKeys.get_id_from_token(token)
            if user_id is None:
                raise_and_log_error(logger, status.HTTP_401_UNAUTHORIZED, f"JWT verification failed: NO user_id.")
            else:
                return user_id
        except jwt.exceptions.ExpiredSignatureError as exc:
            raise_and_log_error(logger, status.HTTP_403_FORBIDDEN, f"JWT Token expired: {exc}")
        except jwt.exceptions.InvalidSignatureError as exc:
            raise_and_log_error(logger, status.HTTP_401_UNAUTHORIZED, f"JWT signature verification failed: {exc}")
        except Exception as e:
            raise_and_log_error(logger, status.HTTP_401_UNAUTHORIZED, f"JWT error: {e}")
