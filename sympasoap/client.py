from zeep.client import Client as ZeepClient, Settings as ZeepSettings

from sympasoap.lists import MailingList, MLUser

TOPICS = [
    "art",
    "business",
    "computers",
    "education",
    "entertainment",
    "government",
    "health",
    "news",
    "recreation",
    "science",
    "social",
    "society",
]

SUBTOPICS = [
    "art/finearts",
    "art/history",
    "art/literature",
    "art/photography",
    "business/b2b",
    "business/finance",
    "business/jobs",
    "business/shopping",
    "computers/games",
    "computers/hardware",
    "computers/internet",
    "computers/software",
    "education/college",
    "education/k12",
    "entertainment/humour",
    "entertainment/movies",
    "entertainment/music",
    "government/elections",
    "government/law",
    "government/military",
    "government/taxes",
    "health/diseases",
    "health/drugs",
    "health/fitness",
    "health/medicine",
    "news/multimedia",
    "news/newspapers",
    "news/radio",
    "news/tv",
    "recreation/autos",
    "recreation/outdoors",
    "recreation/sports",
    "recreation/travel",
    "science/animals",
    "science/astronomy",
    "science/engineering",
    "social/archaeology",
    "social/economics",
    "social/languages",
    "society/environment",
    "society/people",
    "society/religion",
]


class Client:
    def __init__(self, sympa_url: str):
        self.sympa_url = sympa_url
        self.zeep = ZeepClient(sympa_url + "/wsdl", settings=ZeepSettings(strict=False))

    def login(self, email: str, password: str) -> None:
        """
        Login into the API. Set a cookie for future connexions.
        """
        result = self.zeep.service.login(email, password)
        element = result._raw_elements[0]
        self.cookie = element.text
        self.zeep.settings.extra_http_headers = [("Cookie", f"sympa_session={element.text}")]
        if self.checkCookie() != email:
            # FIXME Better exception
            raise Exception("Unknown error: given cookie is invalid")
        print("Successfully authenticated!")

    def checkCookie(self) -> str:
        """
        From the current cookie, retrieve the email address.
        """
        result = self.zeep.service.checkCookie()
        element = result._raw_elements[0]
        return element.text

    def amI(self, mailing_list: str, function: str, email: str) -> bool:
        """
        Check if the given `email` is a member of type `function` in the `mailing_list`.
        The function parameter is one between subscriber, editor or owner.
        """
        if function not in ["subscriber", "editor", "owner"]:
            raise ValueError("function of a mailing list member must be subscriber, editor or owner.")
        result = self.zeep.service.amI(mailing_list, function, email)
        element = result._raw_elements[0]
        return element.text == "true"

    def review(self, mailing_list: str, full: bool = False) -> list:
        """
        Get the list of all subscribers of a list, including the administrators and the editors.
        If full=False, retrieve the list of email addresses only.
        If full=True, retrieve MLUser object, with the name of the user and the role.
        """
        if full:
            users = list()
            elements = self.zeep.service.fullReview(mailing_list)
            for element in elements:
                children = element.getchildren()
                kwargs = dict(mailing_list=mailing_list)
                for child in children:
                    tag = child.tag
                    if "gecos" in tag:
                        kwargs["name"] = child.text
                    elif "email" in tag:
                        kwargs["email"] = child.text
                    elif "isSubscriber" in tag:
                        kwargs["subscriber"] = child.text == "true"
                    elif "isEditor" in tag:
                        kwargs["editor"] = child.text == "true"
                    elif "isOwner" in tag:
                        kwargs["owner"] = child.text == "true"
                    else:
                        print("Unknown child tag:", tag)
                user = MLUser(**kwargs)
                users.append(user)
            return users
        return self.zeep.service.review(mailing_list)

    def lists(self, topic: str, subtopic: str) -> list:
        """
        Get all the (visible) lists that match the given topic and the given subtopic.
        See TOPICS and SUBTOPICS for valid topics and subtopics.
        """
        if topic not in TOPICS:
            raise ValueError(f"'{topic}' is not a valid topic.")
        if subtopic and f"{topic}/{subtopic}" not in SUBTOPICS:
            raise ValueError(f"'{topic}/{subtopic}' is not a valid subtopic.")
        result = self.zeep.service.lists(topic, subtopic)._value_1
        if result is None:
            return list()
        lists = list()
        for list_info in result:
            split = list_info.split(';')
            kwargs = dict()
            for data in split:
                key, value = data.split("=", 2)
                if key == "listAddress":
                    key = "list_address"
                kwargs[key] = value
            ml = MailingList(**kwargs)
            lists.append(ml)
        return lists

    def all_lists(self, subtopics: list = None):
        """
        Retrieve all lists that matches at least one subtopic in a given list.
        If the list is None, retrieve all existing lists.
        Warning: takes time because it is retriving the list for each topic.
        """
        if subtopics is None:
            subtopics = TOPICS + SUBTOPICS

        lists = list()

        for subtopic in list(subtopics):
            if "/" in subtopic:
                li = self.lists(subtopic.split("/")[0], subtopic.split("/")[1])
            else:
                li = self.lists(subtopic.split("/")[0], "")
            lists.extend(li)

        return lists
