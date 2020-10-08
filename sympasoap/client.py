from zeep.client import Client as ZeepClient, Settings as ZeepSettings
from zeep.exceptions import Fault

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

TEMPLATES = [
    "confidential",
    "discussion_list",
    "hotline",
    "html-news-letter",
    "intranet_list",
    "news-letter",
    "private_working_group",
    "public_web_forum",
]


class Client:
    def __init__(self, sympa_url: str):
        self.sympa_url = sympa_url
        self.zeep = ZeepClient(sympa_url + "/wsdl", settings=ZeepSettings(strict=False))
        self.cookie = None

    def login(self, email: str, password: str) -> None:
        """
        Login into the API. Set a cookie for future connexions.
        """
        result = self.zeep.service.login(email, password)
        element = result._raw_elements[0]
        self.cookie = element.text
        self.zeep.settings.extra_http_headers = [("Cookie", f"sympa_session={element.text}")]
        if self.check_cookie() != email:
            # FIXME Better exception
            raise Exception("Unknown error: given cookie is invalid")
        self.email = email
        print("Successfully authenticated!")

    def logout(self):
        """
        Clear cookie
        """
        self.cookie = None
        self.email = None
        self.zeep.settings.extra_http_headers = []

    def check_cookie(self) -> str:
        """
        From the current cookie, retrieve the email address.
        """
        result = self.zeep.service.checkCookie()
        element = result._raw_elements[0]
        return element.text

    def is_subscriber(self, email: str, mailing_list: str, function: str = "subscriber") -> bool:
        """
        Check if the given `email` is a member of type `function` in the `mailing_list`.
        The function parameter is one between subscriber, editor or owner.
        """
        if function not in ["subscriber", "editor", "owner"]:
            raise ValueError("function of a mailing list member must be subscriber, editor or owner.")
        result = self.zeep.service.amI(mailing_list, function, email)
        element = result._raw_elements[0]
        return element.text == "true"

    def get_subscribers(self, mailing_list: str, emails_only: bool = True) -> list:
        """
        Get the list of all subscribers of a list, including the administrators and the editors.
        If emails_only == True, retrieve the list of email addresses only.
        Else, retrieve MLUser object, with the name of the user and the role.
        """
        if not emails_only:
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

    def all_lists(self) -> list:
        """
        Retrieve all lists.
        """
        elem = self.zeep.service.complexLists()._raw_elements[0]
        lists = list()
        for list_info in elem.getchildren():
            kwargs = dict()
            for child in list_info.getchildren():
                if "listAddress" in child.tag:
                    key = "list_address"
                elif "subject" in child.tag:
                    key = "subject"
                elif "homepage" in child.tag:
                    key = "homepage"
                else:
                    raise ValueError(f"Tag {child.tag} is unknown")
                kwargs[key] = child.text
            ml = MailingList(**kwargs)
            lists.append(ml)
        return lists

    def create_list(self, list_name: str, subject: str, template: str, description: str, topic: str,
                    use_custom_template: bool = False) -> bool:
        if topic not in TOPICS and topic not in SUBTOPICS:
            raise ValueError(f"Topic '{topic}' does not exist.")
        if template not in TEMPLATES and not use_custom_template:
            raise ValueError(f"Template '{template}' does not exist.")
        try:
            result = self.zeep.service.createList(list_name, subject, template, description, topic)
            return result._raw_elements[0].text == "true"
        except Fault:
            raise Fault(f"An unknown error occured while creating the list {list_name}. Maybe the list already exists?")
