from django.urls import path
from .views import *
urlpatterns = [
    path('ping/', PingApiView.as_view(), name='ping'),
    path('register/', SigninView.as_view(), name='ping'),
    path("authorize/", LoginView.as_view(), name="authorize"),
    path("dataoperation/", BasicOperationView.as_view(), name="dataoperation"),

]