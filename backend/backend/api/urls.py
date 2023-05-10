from django.urls import include, path
from djoser.views import TokenDestroyView
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, ReciepeViewSet, TagViewSet,
                       TokenCreateView, UserViewSet)

auth_urls_v1 = [
    path(r'token/login/', TokenCreateView.as_view(), name='login'),
    path(r'token/logout/', TokenDestroyView.as_view(), name='logout'),
]

users_urls_v1 = [
    path(r'', UserViewSet.as_view({'get': 'list', 'post': 'create'}), 'users'),
    path(r'<int:id>/', UserViewSet.as_view(
        {'get': 'retrieve'}), 'user-detail'),
    path(r'me/', UserViewSet.as_view({'get': 'me'}), name='me-detail'),
    path(
        r'set_password/',
        UserViewSet.as_view({'post': 'set_password'}),
        name='set-password',
    ),
    path(
        r'subscriptions/',
        UserViewSet.as_view({"get": "list"}),
        name='subscriptions',
    ),
    path(
        r'<int:author_id>/subscribe/',
        UserViewSet.as_view({"post": "create", "delete": "destroy"}),
        name='subscribe',
    ),
]

router_v1 = DefaultRouter()
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'recipes', ReciepeViewSet, basename='recipes')


urlpatterns = [
    path(r'auth/', include(auth_urls_v1)),
    path(r'users/', include(users_urls_v1)),
    path(r'', include(router_v1.urls)),
]
