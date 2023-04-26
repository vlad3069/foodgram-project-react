from djoser.views import TokenCreateView
from rest_framework import status, permissions

from users.models import (
    User,
    UserСonnection,
    Subscription,
)


class TokenCreateView(TokenCreateView):

    permission_classes = (permissions.AllowAny,)

    def _action(self, serializer):
        response = super()._action(serializer)
        if response.status_code == status.HTTP_200_OK:
            response.status_code = status.HTTP_201_CREATED
        return response

