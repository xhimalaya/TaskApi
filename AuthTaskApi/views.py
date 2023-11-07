from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
User = get_user_model()
from django.conf import settings
from django.db.models import Q
from django.core.cache import cache
from django.views.decorators.cache import cache_page

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
import jwt
from django.utils import timezone

from .models import *
from .serializers import *
import json



# Create your views here.


class PingApiView(APIView):
    def get(self, *args, **kwargs):
        return Response({"data":"ping success !!!!"}, status=status.HTTP_200_OK)
    

class SigninView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.create(username=username, password=password, is_active=True).save()

        return Response({'success':'true'},status=status.HTTP_200_OK)
    

class LoginView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, format=None):
        try:
            username = request.data['username']
            user = User.objects.filter(username=username, is_active=True).first()
            if not user:
                return Response(
                    {
                        'success':'false',
                        'message': 'Invalid Username'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            user_id = user.id
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
            payload['exp'] += 30* 24 * 3600
            access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            return Response(
                {
                    'message': 'success',
                    'access_token': access_token
                    },
                status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success':'false','message': 'An error occurred during verify'}, status=status.HTTP_400_BAD_REQUEST)
    
def generate_cache_key(user_id, request_data):
    return f"data_operation_cache_{user_id}"

class BasicOperationView(APIView):
    permission_classes = (IsAuthenticated,)
    queryset = DataOperationModel.objects.all()
    serializer_class = DataOperationSerializer

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        cache_key = generate_cache_key(user_id, request.query_params)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data, status=status.HTTP_200_OK)
        data = list(self.queryset.filter(user=user_id).values())
        cache.set(cache_key, data, 300)
        return Response({"data": data}, status=status.HTTP_200_OK)

    def post(self, request):
        user_id = request.user.id
        data = request.data
        data["user"] = user_id
        serializer = DataOperationSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            cache_key = generate_cache_key(user_id, data)
            cache.delete(cache_key)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        user_id = request.user.id
        data_id = request.data["data_id"]
        dataObj = get_object_or_404(
            DataOperationModel,
            user=user_id,
            data_id=data_id,
            is_delete=False
        )
        dataObj.is_delete = True
        dataObj.save()
        return Response({"status":"deleted data", "user_id":user_id})
    

