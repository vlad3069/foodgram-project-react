from rest_framework import serializers as rest_serialize
from djoser import serializers as djoser_serialize
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from recipes.models import Reciepe, IngredientInRecipe
from ingredients.models import Ingredient
from tags.models import Tag
from users.models import User, Subscription


class UserSerializer(djoser_serialize.UserSerializer):
    is_subscribed = rest_serialize.SerializerMethodField()

    def get_is_subscribed(self, author):
        request = self.context["request"]
        return (
            request.user.is_authenticated
            and author.subscriptions.filter(user=request.user).exists()
        )

    class Meta(djoser_serialize.UserSerializer.Meta):
        model = User
        fields = djoser_serialize.UserSerializer.Meta.fields + ("is_subscribed",)



# class SetPasswordSerializer(rest_serialize.Serializer):