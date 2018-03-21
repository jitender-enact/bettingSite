import random
import os


class UserAgentRotator(object):
    """Create a random header from the proxy list

    Parameters
    ----------
    path: str
        path of the file, the user_agent delimiting the list by new line
    """

    def __init__(self, path='user_agent.txt'):
        if path == "user_agent.txt":
            dir_path = os.path.dirname(os.path.realpath(__file__))
            user_agent_path = "{dir_path}/{path}".format(dir_path=dir_path,
                                                         path=path)
        else:
            user_agent_path = path
        self.user_agents = self.__load_user_agents(path=user_agent_path)

    def __load_user_agents(self, path):
        user_agents = []
        with open(path) as file:
            user_agents = [str(line.strip()) for line in file]
        return user_agents

    def get_user_agent(self):
        return random.choice(self.user_agents)

    def generate_header(self):
        """
        Returns
        -------
        header: Dict[str]
            returns a dict with keys Connection and User-Agent
        """
        header = {
            "Connection": "close",
            "User-Agent": self.get_user_agent()
        }
        return header
