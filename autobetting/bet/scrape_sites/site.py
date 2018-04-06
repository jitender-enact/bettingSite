from bet.models import (BET_ERROR_STATUS,
                        BetErrors)
from users.core import constants as ERROR_MSG

# Define ErrorStatus
ERROR_STATUS = {value: key for key, value in BET_ERROR_STATUS}


class BaseSite:
    IsError = False
    ErrorMsg = {}
    AcceptedGameType = []
    AcceptedGameIntervals = []
    AcceptedGameCombination = {}

    def initial_validation(self, game_interval, game_type):
        """
        Initially validate the bet before crawling the site

        Check the current site supports the given game_interval
        and game_type or not.
        """
        if self.AcceptedGameIntervals:
            if not (game_interval in self.AcceptedGameIntervals):
                self.set_message(True, ERROR_MSG.INVALID_INTERVAL_SELECTED)

        if self.AcceptedGameType:
            if not (game_type in self.AcceptedGameType):
                self.set_message(True, ERROR_MSG.INVALID_GAME_TYPE_SELECTED)

        if self.AcceptedGameCombination and not self.IsError:
            if not (game_type in self.AcceptedGameCombination):
                self.set_message(True, ERROR_MSG.INVALID_GAME_TYPE_SELECTED)
            elif not (game_interval in self.AcceptedGameCombination[game_type]):
                self.set_message(True, ERROR_MSG.INVALID_INTERVAL_SELECTED)

    def set_message(self, is_error, message, site_message=None):
        """
        Set the `IsError` and `ErrorMsg`
        :param is_error:  True or False (Boolean)
        :param message:  message (string)
        """
        self.IsError = is_error
        self.ErrorMsg = {"message": message, "site_message": None}

    def save_bet_messages(self, berErrorObj):
        """

        :param berErrorObj : (instance of BetErrors Model)
        :return instance:
        """
        status = ERROR_STATUS["error" if self.IsError else "success"]
        berErrorObj.status = status
        berErrorObj.message = self.ErrorMsg["message"]
        berErrorObj.site_message = self.ErrorMsg["site_message"]
        berErrorObj.save()
        return berErrorObj
