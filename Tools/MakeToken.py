import jwt
import time

JWT_TOKEN_KEY = "123456"


def make_token(uid, expire=3600 * 24):
    key = JWT_TOKEN_KEY
    now_t = time.time()
    payload_data = {'uid': uid, 'exp': now_t + expire}
    token = jwt.encode(payload_data, key, algorithm='HS256')
    return token
