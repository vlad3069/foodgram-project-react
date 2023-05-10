from django.urls import include, path
from djoser.views import TokenDestroyView
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, ReciepeViewSet,
                       TagViewSet, UserViewSet, TokenCreateView)

auth_urls_v1 = [
    path(r'token/login/', TokenCreateView.as_view(), name='login'),
    path(r'token/logout/', TokenDestroyView.as_view(), name='logout'),
]


router_v1 = DefaultRouter()
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'recipes', ReciepeViewSet, basename='recipes')
router_v1.register(r'users', UserViewSet, 'users')

urlpatterns = [
    path(r'auth/', include(auth_urls_v1)),
    path(r'', include(router_v1.urls)),
]
