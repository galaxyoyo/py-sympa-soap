class MailingList:
    homepage: str
    list_address: str
    subject: str

    def __init__(self, homepage="", list_address="", subject=""):
        self.homepage = homepage
        self.list_address = list_address
        self.subject = subject

    def __str__(self):
        return f"Mailing-list {self.list_address}"

    def __repr__(self):
        return str(self.__dict__)


class MLUser:
    editor: bool
    email: str
    owner: bool
    mailing_list: str
    name: str
    subscriber: bool

    def __init__(self, editor=False, email="", owner=False, mailing_list="", name="", subscriber=False):
        self.editor = editor
        self.email = email
        self.owner = owner
        self.mailing_list = mailing_list
        self.name = name
        self.subscriber = subscriber

    def __str__(self):
        return f"ML subscription for email {self.email} in the list {self.mailing_list}"

    def __repr__(self):
        return str(self.__dict__)
