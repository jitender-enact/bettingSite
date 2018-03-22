from bet.scrapper.scrape_process import ScrapeProcess


class DiamondsSite:
    page_response = None
    SITE_PAGES = {
        "page_1": {
            "method": "get",
            "url": "http://diamondsb.ag/",
        },
        "page_2": {
            "method": "post",
            "url": "http://diamondsb.ag/Login.aspx",
            "update_headers": {
                'Origin': 'http://diamondsb.ag',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9',
                'Upgrade-Insecure-Requests': '1',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Cache-Control': 'max-age=0',
                'Referer': 'http://diamondsb.ag/Themes/Theme001/Styles/btb.css?v=23',
                'Connection': 'keep-alive',
            },
            "post_data": [
                ('txtAccessOfCode', ''),  # "wine108"
                ('txtAccessOfPassword', ''),  # "kt17"
            ]
        },
        "page_3": {
            "method": "get",
            "url": "",
            "update_headers": {
                'Origin': 'http://diamondsb.ag',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9',
                'Upgrade-Insecure-Requests': '1',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Referer': 'http://diamondsb.ag/client/bet-the-board.aspx',
                'Connection': 'keep-alive',
            }
        },
    }

    def __init__(self, biddingModel, credentialModel):

        """ Accept BiddingModel Object and CredentialModel object (login credentials for http://diamondsb.ag/) """

        # update the credentials
        self.SITE_PAGES["page_2"]['post_data'] = [('txtAccessOfCode', credentialModel.username),
                                                  ('txtAccessOfPassword', credentialModel.password)]

        self.scrape_process = ScrapeProcess(self.SITE_PAGES)  # create the ScrapeProcess object.
        self.page_response = None

    def siteLogin(self):

        """ Login to the http://diamondsb.ag/ Site """
        try:
            self.scrape_process.getPage()  # get first page to initialize the cookies and session
            self.scrape_process.nextPage()  # set next page
            self.page_response = self.scrape_process.getPage()  # login to site

        except Exception as e:

            # upnable to access site
            print("Unable to access the http://diamondsb.ag/ site")

    def selectGame(self):

        """ select game from 'page_response' object """
        pass

