import os
import jwt
import logging
import requests
from datetime import datetime
from ..routers.delivery_router_utils import raise_and_log_error
from fastapi import status

logger = logging.getLogger(__name__)


class RSAKeys(object):
    public_key = None

    @staticmethod
    def get_public_key():
        logger.debug("GETTING PUBLIC KEY")
        endpoint = 'http://192.168.17.11/auth/public-key'
        try:
            response = requests.get(endpoint)
            if response.status_code == 200:
                x = response.json()["public_key"]
                RSAKeys.public_key = x
            else:
                print(f"Error al obtener la clave pública. Código de respuesta: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error de solicitud: {e}")

    @staticmethod
    def get_id_from_token(token_jwt):
        try:
            # Decodificar el token JWT
            payload = jwt.decode(token_jwt, RSAKeys.public_key, algorithms='RS256')

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
            payload = jwt.decode(token, RSAKeys.public_key, algorithms='RS256')
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
