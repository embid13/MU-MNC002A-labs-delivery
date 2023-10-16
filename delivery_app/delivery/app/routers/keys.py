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
        endpoint = 'https://{os.environ["AUTH_IP"]}/public-key'
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
            payload = jwt.decode(token_jwt, RSAKeys.public_key, algorithms=os.environ["JWT_ALGORITHM"])

            # Comprobar si el campo "user_id" está presente en el token
            if "user_id" in payload:
                return payload["user_id"]
            else:
                return None  # El campo "user_id" no está presente en el token
        except jwt.ExpiredSignatureError:
            return "Token expirado"
        except jwt.InvalidTokenError:
            return "Token no válido"
        except Exception as e:
            return f"Error desconocido: {str(e)}"

    @staticmethod
    def verify_jwt(token):
        try:
            payload = jwt.decode(token, RSAKeys.public_key, algorithms=os.environ["JWT_ALGORITHM"])
            if payload['exp'] < datetime.timestamp(datetime.utcnow()):
                raise_and_log_error(logger, status.HTTP_403_FORBIDDEN, "JWT Token expired")
        except jwt.exceptions.ExpiredSignatureError as exc:
            raise_and_log_error(logger, status.HTTP_403_FORBIDDEN, f"JWT Token expired: {exc}")
        except jwt.exceptions.InvalidSignatureError as exc:
            raise_and_log_error(logger, status.HTTP_401_UNAUTHORIZED, f"JWT signature verification failed: {exc}")
        except Exception as e:
            raise_and_log_error(logger, status.HTTP_401_UNAUTHORIZED, f"JWT error: {e}")
