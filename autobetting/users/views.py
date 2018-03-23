"""
View handle the all the requests
"""
from django.contrib.auth import views as auth_views, login
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.http import is_safe_url
from django.shortcuts import resolve_url
from django.conf import settings
from django.contrib.messages.constants import DEFAULT_LEVELS
from django.views import generic
from users.forms import UserAuthenticationForm, UserPasswordResetForm, \
    UserPasswordChangeForm, UserSetPasswordForm, UserSignUpForm
from users.core.utils import set_messages
from users.core.constants import MSG_USER_LOGOUT_SUCCESS


@login_required(login_url=reverse_lazy('users:login'))
def change_password(request):
    """
    Call the django's `password_change` methods.


    This method is used for Changing the password of login users.
        If the password is successfully changes then user redirect to
        `redirect_url`.
    """
    redirect_url = reverse_lazy('users:password_change')  # redirect url
    form_class = UserPasswordChangeForm  # form class
    template_name = 'users/change-password.html'

    return auth_views.password_change(request=request,
                                      template_name=template_name,
                                      post_change_redirect=redirect_url,
                                      password_change_form=form_class)


def forgot_password(request):
    """
    Call the django's `password_reset` method.

    Used for generating the forgot password link and sending it through
    mail to user.

    It use:-
        reset-password.html file for email template.
        forgot-password-subject.txt file for email subject.

    After sending the email the user redirect to 'redirect_url'
    """
    redirect_url = reverse_lazy('users:forgot_password')
    template_name = 'users/forgot-password.html'
    email_template = 'users/email_templates/reset-password.html'
    subject_template = 'users/email_templates/forgot-password-subject.txt'
    form_class = UserPasswordResetForm
    from_email = settings.USER_EMAIL

    return auth_views.password_reset(request=request,
                                     template_name=template_name,
                                     email_template_name=email_template,
                                     subject_template_name=subject_template,
                                     password_reset_form=form_class,
                                     post_reset_redirect=redirect_url,
                                     from_email=from_email)


def password_reset(request, uidb64=None, token=None):
    """
    Call the django's password_reset_confirm method.

    Used for resetting the user password  if user forgot his/her password.
    For this it check the token is valid or not. (The token is send to user
    through email.)

    If token is valid then user can successfully reset his/her password.
    """

    template_name = 'users/password-reset-confirm.html'
    form_class = UserSetPasswordForm
    redirect_url = reverse_lazy('users:password_reset')
    content = {'uidb64': uidb64, 'token': token}

    return auth_views.password_reset_confirm(request=request,
                                             token=token,
                                             uidb64=uidb64,
                                             template_name=template_name,
                                             set_password_form=form_class,
                                             post_reset_redirect=redirect_url,
                                             extra_context=content)


class LoginView(generic.FormView):
    """
    This Form view handle the login functionality of the user login.

    *****Login functionality*****

        User can login through their credentials (username and password).

          -> If the credentials are wrong then its show the errors
          -> If the credentials are right but user account is not activate
            then its show the errors.
          -> If All credentials are right and user account is activated
            then user can successfully login and go to the home page.

            (when the user get successfully login then user`s session
            is created, that can be expired in two weeks.
            Through this session user doesn't need to full-up his/her
            login credentials every time.)
    """
    template_name = "users/login.html"
    redirect_to = reverse_lazy('dashboard:dashboard_page')
    form_class = UserAuthenticationForm

    def form_valid(self, form):
        """
        If the form is valid. Then applied the login functionality.
        Also set the session message.
        """
        login(request=self.request, user=form.get_user())
        return self.redirect_the_user()

    def redirect_the_user(self):
        """
        Redirect to home page
        """
        redirect_to = self.redirect_to

        # check is url safe?
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

        # redirect the user in redirect_to url
        return HttpResponseRedirect(redirect_to)

    def get(self, request, *args, **kwargs):
        """
        Handle the Get request.
        Check the user is already login or not.
            > if user is already login then it redirect the user
             to dashboard page, other-wise show the login page
        """
        if request.user.is_authenticated:
            return self.redirect_the_user()

        return super(LoginView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handle the Post request.
        Check the post data and Validate the form.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class=form_class)
        if form.is_valid():
            return self.form_valid(form=form)
        else:
            return self.form_invalid(form=form)

    def _set_session(self):
        """
        This method is used to setting-up the sessions
        """
        pass


class LogoutView(generic.View):
    """
    That view handle the logout functionality.
    """
    login_url = reverse_lazy('users:login')

    @method_decorator(login_required(login_url=login_url))
    def get(self, request):
        """
        logout the user and redirect the user to login page.
        """
        self.before_logout_call_method()
        return auth_views.logout_then_login(request, login_url=self.login_url)

    def before_logout_call_method(self):
        """
        Set the session messages.
        """
        set_messages(request=self.request,
                     msg_text=MSG_USER_LOGOUT_SUCCESS,
                     msg_level=DEFAULT_LEVELS['SUCCESS'])


class SignUpView(generic.FormView):
    """
    That view is used for user sign-up
    """
    form_class = UserSignUpForm
    template_name = 'users/sign-up.html'
    success_url = reverse_lazy('users:sign_up')

    def get(self, request, *args, **kwargs):
        """
        If user already login then send him to dashboard page.
        """
        if request.user.is_authenticated:
            return \
                HttpResponseRedirect(reverse_lazy("dashboard:dashboard_page"))

        return super(SignUpView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        """
        If the form is valid then we save the form.
        Also set the session messages
        """
        form.save(request=self.request)

        return super(SignUpView, self).form_valid(form=form)
