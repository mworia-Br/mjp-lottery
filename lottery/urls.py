from django.urls import path, include
#from .views import *
from . import views

urlpatterns = [
    path('daily_draw/', views.daily_draw_view, name='daily_draw'),
    # other URL patterns
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
    path('api-auth/', include('rest_framework.urls')),
]