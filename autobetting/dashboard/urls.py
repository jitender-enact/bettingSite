from django.urls import path, re_path
from dashboard import views

urlpatterns = [
    path('',
         views.DashboardView.as_view(),
         name="dashboard_page"),
]
