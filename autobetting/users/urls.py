from django.urls import path, re_path
from django.views.generic import RedirectView
from users import views

urlpatterns = [
    path('login/',
         views.LoginView.as_view(),
         name="login"),

    path('password-change/',
         views.change_password,
         name='password_change'),

    path('forgot-password/',
         views.forgot_password,
         name='forgot_password'),

    re_path('reset-password/(?P<uidb64>[0-9A-Za-z_\-]+)'
            '/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            views.password_reset,
            name='password_reset'),

    path('logout/',
         views.LogoutView.as_view(),
         name='logout'),

    path(r'sign-up/',
         views.SignUpView.as_view(),
         name='sign_up'),

    re_path('^.*$',
            RedirectView.as_view(pattern_name='users:login', permanent=False),
            name='index')
]
