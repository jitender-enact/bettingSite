"""
Some Common function.
"""
from django.contrib.auth.models import User
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.utils.crypto import get_random_string
from django.contrib import messages


def get_user_obj_through_email(email):
    """
    Return the user object.
    """
    user_obj = User.objects.filter(email__iexact=email)
    if user_obj:
        return user_obj[0]
    return False


def set_messages(request=None, msg_text=None, msg_level=None, **kwargs):
    """
    Set the session messages.
    If the message is set then it return `True`, otherwise return `False`
    """
    if request and msg_text and msg_level:
        messages.add_message(request=request,
                             level=msg_level,
                             message=msg_text)
        return True
    return False


#
# def send_mail(subject_template_name, email_template_name,
#               context, from_email, to_email, html_email_template_name=None):
#     """
#     Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
#     """
#     subject = loader.render_to_string(subject_template_name, context)
#     # Email subject *must not* contain newlines
#     subject = ''.join(subject.splitlines())
#     body = loader.render_to_string(email_template_name, context)
#
#     email_message = EmailMultiAlternatives(subject, body,
#                                            from_email, [to_email])
#     if html_email_template_name is not None:
#         html_email = loader.render_to_string(html_email_template_name,
#                                              context)
#         email_message.attach_alternative(html_email, 'text/html')
#
#     email_message.send()
#
#
# def send_mail_to_user(user_obj, subject, message, from_email=None, **kwargs):
#     """
#     Send the email of the user object
#     """
#     user_obj.email_user(subject, message, from_email, **kwargs)
#     return True
#
#
# def generate_token(length=30, allowed_chars='abcdefghijklmnopqrstuvwxyz'
#                                             'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
#                                             '0123456789'):
#     """
#     Generate the token
#     """
#     return get_random_string(length=length, allowed_chars=allowed_chars)
#
#
