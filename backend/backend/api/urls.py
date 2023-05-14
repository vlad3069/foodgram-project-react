from django.urls import include, path
from djoser.views import TokenDestroyView
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, ReciepeViewSet,
                       RecipesSubscriptionViewSet, TagViewSet, TokenCreateView,
                       UserViewSet)

auth_urls_v1 = [
    path(r'token/login/', TokenCreateView.as_view(), name='login'),
    path(r'token/logout/', TokenDestroyView.as_view(), name='logout'),
]

users_urls_v1 = [
    path(r'', UserViewSet.as_view(
        {'get': 'list', 'post': 'create'}), name='users'),
    path(r'<int:id>/', DjoserUserViewSet.as_view(
        {'get': 'retrieve'}), name='user-detail'),
    path(r'me/', DjoserUserViewSet.as_view({'get': 'me'}), name='me-detail'),
    path(
        r'set_password/',
        UserViewSet.as_view({'post': 'set_password'}),
        name='set-password',
    ),
    path(
        r'subscriptions/',
        RecipesSubscriptionViewSet.as_view({'get': 'list'}),
        name='subscription',
    ),
    path(
        r'<int:author_id>/subscribe/',
        RecipesSubscriptionViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}),
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
