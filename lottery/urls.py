from django.urls import path

urlpatterns = [
    path('daily_draw/', daily_draw_view, name='daily_draw'),
    # other URL patterns
]