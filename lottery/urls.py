from django.urls import path
from .views import *

urlpatterns = [
    path('daily_draw/', daily_draw_view, name='daily_draw'),
    # other URL patterns
    path('stk-push-callback/', stk_push_callback, name='stk_push_callback'),
]