from django.urls import path
from .views import *

urlpatterns = [
    path('daily_draw/', daily_draw_view, name='daily_draw'),
    # other URL patterns
    Patth('daraja/stk_push', views.stk_push_callback,name='stk_push_callback'),
]