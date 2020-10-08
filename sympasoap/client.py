from zeep.client import Client as ZeepClient, Settings as ZeepSettings
from zeep.exceptions import Fault

from .lists import MailingList, MLUser
from .constants import SUBTOPICS, TOPICS, TEMPLATES


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
                    use_custom_template: bool = False, raise_error: bool = True) -> bool:
        """
        Create a new mailing-list.
        """
        if topic not in TOPICS and topic not in SUBTOPICS:
            raise ValueError(f"Topic '{topic}' does not exist.")
        if template not in TEMPLATES and not use_custom_template:
            raise ValueError(f"Template '{template}' does not exist.")
        try:
            result = self.zeep.service.createList(list_name, subject, template, description, topic)
            return result._raw_elements[0].text == "true"
        except Fault as e:
            if raise_error:
                raise Fault(f"An unknown error occured while creating the list {list_name}. "
                            f"Maybe the list already exists?", e)
            else:
                return False

    def delete_list(self, list_name: str, raise_error: bool = False) -> bool:
        """
        Close a mailing list.
        Warning: the list is not deleted in order to keep the history. Please use the web interface to fully
        delete the list.
        Well, the main reason is that the API does not provide a delete method.
        """
        try:
            result = self.zeep.service.closeList(list_name)
            return result._raw_elements[0].text == "true"
        except Fault as e:
            if raise_error:
                raise Fault(f"An unknown error occured while deleting the list {list_name}. "
                            f"Maybe the list did not exist?", e)
            else:
                return False

    def subscribe(self, email: str, list_address: str, quiet: bool, name: str = "", raise_error: bool = False) -> bool:
        """
        Subscribe the user with the given email to the given mailing list.
        If the quiet mode is enabled, the user won't receive a notification that they got subscribed.
        """
        try:
            result = self.zeep.service.add(list_address, email, name, quiet)
            return result._raw_elements[0].text == "true"
        except Fault as e:
            if raise_error:
                raise Fault(f"An unknown error occured while subscribing to the list {list_address}. "
                            f"Maybe the user is already a member?", e)
            else:
                return False

    def unsubscribe(self, email: str, list_address: str, quiet: bool, raise_error: bool = False) -> bool:
        """
        Subscribe the user with the given email to the given mailing list.
        If the quiet mode is enabled, the user won't receive a notification that they got subscribed.
        """
        try:
            # del is a reserved keyword
            result = getattr(self.zeep.service, "del")(list_address, email, quiet)
            return result._raw_elements[0].text == "true"
        except Fault as e:
            if raise_error:
                raise Fault(f"An unknown error occured while subscribing to the list {list_address}. "
                            f"Maybe the user is already a member?", e)
            else:
                return False
