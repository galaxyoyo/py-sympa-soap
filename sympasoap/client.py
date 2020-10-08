from zeep.client import Client as ZeepClient, Settings as ZeepSettings

from sympasoap.subscribers import MLUser


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
