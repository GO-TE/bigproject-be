import jwt
from bigproject.settings import SECRET_KEY

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from bigproject.settings import keys

GOOGLE_CLIENT_ID = keys['google-client-id']
GOOGLE_CLIENT_PASSWORD = keys['google-client-password']


def decode_jwt(token):
    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    return payload.get('user_id')


def validate_google_token(token):
    try:
        id_info = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
        if 'email' in id_info:
            return id_info
    except ValueError:
        return None
