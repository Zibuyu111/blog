from django.urls import path

from . import views


app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("api/daily-scores/", views.daily_scores, name="daily_scores"),
    path("api/daily-scores/records/", views.daily_score_records, name="daily_score_records"),
]
