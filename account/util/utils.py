import jwt
from bigproject.settings import SECRET_KEY


def decode_jwt(token):
    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    return payload.get('user_id')
