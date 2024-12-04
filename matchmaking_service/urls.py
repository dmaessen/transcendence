from django.urls import path

from . import views
from .views import join_queue, record_match_result

urlpatterns = [
    path("", views.index, name="index"),
    path('api/join/', join_queue, name='join_queue'),
    path('api/record_result/', record_match_result, name='record_match_result'),
]