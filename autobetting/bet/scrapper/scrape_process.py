from bet.scrapper.scrape import Scrapy


class ScrapeProcess:
    """
        ScrapeProcess, initialize the Scrapy object and process each pages and return its response.

        For processing the pages its use same Scrapy object to maintain the session and cookies.
        During initializing the ScrapeProcess object its accept 'site_pages' (dictionary).

        Format of 'site_pages'
        ----------------------

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
                    ('txtAccessOfCode', 'wine108'),
                    ('txtAccessOfPassword', 'kt17'),
                ]
            }
        }


    """
    def __init__(self, site_pages):

        """ Create Scrapy Object and set 'site_pages' and current_page """
        self.SITE_PAGES = site_pages
        self.scrapy = self.createScrapyObject()  # create Scarpy Object
        self.current_page = 1
        self.method = 'get'

    def nextPage(self):

        """ Increment the current_page value by 1 and update current_page value."""
        self.current_page += 1

    def createScrapyObject(self):

        """ Create and Return the Scrapy Object"""
        return Scrapy()

    def configureScrapyObject(self, obj):

        """ Configured the Scrapy objects by given 'site_pages' value."""
        if ('url' in obj) and obj["url"] and ('method' in obj) and (obj["method"].lower() in ["get", "post"]):
            self.scrapy.setUrl(obj["url"])

            self.method = obj["method"].lower()
            if ("set_headers" in obj) and obj['set_headers']:
                self.scrapy.setHeaders(**obj['set_headers'])
            if ("update_headers" in obj) and obj['update_headers']:
                self.scrapy.setHeaders(**obj['update_headers'])

    def getPage(self, updateUserAgent=False):

        """ Return the current page response. """
        page = "page_{}".format(self.current_page)
        obj = self.SITE_PAGES[page]
        self.configureScrapyObject(obj)

        if (self.method == 'get'):
            return self.scrapy.getRequest(updateUserAgent)

        elif (self.method == 'post'):
            if ("post_data" in obj) and obj['post_data']:
                return self.scrapy.postRequest(data=obj['post_data'], updateUserAgent=updateUserAgent)
