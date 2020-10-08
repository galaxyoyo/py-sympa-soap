from zeep.client import Client as ZeepClient, Settings as ZeepSettings


class Client:
    def __init__(self, sympa_url: str):
        self.sympa_url = sympa_url
        self.zeep = ZeepClient(sympa_url + "/wsgl", settings=ZeepSettings(strict=False))

    def login(self, email, password):
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

    def checkCookie(self):
        """
        From the current cookie, retrieve the email address.
        """
        result = self.zeep.service.checkCookie()
        element = result._raw_elements[0]
        return element.text
