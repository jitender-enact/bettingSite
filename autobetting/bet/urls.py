from django.urls import path, re_path
from bet import views

urlpatterns = [
    path('',
         views.CreateBetView.as_view(),
         name="create_bet_page"),
    path('my-bets/',
         views.ListBetView.as_view(),
         name="list_bet_page"),
    path('bet-status/<int:bet_id>/',
         views.ListBetStatusView.as_view(),
         name="list_bet_status_page"),
    path('site-credentials/',
         views.CreateUserCredentialsView.as_view(),
         name="create_credentials_page"),
    path('site-credential-list/',
         views.ListUserCredentialsView.as_view(),
         name="list_credentials_page"),
    path('create-preference/',
         views.CreateUserPreferenceView.as_view(),
         name="create_preference_page"),
]
