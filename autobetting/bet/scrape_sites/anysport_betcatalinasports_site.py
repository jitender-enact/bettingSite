from django.conf import settings
from bet.scrapper.scrape_process import ScrapeProcess
from bet.scrape_sites.site import BaseSite
from bet.models import GAME_INTERVALS, GAME_TYPES, SELECTED_LINES
from bet.scrape_sites.unicode_constants import FRACTION_VALUES
from users.core import constants as ERROR_MSG
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, TooManyRedirects, Timeout, RequestException


class AnysportBetcatalinaSite(BaseSite):
    """
    Class handle the crawling of Ocbet.ag, Vegassb.com, Betevo.com and Lovesaigon.com sites.
    """
    page_response = None
    AcceptedGameType = ["NFL", "NCAA", "NBA", "NHL"]
    AcceptedGameIntervals = ["GAME"]
    AcceptedGameCombination = {
        "MLB": ["GAME"],
        # "NCAA": ["GAME"],
        # "NBA": ["GAME"],
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
                "url": "{}/default.aspx",
            },
            "page_2": {
                "method": "post",
                "url": "{}/default.aspx",
                "update_headers": {
                    'Origin': '{}',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Upgrade-Insecure-Requests': '1',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Cache-Control': 'max-age=0',
                    'Referer': '{}/default.aspx',
                    'Connection': 'keep-alive',
                },
                "post_data": [
                    ('UserID', ''),  # "wine108"
                    ('Password', ''),  # "kt17"
                ]
            },
            "page_3": {
                "method": "get",
                "url": "{}/wager/CreateSports.aspx?WT=0",
                "update_headers": {
                    'Origin': '{}',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Upgrade-Insecure-Requests': '1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Referer': '{}/wager/Message.aspx?lan=undefined',
                    'Connection': 'keep-alive',
                }
            },
            'page_4': {
                "method": "post",
                "url": "{}/wager/CreateSports.aspx?WT=0",
                "update_headers": {
                    'Origin': '{}',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Upgrade-Insecure-Requests': '1',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Cache-Control': 'max-age=0',
                    'Referer': '{}/wager/CreateSports.aspx?WT=0',
                    'Connection': 'keep-alive',
                },
                "post_data": []
            },
            # "page_4": {
            #     "method": "post",
            #     "url": "{}/cog/GameSelection.asp?WTID=9&WCATID=1",
            #     "update_headers": {
            #         'Origin': '{}',
            #         'Accept-Encoding': 'gzip, deflate',
            #         'Accept-Language': 'en-US,en;q=0.9',
            #         'Upgrade-Insecure-Requests': '1',
            #         'Content-Type': 'application/x-www-form-urlencoded',
            #         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            #         'Cache-Control': 'max-age=0',
            #         'Referer': '{}/cog/sportselection.asp',
            #         'Connection': 'keep-alive',
            #     },
            #     "post_data": []
            # },
            # "page_5": {
            #     "method": "post",
            #     "url": "{}/cog/Wager.asp?WTID=9&WCATID=1&ls=1",
            #     "update_headers": {
            #         'Origin': '{}',
            #         'Accept-Encoding': 'gzip, deflate',
            #         'Accept-Language': 'en-US,en;q=0.9',
            #         'Upgrade-Insecure-Requests': '1',
            #         'Content-Type': 'application/x-www-form-urlencoded',
            #         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            #         'Cache-Control': 'max-age=0',
            #         'Referer': '{}/cog/GameSelection.asp?WTID=9&WCATID=1',
            #         'Connection': 'keep-alive',
            #     },
            #     "post_data": []
            # }

        }

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
        self.GAME_TYPES = dict(GAME_TYPES)
        self.GAME_INTERVALS = dict(GAME_INTERVALS)

        self.GAME_NAMES_MAP = {
            "MLB": {"GAME": "lg_5"},
            "NHL": {"GAME": "lg_7"}
        }

    def _validate_balance_page(self, soup_dom_object):
        """
        Validate the DOme Element of account balance page
        :return:
        """
        return_data = {"valid": True, "msg": ""}  # set the `True` value of `return_data` variable.
        balance = soup_dom_object.find("span", attrs={"id": "ctl00_WagerContent_AccountFigures1_lblCurrentBalance"})
        available_balance = soup_dom_object.find("span",
                                                 attrs={"id": "ctl00_WagerContent_AccountFigures1_lblRealAvailBalance"})
        if not balance:
            return_data.update({"valid": False,
                                "msg": "Not found balance "
                                       "span[id=ctl00_WagerContent_AccountFigures1_lblCurrentBalance]"})
        elif not available_balance:
            return_data.update({"valid": False,
                                "msg": "Not found available_balance span"
                                       "[id=ctl00_WagerContent_AccountFigures1_lblRealAvailBalance]"})
        return return_data

    def check_account_balance(self):
        """
        Check the account balance of the user

        Firstly its open the SITE["page_1"] using `get` method, For creating the cookies
        then its login the user
        """
        self.page_response = self.scrape_process.getPage()  # get account detail page
        soup = BeautifulSoup(self.page_response.text, 'lxml')

        valid_dict = self._validate_balance_page(soup)

        if valid_dict['valid']:
            balance = soup.find("span",
                                attrs={
                                    "id": "ctl00_WagerContent_AccountFigures1_lblCurrentBalance"
                                }).get_text(strip=True)
            available_balance = soup.find("span",
                                          attrs={
                                              "id": "ctl00_WagerContent_AccountFigures1_lblRealAvailBalance"
                                          }).get_text(strip=True)
            try:

                balance = int(balance.replace(",", ""))
                available_balance = int(available_balance.replace(",", ""))

                if available_balance <= 1:
                    self.set_message(True, ERROR_MSG.NOT_SUFFICAINT_BALANCE)



            except ValueError:
                self.set_message(True, ERROR_MSG.DOM_STRUCTURE_CHANGED, "Invalid balance about")
        else:
            self.set_message(True, ERROR_MSG.DOM_STRUCTURE_CHANGED, valid_dict['msg'])

    def site_login(self):
        """
        Login to the Site.

        Firstly its open the SITE["page_1"] using `get` method, For creating the cookies
        then its login the user
        """
        self.page_response = self.scrape_process.getPage()  # get first page to initialize the cookies and session

        post_data = {}
        soup = BeautifulSoup(self.page_response.text, 'lxml')
        form = soup.find("form", attrs={"name": "aspnetForm"})
        for input in form.find_all("input"):
            post_data.update({input['name']: input['value'] if input.has_attr('value') else ""})

        post_data.update({'ctl00$MainContent$ctlLogin$_UserName': self.credentialObject.username,
                          'ctl00$MainContent$ctlLogin$_Password': self.credentialObject.password})

        self.SITE_PAGES["page_2"]['post_data'] = [(key, value) for key, value in post_data.items()]

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
        form = soup_dom_object.find("form", attrs={"name": "aspnetForm"})
        if not form:
            return_data.update({"valid": False, "msg": "Not found form[name=aspnetForm]"})
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
        post_data = {}

        if valid_dict['valid']:
            form = soup.find("form", attrs={'name': 'aspnetForm'})
            for tag in form.find("input", attrs={'type': 'hidden'}):
                post_data.update({tag['name']: tag['value'] if tag.has_attr('value') else ''})

            game = self.GAME_TYPES[self.ModelObject.game_type]
            interval = self.GAME_INTERVALS[self.ModelObject.game_interval]

            if game in self.GAME_NAMES_MAP and interval in self.GAME_NAMES_MAP[game]:
                all_divs = [div for div in form.find_all("div", attrs={'class': 'dd_contentBottom'})
                            if div.find("input", attrs={'type': 'submit'})]

                for tag in all_divs:
                    prev_element = tag.find_previous_sibling("table")
                    elem = prev_element.find("input", attrs={"name": self.GAME_NAMES_MAP[game][interval]})
                    submit_elem = tag.find("input", attrs={'type': 'submit'})
                    if elem:
                        post_data.update({elem['name']: elem['value'] if elem.has_attr('value') else ""})
                        post_data.update(
                            {submit_elem['name']: submit_elem['value'] if submit_elem.has_attr('value') else ""})
                self.scrape_process.SITE_PAGES['page_4']["post_data"] = [(key, val) for key, val in post_data.items()]
            else:
                # game not found
                self.set_message(True, ERROR_MSG.GAME_NOT_FOUND)

        else:
            self.set_message(True, ERROR_MSG.DOM_STRUCTURE_CHANGED, valid_dict['msg'])

    def _validate_apply_bet_page(self, soup_dom_object):
        """
        Validate the "GameSelection" page.

        If page valid than it return `return_data['valid']=True`
        otherwise it return `return_data['valid']=False` and error msg
        :param soup_dom_object: DOM Object of BeautifulSoup
        :return return_data: Dictionary
        """
        return_data = {"valid": True, "msg": ""}  # set the `True` value of `return_data` variable.
        form = soup_dom_object.find("form", attrs={"name": "aspnetForm"})
        if not form:
            return_data.update({"valid": False, "msg": "Not found form[name=aspnetForm]"})
        else:
            table = None
            for tb in form.find_all('table'):
                if tb.find("tr", attrs={'class': 'GameBanner'}):
                    table = tb

            if not table:
                return_data.update({"valid": False, "msg": "Not found table that has tr[class=GameBanner]"
                                                           "(form[name=aspnetForm] > table tr[class=GameBanner])"})
        return return_data

    def apply_bet(self):
        """
        Apply the bet

        Check the betting pages and compare all values (incomingJuice, incomingLine, rotation and minimum amount)
        :return:
        """

        # create instance of the BeautifulSoup
        soup = BeautifulSoup(self.page_response.text, 'lxml')
        return_data = self._validate_apply_bet_page(soup)

        # check the DOM structure
        if not return_data['valid']:
            self.set_message(True, ERROR_MSG.DOM_STRUCTURE_CHANGED, return_data['msg'])
            return

        post_data = {}  # initialize post_data as dict
        incomingLineRS = -1000000000000000  # set default incoming Line
        incomingJuiceRS = -1000000000000000  # set default incoming Juice

        # set the all hidden and other input and select element  values in `post_data`
        form = soup.find("form", attrs={"name": "aspnetForm"})
        table = None
        for input_ele in form.find_all("input", attrs={"type": "hidden"}):
            post_data.update({input_ele['name']: input_ele['value'] if input_ele.has_attr('value') else ""})

        for input_ele in form.find_all("input", attrs={"type": "text"}):
            post_data.update({input_ele['name']: input_ele['value'] if input_ele.has_attr('value') else ""})

        for select_ele in form.find_all("select"):
            option = select_ele.find('option', attrs={'selected': True})
            if option:
                post_data.update({select_ele['name']: option['value'] if option.has_attr('value') else "0"})

        date = "{date:%b} {date.day}".format(date=self.ModelObject.bet_date)
        for tb in form.find_all('table'):
            if tb.find("tr", attrs={'class': 'GameBanner'}):
                table = tb

        row_elem = None

        for tr in table.find_all('tr'):
            tds = tr.find_all("td")

            date_td = tds[1] if tds and len(tds) >= 1 else None
            check_date = (date_td.get_text(strip=True) == date) if date_td else False

            check_rotation = (tds[2].get_text(strip=True) == self.ModelObject.rotation) if len(tds) >= 2 else False

            if check_date and check_rotation:
                row_elem = tr
                break
            else:
                next_sibling = tr.find_next_sibling('tr') if check_date and not check_rotation else None
                tds = next_sibling.find_all("td") if next_sibling else None
                check_rotation = (tds[2].get_text(strip=True) == self.ModelObject.rotation) if len(tds) >= 2 else False
                if check_rotation:
                    row_elem = tr
                    break
        if row_elem:
            selected_lines = {value: key for key, value in SELECTED_LINES}
            selected_line_index = {selected_lines["SPREAD"]: 4,
                                   selected_lines["TOTAL"]: 5,
                                   selected_lines['MONEY LINE']: 6}
            index = selected_line_index[self.ModelObject.selected_line] \
                if self.ModelObject.selected_line in selected_line_index else None

            if not index is None:
                tds = row_elem.find_all("td")
                element = tds[index]
                input_ele = element.findChild("input", attrs={'type': 'checkbox'})
                if input_ele and input_ele.has_attr("value"):
                    value = input_ele["value"]
                    context_list = value.replace("_", " ")
                    context_list = context_list.split(" ")[-2:]

                    for key, val in enumerate(context_list):
                        if val == "":
                            continue
                        # if val in FRACTION_VALUES:
                        #     fraction = FRACTION_VALUES[val] if (int(context_list[key - 1]) > 0) \
                        #         else -1 * FRACTION_VALUES[val]
                        #     if key == (len(context_list) - 1):
                        #         incomingJuiceRS = int(context_list[key - 1]) + fraction
                        #     else:
                        #         incomingLineRS = int(context_list[key - 1]) + fraction
                        if self.ModelObject.selected_line == selected_lines['MONEY LINE']:
                            incomingLineRS = 0
                            if key == (len(context_list) - 1) and incomingJuiceRS == -1000000000000000:
                                incomingJuiceRS = int(val)
                        else:
                            if key != (len(context_list) - 1) and incomingLineRS == -1000000000000000:
                                incomingLineRS = int(val)
                            else:
                                incomingJuiceRS = int(val)
                else:
                    # doesn't has  values
                    pass
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


class TdsevenwinSite(AnysportBetcatalinaSite):

    def crawling(self):
        try:
            game_types = self.GAME_TYPES
            game_interval = {key: value for key, value in GAME_INTERVALS}
            self.initial_validation(game_interval[self.ModelObject.game_interval],
                                    game_types[self.ModelObject.game_type])
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
