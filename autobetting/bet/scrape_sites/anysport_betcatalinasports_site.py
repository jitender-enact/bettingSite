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
                return_data.update({"valid": False, "msg": "Not found table[class=table_lines] "
                                                           "(form[name=lf] > table[class=table_lines])"})
            elif not table.find("td", attrs={"class": "trGameTime"}):
                return_data.update({"valid": False, "msg": "Not found td[class=trGameTime] (form[name=lf] > "
                                                           "table[class=table_lines] > td[class=trGameTime])"})
            elif not table.find("tr", attrs={"class": "trGameTime"}):
                return_data.update({"valid": False, "msg": "Not found tr[class=trGameTime] (form[name=lf] > "
                                                           "table[class=table_lines] > td[class=trGameTime] > "
                                                           "tr[class=trGameTime])"})
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
        form = soup.find("form", attrs={"name": "lf"})
        table = form.find("table", attrs={"class": "table_lines"})

        for input_ele in form.find_all("input", attrs={"type": "hidden"}):
            post_data.update({input_ele['name']: input_ele['value'] if input_ele.has_attr('value') else ""})

        for input_ele in form.find_all("input", attrs={"type": "text"}):
            post_data.update({input_ele['name']: input_ele['value'] if input_ele.has_attr('value') else ""})

        for select_ele in form.find_all("select"):
            option = select_ele.find('option', attrs={'selected': True})
            if option:
                post_data.update({select_ele['name']: option['value'] if option.has_attr('value') else "0"})

        date = "{date:%a} {date:%m}/{date.%d}".format(date=self.ModelObject.bet_date)

        game_element = None

        bet_date_games = []

        for row in table.find_all("tr"):
            tr = row.find("tr", attrs={"class": "trGameTime"})
            td = tr.findChild('td') if tr else None
            if td and date in td.get_text():

                # getting the next sibling element
                sibling = row.find_next_sibling("tr")

                # getting the rotation element
                rot = sibling.find("div", attrs={"class": "rot"}) \
                    if sibling and sibling.find("div", attrs={"class": "rot"}) else None

                game_element = sibling if rot and \
                                          rot.get_text(strip=True) == "{}".format(self.ModelObject.rotation) else None

                if not game_element and sibling.find_next_sibling("tr"):
                    # getting the next to next sibling element
                    next_sibling = sibling.find_next_sibling("tr")

                    # getting the rotation element
                    rot = next_sibling.find("div", attrs={"class": "rot"}) \
                        if next_sibling and next_sibling.find("div", attrs={"class": "rot"}) else None

                    game_element = next_sibling if rot and \
                                                   rot.get_text(strip=True) == "{}".format(
                        self.ModelObject.rotation) else None

                # if found the table row then break the loop
                if game_element:
                    break

        if game_element:
            tds = game_element.find_all("td")

            # td[5] = Spread Line, td[6] = Money Line, td[7] = Total Point, td[8] = Team total point
            selected_lines = {value: key for key, value in SELECTED_LINES}
            selected_line_index = {selected_lines["SPREAD"]: 1,
                                   selected_lines["TOTAL"]: 3,
                                   selected_lines['MONEY LINE']: 5,
                                   selected_lines["TEAM TOTAL"]: 7}

            index = selected_line_index[self.ModelObject.selected_line] \
                if self.ModelObject.selected_line in selected_line_index else None

            if not index is None:
                element = tds[index]
                input_ele = element.findChild("input", attrs={'type': 'text'})
                lable_ele = element.findChild("label")
                if input_ele:
                    context = lable_ele.get_text(strip=True)
                    context = context.replace(u'\xa0', " ")
                    context = context.replace("ov", "+")
                    context = context.replace("un", "-")
                    context_list = context.split(" ")

                    post_data.update({input_ele['name']: '{0:.2f}'.format(self.ModelObject.amount)})

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
