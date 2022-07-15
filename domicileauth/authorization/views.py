from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser, Profile
from .serializers import RegistrationSerializer, LoginSerializer, CustomUserSerializer, ProfileSerializer
from .renderers import CustomUserJSONRenderer
from .token_generators import generate_rt, generate_jwt


# Create your views here.


class RefreshView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            user = CustomUser.objects.get(refresh_token=refresh_token)
        except CustomUser.DoesNotExist:
            return Response({
                'error': 'User does not exist'
            }, status=status.HTTP_418_IM_A_TEAPOT)
        user.refresh_token = generate_rt()
        user.save(update_fields=('refresh_token',))
        data = {
                'access_token': generate_jwt(user.pk),
                'refresh_token': user.refresh_token
        }
        return Response(data, status=status.HTTP_200_OK)


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer
    renderer_classes = (CustomUserJSONRenderer,)

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    renderer_classes = (CustomUserJSONRenderer,)

    def post(self, request):
        user = request.data

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomUserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (CustomUserJSONRenderer,)
    serializer_class = CustomUserSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = self.serializer_class(profile)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        profile = Profile.objects.get(user=request.user)
        data = request.data
        if data['avatar']:
            profile.avatar = data['avatar']
        if data['phone']:
            profile.phone = data['phone']
        if data['fio']:
            profile.fio = data['fio']
        profile.save()
        return Response(status=status.HTTP_200_OK)


class CreateProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    def post(self, request):
        data = request.data
        Profile.objects.get_or_create(
            user=request.user,
            avatar=data["avatar"],
            phone=data["phone"],
            fio=data["fio"]
        )
        return Response(status=status.HTTP_201_CREATED)
