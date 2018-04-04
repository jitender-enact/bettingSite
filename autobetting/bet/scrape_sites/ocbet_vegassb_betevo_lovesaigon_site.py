from django.conf import settings
from bet.scrapper.scrape_process import ScrapeProcess
from bet.scrape_sites.site import BaseSite
from bet.models import GAME_INTERVALS, GAME_TYPES, SELECTED_LINES
from bet.scrape_sites.unicode_constants import FRACTION_VALUES
from users.core import constants as ERROR_MSG
from bs4 import BeautifulSoup
import datetime


class OcbetVegaBetevoLoveSite(BaseSite):
    """
    Class handle the crawling of Ocbet.ag, Vegassb.com, Betevo.com and Lovesaigon.com sites.
    """
    page_response = None
    AcceptedGameType = ["NFL", "NCAA", "NBA", "NHL"]
    AcceptedGameIntervals = ["GAME", "1ST HALF", "2ND HALF", "1ST QTR", "2ND QTR", "3RD QTR", "4TH QTR"]
    AcceptedGameCombination = {
        "NFL": ["GAME", "1ST HALF", "2ND HALF", "1ST QTR", "2ND QTR", "3RD QTR", "4TH QTR"],
        "NCAA": ["GAME", "1ST HALF", "2ND HALF"],
        "NBA": ["GAME", "1ST HALF", "2ND HALF"],
        "NHL": ["GAME"]
    }
    IsError = False
    ErrorMsg = None
    SITE_PAGES = {}

    def __init__(self, betModelObject, credentialObject, betErrorModelObject):
        """
        Accept UserBetModel Object, BetErrorModel Object (error messages) and CredentialModel object (login credentials)
        """
        self.SITE_PAGES = {
            "page_1": {
                "method": "get",
                "url": "{}/",
            },
            "page_2": {
                "method": "get",
                "url": "",
            },
            "page_3": {
                "method": "post",
                "url": "{}/LoginVerify.asp",
                "update_headers": {
                    'Origin': '{}',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Upgrade-Insecure-Requests': '1',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Cache-Control': 'max-age=0',
                    'Referer': '{}/vegassb_login_english.asp?m=',
                    'Connection': 'keep-alive',
                },
                "post_data": [
                    ('customerID', ''),  # "wine108"
                    ('password', ''),  # "kt17"
                ]
            },
            "page_4": {
                "method": "get",
                "url": "{}/BbSportSelection.asp",
                "update_headers": {
                    'Origin': '{}',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Upgrade-Insecure-Requests': '1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Referer': '{}/CustomerDashboard.asp',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'max-age=0',
                }
            },
            "page_5": {
                "method": "post",
                "url": "{}/BbGameSelection.asp",
                "update_headers": {
                    'Origin': '{}',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Upgrade-Insecure-Requests': '1',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Cache-Control': 'max-age=0',
                    'Referer': '{}/BbSportSelection.asp',
                    'Connection': 'keep-alive',
                },
                "post_data": []
            },
            "page_6": {
                "method": "post",
                "url": "{}/BbVerifyWager.asp",
                "update_headers": {
                    'Origin': '{}',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Upgrade-Insecure-Requests': '1',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Cache-Control': 'max-age=0',
                    'Referer': '{}/BbGameSelection.asp',
                    'Connection': 'keep-alive',
                },
                "post_data": []
            }

        }
        # update the credentials
        self.SITE_PAGES["page_3"]['post_data'] = [('customerID', credentialObject.username),
                                                  ('password', credentialObject.password)]
        siteLink = betErrorModelObject.site.site_link.strip()
        siteLink = siteLink if (siteLink[len(siteLink) - 1] != "/") else siteLink[:-1]
        self.siteLink = siteLink

        for key, val in self.SITE_PAGES.items():
            val['url'] = val['url'].format(siteLink)
            if "update_headers" in val and "Origin" in val['update_headers']:
                val['update_headers']["Origin"] = val['update_headers']["Origin"].format(siteLink)
            if "update_headers" in val and "Referer" in val['update_headers']:
                val['update_headers']["Referer"] = val['update_headers']["Referer"].format(siteLink)
            self.SITE_PAGES[key] = val

        self.scrape_process = ScrapeProcess(self.SITE_PAGES)  # create the ScrapeProcess object.
        self.page_response = None
        self.ModelObject = betModelObject
        self.credentialObject = credentialObject
        self.betErrorObject = betErrorModelObject

        self.GAME_TYPES = {}
        for key, val in GAME_TYPES:
            if val == "BASKETBALL COLLEGE":
                self.GAME_TYPES.update({key: "NCAA"})
            else:
                self.GAME_TYPES.update({key: val})

        self.GAME_INTERVALS = {}
        for key, val in GAME_INTERVALS:
            self.GAME_INTERVALS.update({key: val.replace("QTR", "QUARTER")})

    def siteLogin(self):
        """
        Login to the Site
        """
        try:
            self.page_response = self.scrape_process.getPage()  # get first page to initialize the cookies and session
            self.scrape_process.SITE_PAGES["page_2"]['url'] = self.page_response.url
            self.scrape_process.SITE_PAGES["page_3"]['update_headers']['Referer'] = self.page_response.url
            self.scrape_process.nextPage()  # set next page
            self.page_response = self.scrape_process.getPage()

            self.scrape_process.nextPage()  # set next page
            self.page_response = self.scrape_process.getPage()  # login to site

        except Exception as e:
            # unable to access site
            self.IsError = True
            self.ErrorMsg = ERROR_MSG.INVALID_SERVER_ERROR

    def selectGame(self):
        """
        select game from 'page_response' object
        """
        game_types = {val: key for key, val in self.GAME_TYPES.items()}
        game_intervals = {val.replace("QUARTER", "QTR"): key for key, val in self.GAME_INTERVALS.items()}
        supportedGames = {}
        for game, intervels in self.AcceptedGameCombination.items():
            game_name = game
            if game in ["NFL"]:
                game_name = "FOOTBALL_{}".format(game)
            elif game in ["NCAA", "NBA"]:
                game_name = "BASKETBALL_{}".format(game)
            elif game_name in ["NHL"]:
                game_name = "HOCKEY_{}".format(game)

            for inter in intervels:
                key = "game_{}_inter_{}".format(game_types[game], game_intervals[inter])
                val = "{}*{}".format(game_name, inter.replace("QTR", "QUARTER"))
                supportedGames.update({key: val})

        select_game = "game_{}_inter_{}".format(self.ModelObject.game_type, self.ModelObject.game_interval)
        if not select_game in supportedGames:
            self.set_message(True, ERROR_MSG.GAME_NOT_FOUND)
            return

        soup = BeautifulSoup(self.page_response.text, 'html.parser')
        form = soup.find("form", attrs={'name': 'SportSelectionForm'})
        if form:
            post_data = {}
            inputs = form.find_all("input")
            for tag in inputs:
                if tag['type'] and (tag['type'].lower() == 'hidden' or tag['type'].lower() == 'submit'):
                    post_data.update({tag['name']: tag['value']})
                if tag['name'] and tag['name'].upper() == supportedGames[select_game]:
                    post_data.update({tag['name']: "on"})

            if not inputs:
                # structure changed
                pass
            self.scrape_process.SITE_PAGES['page_5']["post_data"] = [(key, val) for key, val in post_data.items()]
        else:
            pass
            # structure changed

    def applyBet(self):
        """
        Apply the bet

        Check the betting pages and compare all values (incomingJuice, incomingLine, rotation and minimum amount)
        :return:
        """

        # create instance of the BeautifulSoup
        soup = BeautifulSoup(self.page_response.text, 'lxml')

        post_data = {}  # initialize post_data as dict
        incomingLineRS = -1000000000000000  # set default incoming Line
        incomingJuiceRS = -1000000000000000  # set default incoming Juice

        # set the all hidden and other input and select element  values in `post_data`
        form = soup.find("form", attrs={"name": "GameSelectionForm"})
        table = form.find("table", attrs={"class": "lines-offering"})

        for input_ele in form.find_all("input", attrs={"type": "hidden"}):
            post_data.update({input_ele['name']: input_ele['value'] if input_ele.has_attr('value') else ""})

        date = "{date:%a} {date.month}/{date.day}".format(date=self.ModelObject.bet_date)

        game_element = None

        for row in table.find_all("tr"):
            if row.find("td") and row.find("td").get_text(strip=True) == date:

                tds = row.find_all("td")

                # td [1] for getting the rotation value
                rotation_td = tds[1].get_text(strip=True) if tds and len(tds) > 0 else None


                if int(rotation_td) == self.ModelObject.rotation:
                    game_element = row
                    break

                sibling = row.find_next_sibling("tr")
                if sibling and (not sibling.has_attr("colspan")):
                    tds = row.find_all("td")

                    # td [1] for getting the rotation value
                    rotation_td = tds[1].get_text(strip=True) if tds and len(tds) > 0 else None

                    if int(rotation_td) == self.ModelObject.rotation:
                        game_element = row
                        break
        if game_element:
            tds = game_element.find_all("td")

            # td[5] = Spread Line, td[6] = Money Line, td[7] = Total Point, td[8] = Team total point
            selected_lines = {value: key for key, value in SELECTED_LINES}
            selected_line_index = {selected_lines["SPREAD"]: 5,
                                   selected_lines["TOTAL"]: 7,
                                   selected_lines['MONEY LINE']: 6,
                                   selected_lines["TEAM TOTAL"]: 8}

            index = selected_line_index[self.ModelObject.selected_line] if self.ModelObject.selected_line \
                                                                           in selected_line_index else None

            if not index is None:
                element = tds[index]
                input_ele = element.find("input", attrs={'type': 'text'})
                if input_ele:
                    context = element.get_text(strip=True)
                    context = context.replace(u'\xa0', " ")
                    context_list = context.split(" ")

                    post_data.update({input_ele['name']: '{0:.2f}'.format(self.ModelObject.amount)})

                    total_point = ["Over", "Under"]
                    for key, val in enumerate(context_list):
                        if val == "":
                            continue
                        if val in FRACTION_VALUES:
                            fraction = FRACTION_VALUES[val] if (int(context_list[key - 1]) > 0) \
                                else -1 * FRACTION_VALUES[val]
                            if key == (len(context_list) - 1):
                                incomingJuiceRS = int(context_list[key - 1]) + fraction
                            else:
                                incomingLineRS = int(context_list[key - 1]) + fraction
                        elif val in total_point:
                            if val == "Over":
                                context_list[key + 1] = -1 * int(context_list[key + 1])
                            else:
                                context_list[key] = int(context_list[key])
                        elif self.ModelObject.selected_line == selected_lines['MONEY LINE']:
                            incomingLineRS = 0
                            if incomingJuiceRS == -1000000000000000:
                                incomingJuiceRS = int(val)
                        else:
                            if key != (len(context_list) - 1) and incomingLineRS == -1000000000000000:
                                incomingLineRS = int(val)
                            else:
                                incomingJuiceRS = int(val)

            if (int(self.ModelObject.incoming_line) <= int(incomingLineRS) and
                    int(self.ModelObject.incoming_juice) <= int(incomingJuiceRS)):
                post_data.update({'submit1': 'Continue'})
                self.scrape_process.SITE_PAGES['page_6']["post_data"] = [(key, val) for key, val in post_data.items()]
            else:
                # display error of mismatch incomingLines or incomingJuice
                self.set_message(True, ERROR_MSG.PROVIDED_ODDS_NOT_MATCH)

    def submitBet(self):
        soup = BeautifulSoup(self.page_response.text, 'html.parser')
        post_data = {}

        form = soup.find("form", attrs={"name": 'frmMain'})
        post_data.update({tag["name"]: tag["value"] for tag in form.find_all("input", attrs={"type": "hidden"})
                          if tag["name"] != 'wgt'})
        post_data.update({"wgt": 'base'})

        if settings.LIVE_BETTING:
            post_data.update({'password': self.credentialObject.password})
        else:
            post_data.update({'password': "sdsdsdsdsdsdsdsddsdsd"})  # set default password
        self.scrape_process.SITE_PAGES['page_6']["post_data"] = [(key, val) for key, val in post_data.items()]

    def crawling(self):
        game_types = self.GAME_TYPES
        game_interval = {key: value for key, value in GAME_INTERVALS}
        self.initial_validation(game_interval[self.ModelObject.game_interval], game_types[self.ModelObject.game_type])
        if self.IsError:
            self.save_bet_messages(self.betErrorObject)
            return

        self.siteLogin()
        if self.page_response is None:
            self.set_message(True, ERROR_MSG.NOT_FOUND_RESPONSE)

        elif self.page_response.url == "{}/LoginFailed.asp".format(self.siteLink):
            self.set_message(True, ERROR_MSG.INVALID_CREDENTIALS)

        if self.IsError:
            self.save_bet_messages(self.betErrorObject)
            return

        self.scrape_process.nextPage()
        self.page_response = self.scrape_process.getPage()
        if self.page_response is None:
            self.set_message(True, ERROR_MSG.NOT_FOUND_RESPONSE)

        if self.IsError:
            self.save_bet_messages(self.betErrorObject)
            return

        self.selectGame()
        if self.IsError:
            self.save_bet_messages(self.betErrorObject)
            return

        self.scrape_process.nextPage()
        self.page_response = self.scrape_process.getPage()
        if self.page_response is None:
            self.IsError = True
            self.ErrorMsg = ERROR_MSG.NOT_FOUND_RESPONSE
        if self.IsError:
            self.save_bet_messages(self.betErrorObject)
            return

        # print(self.page_response.text)
        self.applyBet()
        if self.IsError:
            self.save_bet_messages(self.betErrorObject)
            return

        self.scrape_process.nextPage()
        self.page_response = self.scrape_process.getPage()
        print(self.page_response)
        # if self.page_response is None:
        #     self.IsError = True
        #     self.ErrorMsg = ERROR_MSG.NOT_FOUND_RESPONSE
        # elif self.page_response.url == '{}/client/bet-the-board.aspx?error=toomuchtotal'.format(self.siteLink):
        #     self.IsError = True
        #     self.ErrorMsg = ERROR_MSG.INSUFFICIENT_BALANCE
        # elif self.page_response.url == '{}/client/bet-the-board.aspx?error=toolittlesingle'.format(self.siteLink):
        #     self.IsError = True
        #     self.ErrorMsg = ERROR_MSG.MINIMUM_WAGER_LIMIT
        # if self.IsError:
        #     self.save_bet_messages(self.betErrorObject)
        #     return
        #
        # self.submitBet()
        # self.scrape_process.nextPage()
        # self.page_response = self.scrape_process.getPage()
        # if self.page_response is None:
        #     self.IsError = True
        #     self.ErrorMsg = ERROR_MSG.NOT_FOUND_RESPONSE
        #
        # if self.IsError:
        #     self.save_bet_messages(self.betErrorObject)
        #     return
        # else:
        #     self.IsError = False
        #     self.ErrorMsg = ERROR_MSG.BET_PLACED
        #     self.save_bet_messages(self.betErrorObject)
