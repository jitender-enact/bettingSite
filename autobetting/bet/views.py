from django.shortcuts import render, HttpResponseRedirect
from django.views import generic
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings
from users.core import constants as MSG
from bet.forms import UserBetForm, UserSiteCredentialsFrom
from bet.models import UserBets, BetErrors, UserSiteCredentials, Sites, BET_ERROR_STATUS

from bet.scrape_sites.diamond_eight_betbruh_site import DiamondEightBetbruhSite
# Create your views here.


class ListBetView(generic.ListView):
    template_name = "bet/bet-list.html"
    paginate_by = settings.LIST_VIEW_PAGINATION

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
    paginate_by = settings.LIST_VIEW_PAGINATION

    def get(self, request, bet_id, *args, **kwargs):
        self.bet_id = bet_id
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Overwrite the get_queryset method.

        this method return the all `BetStatus` of given bet `ID`.
        also apply the sorting on the basis of given `sort` field
        :return BetStatus queryset:
        """
        bet_id = self.bet_id
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
    success_url = reverse_lazy('bet:list_credentials_page')

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
            betObject = form.save(request)

            self.initializeCrawling(betObject)
            # Add custom success message
            messages.success(request, MSG.BET_SAVED)
            # Redirect to success page
            return HttpResponseRedirect(self.get_success_url())
        # Form is invalid
        # Set object to None, since class-based view expects model record object
        self.object = None
        # Return class-based view form_invalid to generate form with errors
        return self.form_invalid(form)

    def initializeCrawling(self, betObject):
        """
        Method get all user's site credentials and create the BetErrors object for each credential
        then call the startThread Method.

        Main functionality of this method to get all required objects of model(data from database), so that no need
        to get the object(Model object) in other method.
        :param betObject:
        :return:
        """

        # get all user site credentials
        credentials = UserSiteCredentials.objects.filter(user__id=self.request.user.id,
                                                         is_active=True,
                                                         site__is_active=True)

        if credentials:
            for credential in credentials:

                # create BetErrors Object with with status=1
                betErrors = BetErrors.objects.create(**{
                    "bet_id": betObject.id,
                    "site_id": credential.site.id,
                    "message": "Pending"
                })

                # call the startThread method
                self.startThread(betObject, credential, betErrors)

    def startThread(self, betObject, credentials, betErrors):
        """
        Start the crawling thread for each site.
        :param betObject:
        :param credentials:
        :param betErrors:
        :return:
        """
        def site_crawling(betObject, credentials, betErrors):
            """
            start the crawling of site
            :param betObject:
            :param credentials:
            :param betErrors:
            :return:
            """
            site = DiamondEightBetbruhSite(betObject, credentials, betErrors)
            site.crawling()

        import threading
        if credentials.site.site_name.upper() in ["DIAMONDSB", "EIGHTPLAYS", "BETBRUH"]:

            # initialize thread
            t = threading.Thread(target=site_crawling, args=(betObject, credentials, betErrors), kwargs={})
            t.setDaemon(True)  # set thread in bg
            t.start()  # start thread


class ListUserCredentialsView(generic.ListView):
    template_name = "bet/user-site-credentials-list.html"
    paginate_by = settings.LIST_VIEW_PAGINATION

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
            if sort_field.replace("-", "") in [f.name for f in UserSiteCredentials._meta.get_fields()]:
                order_field = sort_field
        return UserSiteCredentials.objects.filter(user__id=self.request.user.id).order_by(order_field)


class CreateUserCredentialsView(generic.FormView):
    """
    View handle and show the user credentials
    """
    template_name = "bet/user-site-credentials-create.html"
    form_class = UserSiteCredentialsFrom
    success_url = reverse_lazy('bet:create_bet_page')

    @method_decorator(login_required(login_url=reverse_lazy('users:login')))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get(self, request, *args, **kwargs):
        form = super(CreateUserCredentialsView, self).get_form()
        # Set initial values and custom widget
        initial_base = self.get_initial()
        initial_base.update({'request': request})
        form.initial = initial_base
        # return response using standard render() method
        return render(request, self.template_name,
                      {'form': form,
                       'special_context_variable': 'My special context variable!!!'})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        initial_base = self.get_initial()
        initial_base.update({'request': request})
        # Verify form is valid
        if form.is_valid():
            # Call parent form_valid to create model record object
            super().form_valid(form)
            form.save(request)

            # Add custom success message
            messages.success(request, MSG.CREDENTIALS_SAVED)
            # Redirect to success page
            return HttpResponseRedirect(self.get_success_url())
        # Form is invalid
        # Set object to None, since class-based view expects model record object
        self.object = None
        # Return class-based view form_invalid to generate form with errors
        return self.form_invalid(form)