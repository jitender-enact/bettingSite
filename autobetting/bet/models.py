from django.db import models
from django.contrib.auth.models import User
from users.core.utils import generate_token
# Create your models here.


GAME_TYPES = (
    (1, "FOOTBALL COLLEGE"),
    (2, "NFL"),
    (3, "BASKETBALL COLLEGE"),
    (4, "NBA"),
    (5, "WNBA"),
    (6, "MLB"),
    (7, "NHL"),
    (8, "SOCCER"),
    (9, "GOLF"),
    (10, "BASEBALL COLLEGE"),
    (11, "PROP")
)

GAME_INTERVALS = (
    (1, 'GAME'),
    (2, '1ST HALF'),
    (3, '2ND HALF'),
    (4, '1ST QTR'),
    (5, '2ND QTR'),
    (6, '3RD QTR'),
    (7, '4TH QTR')
)

SELECTED_LINES = (
    (1, 'SPREAD'),
    (2, 'TOTAL'),
    (3, 'MONEY LINE'),
    (4, 'TEAM TOTAL')
)

BET_ERROR_STATUS = (
    (1, 'initialize'),
    (2, 'success'),
    (3, 'error')
)

class Sites(models.Model):
    site_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Name of the site")
    site_link = models.CharField(max_length=255, null=True, blank=True, verbose_name="Url link of the site")
    is_active = models.BooleanField(default=True, verbose_name="Is site active for crawling")
    created = models.DateTimeField(null=True, auto_now_add=True)
    modified = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return 'Site Name: {}'.format(self.site_name)


class UserSiteCredentials(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="site_credentials")
    site = models.ForeignKey(Sites, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="credentials")
    is_active = models.BooleanField(default=True, verbose_name="Is site credentials active")
    username = models.CharField(max_length=255, null=True, blank=True, verbose_name="Username or Email")
    password = models.CharField(max_length=255, null=True, blank=True, verbose_name="User's pass")
    default_amount = models.DecimalField(max_digits=11, decimal_places=3, default=0)
    created = models.DateTimeField(null=True, auto_now_add=True)
    modified = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return 'Credentials of user: {}'.format(self.user.username)


class UserBets(models.Model):
    ticket = models.CharField(default=generate_token, max_length=64, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="user_bets")
    game_name = models.CharField(max_length=255, null=True, blank=True,
                                 verbose_name="Name of the game (only for display)")
    game_type = models.IntegerField(default=GAME_TYPES[0][0], verbose_name="Type of game")
    game_interval = models.IntegerField(default=GAME_INTERVALS[0][0], verbose_name="Game interval")
    game_team = models.CharField(max_length=255, null=True, blank=True)
    rotation = models.IntegerField(default=0)
    selected_line = models.IntegerField(default=SELECTED_LINES[0][0], verbose_name="Selected line")
    incoming_line = models.CharField(max_length=12, null=True, blank=True)
    incoming_juice = models.CharField(max_length=12, null=True, blank=True)
    amount = models.DecimalField(max_digits=11, decimal_places=3, default=0)
    is_default_amount = models.BooleanField(default=False)
    bet_date = models.DateField(null=True, blank=True)
    created = models.DateTimeField(null=True, auto_now_add=True)
    modified = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return 'Bet by user: {}'.format(self.user.username)


class BetErrors(models.Model):
    bet = models.ForeignKey(UserBets, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="bet_errors")
    site = models.ForeignKey(Sites, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="site_errors")
    message = models.TextField(blank=True, null=True)
    site_message = models.TextField(blank=True, null=True)
    status = models.IntegerField(default=BET_ERROR_STATUS[0][0])
    created = models.DateTimeField(null=True, auto_now_add=True)
    modified = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return 'Bet message: {}'.format(self.message)


class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, null=True, blank=True,
                                related_name="user_preferences")
    game_type = models.IntegerField(default=0, verbose_name="Type of sport")
    game_interval = models.IntegerField(default=0, verbose_name="Game interval")
    selected_line = models.IntegerField(default=0, verbose_name="Bet type")
    created = models.DateTimeField(null=True, auto_now_add=True)
    modified = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return '{}'.format(self.pk)