from django.urls import path
from . import views

app_name = 'faceauth'

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_reference, name='upload'),
    path('verify/', views.verify_image, name='verify'),
]
