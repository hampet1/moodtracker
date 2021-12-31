from django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name="index"),
    path('logout/', views.index, name="logout"),
    path('message/', views.message, name="message"),
    path('mood_history/', views.mood_history, name="mood_history"),
    path('mood_boost/', views.mood_boosts, name="mood_boost"),
    path('med/', views.medication_update, name="med"),
    path('med_del/', views.medication_delete, name="med_del"),
    path('mood_history_result/', views.mood_history_result, name="mood_history_result"),
    path('download_pdf/', views.download_pdf, name="download_pdf"),
    path('guideline/', views.guideline, name="guideline"),
]
