from django.shortcuts import render, HttpResponseRedirect
from django.views import generic
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from users.core import constants as MSG
from bet.forms import UserBetForm
from bet.models import UserBets, BetErrors
# Create your views here.


class ListBetView(generic.ListView):
    template_name = "bet/bet-list.html"

    def get_queryset(self):
        """
        Overwrite the get_queryset method.

        this method return the all `UserBets` of currently logged in user.
        also apply the sorting on the basis of given `sort` field
        :return UserBets queryset:
        """
        sort_field = self.request.GET.get('sort', None)
        order_field = '-id'

        if sort_field:
            if sort_field.replace("-", "") in [f.name for f in UserBets._meta.get_fields()]:
                order_field = sort_field
        return UserBets.objects.filter(user__id=self.request.user.id).order_by(order_field)


class ListBetStatusView(generic.ListView):
    template_name = "bet/bet-error-list.html"

    def get_queryset(self):
        """
        Overwrite the get_queryset method.

        this method return the all `BetStatus` of given bet `ID`.
        also apply the sorting on the basis of given `sort` field
        :return BetStatus queryset:
        """
        bet_id = self.request.GET.get('bet', None)
        sort_field = self.request.GET.get('sort', None)
        order_field = '-id'

        if sort_field:
            if sort_field.replace("-", "") in [f.name for f in BetErrors._meta.get_fields()]:
                order_field = sort_field
        return BetErrors.objects.filter(bet__id=bet_id).order_by(order_field)


class CreateBetView(generic.FormView):
    """
    View handle and show the dash-board
    """
    template_name = "bet/bet-create.html"
    form_class = UserBetForm
    success_url = reverse_lazy('bet:create_bet_page')

    @method_decorator(login_required(login_url=reverse_lazy('users:login')))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = super(CreateBetView, self).get_form()
        # Set initial values and custom widget
        initial_base = self.get_initial()
        form.initial = initial_base
        # return response using standard render() method
        return render(request, self.template_name,
                      {'form': form,
                       'special_context_variable': 'My special context variable!!!'})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        # Verify form is valid
        if form.is_valid():
            # Call parent form_valid to create model record object
            super().form_valid(form)
            form.save(request)
            # Add custom success message
            messages.success(request, MSG.BET_SAVED)
            # Redirect to success page
            return HttpResponseRedirect(self.get_success_url())
        # Form is invalid
        # Set object to None, since class-based view expects model record object
        self.object = None
        # Return class-based view form_invalid to generate form with errors
        return self.form_invalid(form)
