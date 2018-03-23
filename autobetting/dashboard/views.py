# from django.shortcuts import render
from django.views import generic
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

# Create your views here.


class DashboardView(generic.TemplateView):
    """
    View handle and show the dash-board
    """
    template_name = "dashboard/index.html"

    @method_decorator(login_required(login_url=reverse_lazy('users:login')))
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)
