Python Sympa SOAP Wrapper
=========================

Small wrapper that uses [ZEEP](https://pypi.org/project/zeep/) to communicate with a SOAP endpoint linked to a Sympa
server, to let automation in lists creation.

Example
-------

Start by creating a new client, and log in.
Then, you can use some pre-constructed methods.

```python
from sympasoap import Client

client = Client("https://lists.example.com/sympa")
client.login("admin@example.com", "MY_STRONG_PASSWORD")     # Get from env

# Create a list of type hotline that is named automatically-created@lists.example.com with basic description
client.create_list(list_name="automatically-created", subject="Automatically created list", template="hotline",
        description="This mailing list was created from a Python shell.", topic="computers/software")

# Subscribe the email address toto@example.com with name "Toto TOTO" to the list automatically-created@lists.example.com
# in non-quiet mode: the user will receive a notification that they got subscribed
client.subscribe(email="toto@example.com", list_address="automatically-created", quiet=False, name="Toto TOTO")

# Unsubscribe the email in quiet mode
client.subscribe(email="toto@example.com", list_address="automatically-created", quiet=True)
```

Available functions
-------------------

```python
    def login(self, email: str, password: str) -> None:
        """
        Login into the API. Set a cookie for future connexions.
        """

    def check_cookie(self) -> str:
        """
        From the current stored cookie, retrieve the email address.
        """

    def is_subscriber(self, email: str, mailing_list: str, function: str = "subscriber") -> bool:
        """
        Check if the given `email` is a member of type `function` in the `mailing_list`.
        The function parameter is one between subscriber, editor or owner.
        """

    def get_subscribers(self, mailing_list: str, emails_only: bool = True) -> list:
        """
        Get the list of all subscribers of a list, including the administrators and the editors.
        If emails_only == True, retrieve the list of email addresses only.
        Else, retrieve MLUser object, with the name of the user and the role.
        """

    def lists(self, topic: str, subtopic: str) -> list:
        """
        Get all the (visible) lists that match the given topic and the given subtopic.
        See TOPICS and SUBTOPICS for valid topics and subtopics.
        """

    def all_lists(self) -> list:
        """
        Retrieve all lists.
        """

    def create_list(self, list_name: str, subject: str, template: str, description: str, topic: str,
                    use_custom_template: bool = False, raise_error: bool = True) -> bool:
        """
        Create a new mailing-list.
        """

    def delete_list(self, list_name: str, raise_error: bool = False) -> bool:
        """
        Close a mailing list.
        Warning: the list is not deleted in order to keep the history. Please use the web interface to fully
        delete the list.
        Well, the main reason is that the API does not provide a delete method.
        """

    def subscribe(self, email: str, list_address: str, quiet: bool, name: str = "", raise_error: bool = False) -> bool:
        """
        Subscribe the user with the given email to the given mailing list.
        If the quiet mode is enabled, the user won't receive a notification that they got subscribed.
        """

    def unsubscribe(self, email: str, list_address: str, quiet: bool, raise_error: bool = False) -> bool:
        """
        Subscribe the user with the given email to the given mailing list.
        If the quiet mode is enabled, the user won't receive a notification that they got subscribed.
        """
```
