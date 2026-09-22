from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import requests

class ServiceUser:
    is_authenticated = True

    def __init__(self, user_id, group):
        self.user_id = user_id
        self.group = group

class RemoteJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        try:
            scheme, token = auth_header.split()
            if scheme.lower() != 'bearer':
                raise AuthenticationFailed("Invalid authentication scheme")
        except ValueError:
            raise AuthenticationFailed("Invalid authentication header")

        try:
            response = requests.post(
                "http://127.0.0.1:8000/auth/verify/",
                json={"token":token}
            )
        except requests.exceptions.RequestException:
            raise AuthenticationFailed("Auth service unavailable")

        if response.status_code != 200:
            raise AuthenticationFailed("Invalid or expired token")

        data = response.json()
        service_user = ServiceUser(user_id=data["user_id"], group=data["group"])

        return (service_user, token)
