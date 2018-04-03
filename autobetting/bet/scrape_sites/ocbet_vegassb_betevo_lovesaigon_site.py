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
                    'Referer': 'http://vegassb.net/vegassb_login_english.asp?m=',
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
                "update_headrs": {
                    'Origin': '{}',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Upgrade-Insecure-Requests': '1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Referer': 'http://vegassb.net/CustomerDashboard.asp',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'max-age=0',
                }
            },
            "page_5": {
                "method": "post",
                "url": "{}/BbGameSelection.asp",
                "update_headrs": {
                    'Origin': '{}',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Upgrade-Insecure-Requests': '1',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Cache-Control': 'max-age=0',
                    'Referer': 'http://vegassb.net/BbSportSelection.asp',
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
            print(supportedGames[select_game])
            for tag in inputs:
                if tag['type'] and (tag['type'].lower() == 'hidden' or tag['type'].lower() == 'submit'):
                    post_data.update({tag['name']: tag['value']})
                if tag['name'] and tag['name'].upper() == supportedGames[select_game]:
                    print(tag['name'])
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
        table = soup.find("table", attrs={"class": "lines-offering"})

        tr = []
        for row in table.find_all("tr"):
            if not row.find("td").has_attr("colspan"):
                tr.append(row)


        #
        # date = datetime.datetime.strftime(self.ModelObject.bet_date, "%B %d, %Y")
        #
        # # find out game_element (not offline)
        # game_name_div = [tag for tag in soup.find_all("div", attrs={'class': 'gameName'})
        #                  if date in tag.get_text(strip=True) and not ("OFFLINE" in tag.get_text(strip=True))]
        # for ele in game_name_div:
        #     table = ele.find_next_sibling('table', attrs={"class": "gameTeams"})
        #     table_tds = table.find_all("td", attrs={'class': 'sportTitle'})
        #     for td in table_tds:
        #         if "{}".format(self.ModelObject.rotation) in td.get_text(strip=True):
        #             game_element = td.parent
        #
        # # map the selected_lines with css class names
        # selected_line_names_map = {SELECTED_LINES[0][1]: "pointSpread",
        #                            SELECTED_LINES[2][1]: "moneyLine",
        #                            SELECTED_LINES[1][1]: "totalPoints",
        #                            SELECTED_LINES[3][1]: "teamTotal"
        #                            }
        #
        # selected_line_names = {key: value for key, value in SELECTED_LINES}  # dict of selected lines
        #
        # # define the css class
        # selected_line_class = selected_line_names_map[selected_line_names[self.ModelObject.selected_line]]
        #
        # if game_element:
        #     ele = None
        #     if selected_line_class == "pointSpread":
        #         pointSpreadEle = game_element.findChild('td', attrs={'class': selected_line_class})
        #         if pointSpreadEle:
        #             ele = pointSpreadEle.findChild('table')
        #     else:
        #         ele = game_element.findChild('td', attrs={'class': selected_line_class})
        #
        #     inputEle = ele.findChild('input')
        #     if inputEle:
        #
        #         # set amount
        #         post_data.update({inputEle['name']: self.ModelObject.amount})
        #
        #         if selected_line_class in ["pointSpread", "totalPoints"]:
        #             selectEle = ele.findChild('select')
        #             post_data.update({selectEle['name']: selectEle.findChild('option',
        #                                                                      attrs={'selected': True})['value']})
        #             selectEleText = selectEle.findChild('option', attrs={'selected': True}).get_text(strip=True)
        #             selectEleTextList = selectEleText.split(" ")
        #
        #             total_point = ["OV", "UN"]
        #
        #             # calculate the incomingJuiceRS and incomingLineRS on the basis of fraction values
        #             for key, val in enumerate(selectEleTextList):
        #                 if val == "Even":
        #                     selectEleTextList[key] = 100
        #
        #                 if val in FRACTION_VALUES:
        #                     fraction = FRACTION_VALUES[val] if (int(selectEleTextList[key - 1]) > 0) \
        #                         else -1 * FRACTION_VALUES[val]
        #                     if key == (len(selectEleTextList) - 1):
        #                         incomingJuiceRS = int(selectEleTextList[key - 1]) + fraction
        #                     else:
        #                         incomingLineRS = int(selectEleTextList[key - 1]) + fraction
        #                 elif val in total_point:
        #                     if val == "OV":
        #                         selectEleTextList[key + 1] = -1 * int(selectEleTextList[key + 1])
        #                     else:
        #                         selectEleTextList[key] = int(selectEleTextList[key])
        #                 else:
        #                     if key != (len(selectEleTextList) - 1) and incomingLineRS == -1000000000000000:
        #                         incomingLineRS = int(val)
        #                     else:
        #                         incomingJuiceRS = int(val)
        #
        #         elif selected_line_class == "moneyLine":
        #             money_tds = ele.find_all("td")
        #             incomingLineRS = 0
        #             if money_tds.length >= 1:
        #                 td = money_tds[1]
        #                 incomingJuiceRS = (100 if (td.next_element.strip() == "Even")
        #                                    else int(td.next_element.strip())
        #                                    ) if (td.next_element.strip() != "") else incomingJuiceRS
        #     else:
        #         pass
        #         # display input field not found
        #
        #
        # else:
        #     self.set_message(True, ERROR_MSG.ROTATION_NUMBER_NOT_FOUND)
        #     return
        #     # error not found element
        #
        # post_data.update({'sbm1': "Submit All Wagers"})
        #
        # if (int(self.ModelObject.incoming_line) <= int(incomingLineRS) and
        #         int(self.ModelObject.incoming_juice) <= int(incomingJuiceRS)):
        #     self.scrape_process.SITE_PAGES['page_5']["post_data"] = [(key, val) for key, val in post_data.items()]
        # else:
        #     # display error of mismatch incomingLines or incomingJuice
        #     self.set_message(True, ERROR_MSG.PROVIDED_ODDS_NOT_MATCH)

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
        # self.applyBet()
        # if self.IsError:
        #     self.save_bet_messages(self.betErrorObject)
        #     return
        #
        # self.scrape_process.nextPage()
        # self.page_response = self.scrape_process.getPage()
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
