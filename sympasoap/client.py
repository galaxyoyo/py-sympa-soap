from zeep.client import Client as ZeepClient, Settings as ZeepSettings


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
