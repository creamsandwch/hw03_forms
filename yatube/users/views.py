from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, \
    PasswordResetConfirmView, PasswordResetCompleteView, PasswordResetDoneView


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChange(PasswordChangeView):
    success_url = reverse_lazy('users:password_change_done')


class PasswordReset(PasswordResetView):
    success_url = reverse_lazy('users:password_reset_done')
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class PasswordResetComplete(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'


class PasswordResetDone(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'
