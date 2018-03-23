from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import (AuthenticationForm, PasswordChangeForm, \
    PasswordResetForm, SetPasswordForm)
from django.contrib.messages.constants import DEFAULT_LEVELS
from users.core.utils import set_messages
from users.core.constants import MSG_FORGOT_PASSWORD_MAIL_SUCCESS,\
    MSG_USER_LOGIN_SUCCESS, MSG_USER_SIGNUP_SUCCESS


class WidgetAttributesMixin(object):
    """
    Mixin for updating the widget attributes of the model fields
    """

    def update_the_widget_attr(self, field, attributes_dict):
        self.fields[field].widget.attrs.update(attributes_dict)


class UserAuthenticationForm(WidgetAttributesMixin, AuthenticationForm):
    """
    Extend the Authentication Form. for
    """

    def __init__(self, request=None, *args, **kwargs):
        """
        Applied some css class and placeholders into the username and password
         fields of the AuthenticationForm form.
        """
        super(UserAuthenticationForm, self).__init__(request, *args, **kwargs)

        self.update_the_widget_attr('username', {
            'class': 'form-control',
            'placeholder': 'Username',
        })

        self.update_the_widget_attr('password', {
            'class': 'form-control',
            'placeholder': 'Password',
        })

    def is_valid(self):
        """
        set session messages
        """
        set_messages(request=self.request,
                     msg_text=MSG_USER_LOGIN_SUCCESS,
                     msg_level=DEFAULT_LEVELS['SUCCESS'])
        return super(UserAuthenticationForm, self).is_valid()


class UserPasswordChangeForm(WidgetAttributesMixin, PasswordChangeForm):
    """
    Extend the PasswordChangeForm form.
    """

    def __init__(self, user, *args, **kwargs):
        """
        Applied some css class and placeholders into the new_password1,
         new_password2 and password and old_password fields of the
         PasswordChangeForm form.
        """
        super(UserPasswordChangeForm, self).__init__(user, *args, **kwargs)

        self.update_the_widget_attr('new_password1', {
            'class': 'form-control',
            'placeholder': 'New Password',
        })

        self.update_the_widget_attr('new_password2', {
            'class': 'form-control',
            'placeholder': 'Confirm Password',
        })

        self.update_the_widget_attr('old_password', {
            'class': 'form-control',
            'placeholder': 'Old Password',
        })


class UserPasswordResetForm(WidgetAttributesMixin, PasswordResetForm):
    """
    Extend the PasswordResetForm form.
    """

    def __init__(self, *args, **kwargs):
        """
        Applied some css class and placeholders into the email fields of
        the PasswordResetForm form.
        """
        super(UserPasswordResetForm, self).__init__(*args, **kwargs)

        self.update_the_widget_attr('email', {
            'class': 'form-control',
            'placeholder': 'Email Address',
        })

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Set the session messages
        """
        set_messages(request=request,
                     msg_text=MSG_FORGOT_PASSWORD_MAIL_SUCCESS,
                     msg_level=DEFAULT_LEVELS['SUCCESS'])

        return super(UserPasswordResetForm, self).\
            save(domain_override, subject_template_name, email_template_name,
                 use_https, token_generator, from_email, request,
                 html_email_template_name)

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email,
                  html_email_template_name=None):
        """
        over-write the send_mail function of the  PasswordResetForm class.
        """
        return True


class UserSetPasswordForm(WidgetAttributesMixin, SetPasswordForm):
    """
    Extend the SetPasswordForm form.
    """

    def __init__(self, user, *args, **kwargs):
        """
        Applied some css class and placeholders into the email fields of
        the SetPasswordForm form.
        """
        super(UserSetPasswordForm, self).__init__(user, *args, **kwargs)

        self.update_the_widget_attr('new_password1', {
            'class': 'form-control',
            'placeholder': 'New Password',
        })

        self.update_the_widget_attr('new_password2', {
            'class': 'form-control',
            'placeholder': 'Confirm Password',
        })


class UserSignUpForm(forms.ModelForm):
    """
    ModelForm for user sign-up by filling up users following
    credentials (username, password and email).
    """
    password = forms. \
        CharField(label="Password",
                  required=True,
                  widget=forms.PasswordInput(
                      attrs={'class': 'form-control',
                             'placeholder': 'Password'}))

    class Meta:
        model = User
        fields = ("username", "email")
        widgets = {'username':
                       forms.TextInput(attrs={'class': 'form-control',
                                              'placeholder': 'Username'}),
                   'email':
                       forms.EmailInput(attrs={'class': 'form-control',
                                               'placeholder': 'Email'})}

    def save(self, request=None, commit=True):
        """
        Overwrite the Form save method.
        So that we set the encrypted password for user.
        Also set the session message.
        """
        user = super(UserSignUpForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            if request:
                set_messages(request=request,
                             msg_text=MSG_USER_SIGNUP_SUCCESS,
                             msg_level=DEFAULT_LEVELS['SUCCESS'])
        return user
