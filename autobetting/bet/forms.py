from django import forms
from bet.models import UserBets, GAME_INTERVALS, GAME_TYPES,  SELECTED_LINES
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
