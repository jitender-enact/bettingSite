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
        exclude = ['user', 'ticket', 'created', 'modified']

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
            "pattern": "^[+,\-,o,u][0-9]+$",
            "data-pattern-error": 'Incoming line must be start with +/- (spread) or o/u (Total)',
            "data-equalElem": "selected_line"
        })

        self.update_the_widget_attr('incoming_juice', {
            'class': 'form-control',
            'autofocus': False,
            'placeholder': 'Incoming Jiuce',
            "pattern": "^[+,\-][0-9]+$",
            "data-pattern-error": 'Incoming juice must be start with +/- '
        })
        self.fields['incoming_juice'].required = True

        self.fields['amount'] = forms.DecimalField(widget=forms.TextInput)
        self.fields['amount'].required = False
        self.update_the_widget_attr('amount', {
            'class': 'form-control',
            'autofocus': False,
            'placeholder': 'Incoming Bet Amount (optional, default=$100)',
            'required': False
        })

        self.fields['rotation'] = forms.IntegerField(widget=forms.TextInput)
        self.update_the_widget_attr('rotation', {
            'class': 'form-control',
            'autofocus': False,
            'placeholder': 'Rotation# (full game always)',
            "pattern": "^[0-9]+$"
        })

        self.update_the_widget_attr('game_team', {
            'class': 'form-control',
            'autofocus': False,
            'placeholder': 'Game/Team (display only)',
        })

        self.fields['is_default_amount'] = forms.BooleanField(widget=forms.HiddenInput, required=False, initial=True)

        self.fields['game_type'] = forms.ChoiceField(choices=GAME_TYPES, widget=forms.RadioSelect)
        self.fields['game_interval'] = forms.ChoiceField(choices=GAME_INTERVALS, widget=forms.RadioSelect)
        self.update_the_widget_attr('game_interval', {
            'class': 'form-control period',
            'autofocus': False,
        })
        self.fields['selected_line'] = forms.ChoiceField(choices=SELECTED_LINES, widget=forms.RadioSelect)

        current_weeks = (((timezone.now()+datetime.timedelta(days=x)).date(),
                          (timezone.now()+datetime.timedelta(days=x)).date()) for x in range(0, 7))
        self.fields['bet_date'] = forms.ChoiceField(choices=current_weeks, widget=forms.RadioSelect, required=False)

    @staticmethod
    def is_a_number(value):
        """
        Check the provided value is a number or not

        :param value:
        :return True or False: boolean
        """
        try:
            float(value)
            if value in ["NaN", "inf"]:
                return False
            return True
        except ValueError:
            return False

    def clean_bet_date(self):
        # validate amount
        bet_date = self.cleaned_data['bet_date'].strip()
        if bet_date is None or bet_date == "":
            return timezone.now().date()
        else:
            return bet_date

    def clean_amount(self):
        # validate amount
        amount = self.cleaned_data['amount']
        if amount is not None and amount is not "":
            if not self.is_a_number(amount):
                raise forms.ValidationError("Invalid amount")
        return amount


    # def clean_is_default_amount(self):
    #     # validate amount
    #     print(self.cleaned_data)
    #     amount = self.cleaned_data['amount']
    #     is_default_amount = self.cleaned_data['is_default_amount']
    #     print(is_default_amount)
    #     if amount is None or amount == "":
    #         return True
    #     else:
    #         return False


    def clean(self):
        super(UserBetForm, self).clean()
        selected_line = int(self.cleaned_data['selected_line'])
        bet_types = dict(SELECTED_LINES)

        # validate incoming juice
        if "incoming_line" in self.cleaned_data:
            if bet_types[selected_line] not in ['SPREAD', 'TOTAL']:
                self.cleaned_data['incoming_line'] = None

            elif self.cleaned_data['incoming_line']:
                incoming_line = self.cleaned_data['incoming_line'].strip()
                # selected_line = int(self.cleaned_data['selected_line'])
                # bet_types = dict(SELECTED_LINES)
                accepted_param = ["o", "u", "+", "-"]
                first_char = incoming_line[:1]
                remaining_str = incoming_line[1:]

                if first_char not in accepted_param:
                    raise forms.ValidationError("BET INVALID!(Invalid incoming line accept +/- (spread) or o/u (Total).)")

                if not self.is_a_number(remaining_str):
                    raise forms.ValidationError("BET INVALID!(Invalid incoming line)")

                if bet_types[selected_line] == 'SPREAD':
                    if first_char not in accepted_param[2:]:
                        raise forms.ValidationError("BET INVALID!(Doesn't match type)")

                elif bet_types[selected_line] == 'TOTAL':
                    if first_char not in accepted_param[:2]:
                        raise forms.ValidationError("BET INVALID!(Doesn't match type)")
                    elif first_char == "o":
                        self.cleaned_data['incoming_line'] = "-{}".format(remaining_str)
                    else:
                        self.cleaned_data['incoming_line'] = "+{}".format(remaining_str)
            else:
                raise forms.ValidationError("BET INVALID!(Invalid incoming line)")

        # validate incoming juice
        if "incoming_juice" in self.cleaned_data and self.cleaned_data['incoming_juice']:
            incoming_juice = self.cleaned_data['incoming_juice'].strip()
            accepted_param = ["+", "-"]
            first_char = incoming_juice[:1]
            remaining_str = incoming_juice[1:]

            if first_char not in accepted_param:
                raise forms.ValidationError("BET INVALID!(Invalid incoming juice accept +/- .)")

            elif not self.is_a_number(remaining_str):
                raise forms.ValidationError("BET INVALID!(Invalid incoming juice value)")

            elif float(remaining_str) < 100:
                raise forms.ValidationError("BET INVALID!(Invalid incoming juice)")

            elif first_char == "-" and float(remaining_str) == 100:
                raise forms.ValidationError("BET INVALID!(Invalid incoming juice)")
            else:
                self.cleaned_data['incoming_juice'] = incoming_juice

        # validate rotation
        if "rotation" in self.cleaned_data and self.cleaned_data['rotation']:
            rotation = self.cleaned_data['rotation']
            if not self.is_a_number(rotation):
                raise forms.ValidationError("BET INVALID!(Invalid rotation)")
            elif float(rotation) < 0:
                raise forms.ValidationError("BET INVALID!(Invalid rotation)")
            else:
                self.cleaned_data['rotation'] = rotation

        if "amount" in self.cleaned_data and "is_default_amount" in self.cleaned_data:
            amount = self.cleaned_data['amount']
            if amount is None or amount == "":
                self.cleaned_data['amount'] = 0
                self.cleaned_data['is_default_amount'] = True
            else:
                self.cleaned_data['amount'] = amount
                self.cleaned_data['is_default_amount'] = False
        print(self.cleaned_data)
        return self.cleaned_data

    def save(self, request):
        """
        Overwrite the save method and set the user before saving the UserBets instance
        :param request:
        :return UserBets instance:
        """
        print(self.instance.__dict__)
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
