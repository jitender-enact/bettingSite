from django import forms
from bet.models import UserBets, UserSiteCredentials, Sites, UserPreferences, GAME_INTERVALS, GAME_TYPES,  SELECTED_LINES
from users.forms import WidgetAttributesMixin
from django.utils import timezone
import datetime


class UserBetForm(WidgetAttributesMixin, forms.ModelForm):
    """
    UserBetForm used for creating and validating the UserBet
    """
    class Meta:
        model = UserBets
        exclude = ['user', 'created', 'modified']

    def __init__(self, *args, **kwargs):
        """
        Applied some css class and placeholders into the all
         fields of the UserBetForm form.
        """
        super().__init__(*args, **kwargs)

        self.update_the_widget_attr('game_name', {
            'class': 'form-control',
            'autofocus': False,
            'placeholder': 'Game Name',
        })

        self.update_the_widget_attr('incoming_line', {
            'class': 'form-control',
            'autofocus': False,
            'placeholder': 'Incoming Line (points, spread/total only)',
        })

        self.update_the_widget_attr('incoming_juice', {
            'class': 'form-control',
            'autofocus': False,
            'placeholder': 'Incoming Jiuce',
        })

        self.update_the_widget_attr('amount', {
            'class': 'form-control',
            'autofocus': False,
            'placeholder': 'Incoming Bet Amount (optional, default=$100)',
        })

        self.fields['rotation'] = forms.IntegerField(widget=forms.TextInput)
        self.update_the_widget_attr('rotation', {
            'class': 'form-control',
            'autofocus': False,
            'placeholder': 'Rotation# (full game always)',
        })

        self.update_the_widget_attr('game_team', {
            'class': 'form-control',
            'autofocus': False,
            'placeholder': 'Game/Team (display only)',
        })

        self.fields['game_type'] = forms.ChoiceField(choices=GAME_TYPES, widget=forms.RadioSelect)
        self.fields['game_interval'] = forms.ChoiceField(choices=GAME_INTERVALS, widget=forms.RadioSelect)
        self.fields['selected_line'] = forms.ChoiceField(choices=SELECTED_LINES, widget=forms.RadioSelect)

        current_weeks = (((timezone.now()+datetime.timedelta(days=x)).date(),
                          (timezone.now()+datetime.timedelta(days=x)).date()) for x in range(0, 7))
        self.fields['bet_date'] = forms.ChoiceField(choices=current_weeks, widget=forms.RadioSelect)

    def save(self, request):
        """
        Overwrite the save method and set the user before saving the UserBets instance
        :param request:
        :return UserBets instance:
        """
        self.instance.user = request.user
        return super().save()


class UserSiteCredentialsFrom(WidgetAttributesMixin, forms.ModelForm):
    """
    UserSiteCredentialsFrom used for creating and validating the UserSiteCredentials
    """
    class Meta:
        model = UserSiteCredentials
        exclude = ['user', 'is_active', 'created', 'modified']

    def __init__(self, *args, **kwargs):
        """
        Applied some css class and placeholders into the all
         fields of the UserBetForm form.
        """
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

        self.update_the_widget_attr('username', {
            'class': 'form-control',
            'autofocus': False,
            'placeholder': 'Username/Email',
        })

        self.update_the_widget_attr('password', {
            'class': 'form-control',
            'autofocus': False,
            'placeholder': 'Password',
        })

        # already_selected = UserSiteCredentials.objects.filter(user__id=self.request.user.id).values("site_id")
        sites = Sites.objects.filter(is_active=True)  # .exclude(id__in=already_selected)
        self.fields['site'] = forms.ModelChoiceField(queryset=sites,
                                                     widget=forms.Select)
        self.update_the_widget_attr('site', {
            'class': 'form-control',
            'autofocus': False,
            'placeholder': 'Please select Site',
        })

    def save(self, request):
        """
        Overwrite the save method and set the user before saving the UserSiteCredentials instance
        :param request:
        :return UserSiteCredentials instance:
        """
        self.instance.user = request.user

        # if selected site already exists in UserSiteCredentials, then update the instance otherwise
        # create new instance
        if self.cleaned_data["site"]:
            instance = UserSiteCredentials.objects.filter(site__id=self.cleaned_data["site"].id,
                                                          user__id=request.user.id).first()
            if instance:
                self.instance = instance
                self.instance.username = self.cleaned_data["username"]
                self.instance.password = self.cleaned_data["password"]
        return super().save()


class UserPreferencesForm(WidgetAttributesMixin, forms.ModelForm):
    """
    UserBetForm used for creating and validating the UserBet
    """
    class Meta:
        model = UserPreferences
        exclude = ['user', 'created', 'modified']

    def __init__(self, *args, **kwargs):
        """
        Applied some css class and placeholders into the all
         fields of the UserBetForm form.
        """
        super().__init__(*args, **kwargs)
        game_types = [(0, "----")]
        game_types.extend([(key, val) for key,val in GAME_TYPES])
        game_intervales = [(0, "----")]
        game_intervales.extend([(key, val) for key,val in GAME_INTERVALS])
        selected_lines = [(0, "----")]
        selected_lines.extend([(key, val) for key, val in SELECTED_LINES])

        self.fields['game_type'] = forms.ChoiceField(choices=game_types, widget=forms.Select)
        self.fields['game_interval'] = forms.ChoiceField(choices=game_intervales, widget=forms.Select)
        self.fields['selected_line'] = forms.ChoiceField(choices=selected_lines, widget=forms.Select)

        self.update_the_widget_attr('game_type', {
            'class': 'form-control',
            'placeholder': 'Select Option',
        })
        self.update_the_widget_attr('game_interval', {
            'class': 'form-control',
            'placeholder': 'Select Option',
        })
        self.update_the_widget_attr('selected_line', {
            'class': 'form-control',
            'placeholder': 'Select Option',
        })


    def save(self, request):
        """
        Overwrite the save method and set the user before saving the UserBets instance
        :param request:
        :return UserBets instance:
        """
        self.instance.user = request.user
        instance = UserPreferences.objects.filter(user__id=request.user.id).first()
        if instance:
            self.instance = instance
            self.instance.game_type = int(self.cleaned_data["game_type"])
            self.instance.game_interval = int(self.cleaned_data["game_interval"])
            self.instance.selected_line = int(self.cleaned_data["selected_line"])
        return super().save()
