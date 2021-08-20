from django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name="index"),
    path('logout/', views.index, name="logout"),
    path('message/', views.message, name="message"),
    path('mood_history/', views.mood_history, name="mood_history"),
    path('mood_boost/', views.mood_boosts, name="mood_boost")
]
