from functools import wraps

import jwt
from channels.db import database_sync_to_async
from rest_framework.response import Response

from Tools.MakeToken import JWT_TOKEN_KEY
from User.models import User


def login_required(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return Response({'error': 'Token is missing'}, status=401)
        try:
            payload = jwt.decode(token, JWT_TOKEN_KEY, algorithms=['HS256'])
            uid = payload['uid']
            user = User.objects.get(pk=uid)
            request.user = user
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=401)
        return view_func(self, request, *args, **kwargs)
    return wrapper

@database_sync_to_async
def get_user(uid):
    return User.objects.get(uid=uid)
