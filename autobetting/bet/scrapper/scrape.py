import requests
from bet.scrapper.agent_rotator import UserAgentRotator


class Scrapy:
    """
        Scrapy class use for creating and handling the session or cookies for request object.
    During initializing the Scrapy object a random user-agent set in request object.

    """

    session = None
    url = None
    user_agent = None

    def __init__(self, url=None, headers=None):
        self.url = url  # set url

        # set random user-agent
        self.user_agent = self.getUserAgent()

        self.headers = headers if headers else {}  # set headers
        self.session = requests.session()  # create request session

    @staticmethod
    def getUserAgent():
        user_agent = UserAgentRotator()
        return user_agent.get_user_agent()


    def setUrl(self, url):

        """ Method set the headers """
        self.url = url

    def setHeaders(self, **args):

        """ Method set the headers """
        self.headers = args

    def updateHeaders(self, **args):

        """ Method update the headers"""
        for key, val in args.items():
            self.headers[key] = val

    def getRequest(self, updateUserAgent=False):

        """ handle the get request of the requests object by setting the headers and url """

        # get user-agent
        user_agent_headers = {"User-Agent": self.getUserAgent() if updateUserAgent else self.user_agent}

        #update headers
        self.updateHeaders(**user_agent_headers)

        return self.session.get(self.url, headers=self.headers, cookies=self.session.cookies)

    def postRequest(self, data, updateUserAgent=False):

        """ handle the post request of the requests object by setting the headers, params and url """

        # get user-agent
        user_agent_headers = {"User-Agent": self.getUserAgent() if updateUserAgent else self.user_agent}

        # update headers
        self.updateHeaders(**user_agent_headers)

        return self.session.post(self.url, data=data, headers=self.headers, cookies=self.session.cookies)
