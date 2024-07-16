import requests

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import JsonResponse

from rest_framework_simplejwt.tokens import (
    RefreshToken,
    AccessToken
)
from rest_framework_simplejwt.exceptions import (
    TokenError,
    InvalidToken
)


class RefreshTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
                access_token = AccessToken(token)
                access_token.verify()  # Verify the token
            except (TokenError, InvalidToken):
                refresh_token = request.COOKIES.get('refresh')
                if refresh_token:
                    try:
                        refresh = RefreshToken(refresh_token)
                        new_access_token = refresh.access_token
                        request.META['HTTP_AUTHORIZATION'] = f'Bearer {new_access_token}'
                    except TokenError:
                        return JsonResponse({'detail': 'Refresh token expired or invalid'}, status=401)
        return None
