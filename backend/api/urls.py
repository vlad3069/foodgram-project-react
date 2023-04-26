from django.urls import include, path
from djoser.views import UserViewSet, TokenDestroyView
from rest_framework.routers import DefaultRouter

from api.views import (
    TokenCreateView,
)

auth_urls_v1 = [
    path(r'token/login/', TokenCreateView.as_view(), name='login'),
    path(r'token/logout/', TokenDestroyView.as_view(), name='logout'),
]

users_urls_v1 = [
    path(r'', UserViewSet.as_view(
        {'get': 'list', 'post': 'create'}), name='users'),
    path(r'<int:id>/', UserViewSet.as_view({'get': 'retrieve'}),
         name='user-detail'),
    path(r'me/', UserViewSet.as_view({'get': 'me'}), name='me'),
    path(r'set_password/', UserViewSet.as_view({'post': 'set_password'}),
         name='set-password'),
]

router_v1 = DefaultRouter()

urlpatterns = [
    path(r'auth/', include(auth_urls_v1)),
    path(r'users/', include(users_urls_v1)),
    path(r'', include(router_v1.urls)),
]
