from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from users.serializers import UserSerializer


@extend_schema(
    summary="Register a new user",
    description="Allows unauthenticated users to register a new account.",
    request=UserSerializer,
    responses={201: UserSerializer},
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


@extend_schema(
    summary="Get or update your profile",
    description="Allows authenticated users to view or update their own profile.",
    responses={200: UserSerializer},
    request=UserSerializer,
)
class UpdateUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
