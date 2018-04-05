from django.conf import settings
from bet.scrapper.scrape_process import ScrapeProcess
from bet.scrape_sites.site import BaseSite
from bet.models import GAME_INTERVALS, GAME_TYPES, SELECTED_LINES
from bet.scrape_sites.unicode_constants import FRACTION_VALUES
from users.core import constants as ERROR_MSG
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, TooManyRedirects, Timeout, RequestException

class SportsbetTdseven(BaseSite):
    """
    Class handle the crawling of Ocbet.ag, Vegassb.com, Betevo.com and Lovesaigon.com sites.
    """
    page_response = None
    AcceptedGameType = ["NBA"]
    AcceptedGameIntervals = ["GAME"]
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
                "method": "post",
                "url": "{}/cog/loginVerify.asp",
                "update_headers": {
                    'Origin': '{}',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Upgrade-Insecure-Requests': '1',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Cache-Control': 'max-age=0',
                    'Referer': '{}/',
                    'Connection': 'keep-alive',
                },
                "post_data": [
                    ('UserID', ''),  # "wine108"
                    ('Password', ''),  # "kt17"
                ]
            },
            "page_3": {
                "method": "get",
                "url": "{}/cog/sportselection.asp",
                "update_headers": {
                    'Origin': '{}',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Upgrade-Insecure-Requests': '1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Referer': '{}/',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'max-age=0',
                }
            },
            "page_4": {
                "method": "post",
                "url": "{}/cog/GameSelection.asp?WTID=9&WCATID=1",
                "update_headers": {
                    'Origin': '{}',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Upgrade-Insecure-Requests': '1',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Cache-Control': 'max-age=0',
                    'Referer': '{}/cog/sportselection.asp',
                    'Connection': 'keep-alive',
                },
                "post_data": []
            },
            "page_5": {
                "method": "post",
                "url": "{}/cog/Wager.asp?WTID=9&WCATID=1&ls=1",
                "update_headers": {
                    'Origin': '{}',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Upgrade-Insecure-Requests': '1',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Cache-Control': 'max-age=0',
                    'Referer': '{}/cog/GameSelection.asp?WTID=9&WCATID=1',
                    'Connection': 'keep-alive',
                },
                "post_data": []
            }

        }

        # update the credentials
        self.SITE_PAGES["page_2"]['post_data'] = [('UserID', credentialObject.username),
                                                  ('Password', credentialObject.password)]

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
        # for key, val in GAME_TYPES:
        #     if val == "BASKETBALL COLLEGE":
        #         self.GAME_TYPES.update({key: "NCAA"})
        #     else:
        #         self.GAME_TYPES.update({key: val})

        self.GAME_INTERVALS = {key: val.replace("QTR", "QUARTER") for key, val in GAME_INTERVALS}

    def site_login(self):
        """
        Login to the Site.

        Firstly its open the SITE["page_1"] using `get` method, For creating the cookies
        then its login the user
        """
        self.page_response = self.scrape_process.getPage()  # get first page to initialize the cookies and session
        self.scrape_process.nextPage()  # set next page
        self.page_response = self.scrape_process.getPage()  # login to site

    def _validate_select_game_page(self, soup_dom_object):
        """
        Validate the "SportSelection" page.

        If page valid than it return `return_data['valid']=True`
        otherwise it return `return_data['valid']=False` and error msg
        :param soup_dom_object: DOM Object of BeautifulSoup
        :return return_data: Dictionary
        """
        return_data = {"valid": True, "msg": ""}  # set the `True` value of `return_data` variable.
        form = soup_dom_object.find("form", attrs={"name": "SportSelectionForm"})
        if not form:
            return_data.update({"valid": False, "msg": "Not found form[name=SportSelectionForm]"})
        return return_data

    def select_game(self):
        """
        Select game from 'page_response' object.

        Using the `BeautifulSoup` its read the content of `page_response.text`
        and validate the page. if page validate successfully then its fetch the necessary content
        and compare it with `self.ModelObject` and updated the `SITE_PAGES['page_4']["post_data"]`
        """
        soup = BeautifulSoup(self.page_response.text, 'lxml')
        valid_dict = self._validate_select_game_page(soup)

        if valid_dict['valid']:
            form = soup.find("form", attrs={'name': 'SportSelectionForm'})
            select_game = form.find("input", attrs={'name': 'lg30'})
            if select_game:
                self.scrape_process.SITE_PAGES['page_5']["post_data"] = [(select_game['name'], select_game['value']),]
            else:
                # game not found
                self.set_message(True, ERROR_MSG.GAME_NOT_FOUND)

    def _validate_apply_bet_page(self, soup_dom_object):
        """
        Validate the "GameSelection" page.

        If page valid than it return `return_data['valid']=True`
        otherwise it return `return_data['valid']=False` and error msg
        :param soup_dom_object: DOM Object of BeautifulSoup
        :return return_data: Dictionary
        """
        return_data = {"valid": True, "msg": ""}  # set the `True` value of `return_data` variable.
        pass
        return return_data

    def apply_bet(self):
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

    # def submitBet(self):
    #     soup = BeautifulSoup(self.page_response.text, 'html.parser')
    #     post_data = {}
    #
    #     form = soup.find("form", attrs={"name": 'frmMain'})
    #     post_data.update({tag["name"]: tag["value"] for tag in form.find_all("input", attrs={"type": "hidden"})
    #                       if tag["name"] != 'wgt'})
    #     post_data.update({"wgt": 'base'})
    #
    #     if settings.LIVE_BETTING:
    #         post_data.update({'password': self.credentialObject.password})
    #     else:
    #         post_data.update({'password': "sdsdsdsdsdsdsdsddsdsd"})  # set default password
    #     self.scrape_process.SITE_PAGES['page_6']["post_data"] = [(key, val) for key, val in post_data.items()]
    #
    # def crawling(self):
    #     game_types = self.GAME_TYPES
    #     game_interval = {key: value for key, value in GAME_INTERVALS}
    #     self.initial_validation(game_interval[self.ModelObject.game_interval], game_types[self.ModelObject.game_type])
    #     if self.IsError:
    #         self.save_bet_messages(self.betErrorObject)
    #         return
    #
    #     self.siteLogin()
    #     if self.page_response is None:
    #         self.set_message(True, ERROR_MSG.NOT_FOUND_RESPONSE)
    #
    #     elif self.page_response.url == "{}/LoginFailed.asp".format(self.siteLink):
    #         self.set_message(True, ERROR_MSG.INVALID_CREDENTIALS)
    #
    #     if self.IsError:
    #         self.save_bet_messages(self.betErrorObject)
    #         return
    #
    #     self.scrape_process.nextPage()
    #     self.page_response = self.scrape_process.getPage()
    #     if self.page_response is None:
    #         self.set_message(True, ERROR_MSG.NOT_FOUND_RESPONSE)
    #
    #     if self.IsError:
    #         self.save_bet_messages(self.betErrorObject)
    #         return
    #
    #     self.selectGame()
    #     if self.IsError:
    #         self.save_bet_messages(self.betErrorObject)
    #         return
    #
    #     self.scrape_process.nextPage()
    #     self.page_response = self.scrape_process.getPage()
    #     if self.page_response is None:
    #         self.IsError = True
    #         self.ErrorMsg = ERROR_MSG.NOT_FOUND_RESPONSE
    #     if self.IsError:
    #         self.save_bet_messages(self.betErrorObject)
    #         return
    #
    #     # print(self.page_response.text)
    #     self.applyBet()
    #     if self.IsError:
    #         self.save_bet_messages(self.betErrorObject)
    #         return
    #
    #     self.scrape_process.nextPage()
    #     self.page_response = self.scrape_process.getPage()
    #     print(self.page_response)
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


class TdsevenwinSite(SportsbetTdseven):

    def crawling(self):
        try:
            game_types = self.GAME_TYPES
            game_interval = {key: value for key, value in GAME_INTERVALS}
            self.initial_validation(game_interval[self.ModelObject.game_interval], game_types[self.ModelObject.game_type])
            if self.IsError:
                self.save_bet_messages(self.betErrorObject)
                return

            self.site_login()
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

            self.select_game()
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
            self.apply_bet()
            if self.IsError:
                self.save_bet_messages(self.betErrorObject)
                return

            self.scrape_process.nextPage()
            self.page_response = self.scrape_process.getPage()
            print(self.page_response)
        except Timeout as err:
            print("Timeout Error:", err)
        except TooManyRedirects as err:
            print("Too many redirect")
        except RequestException as err:
            print("OOps: Something Else", err)
        except Exception as err:
            print("Interval server error", err)

