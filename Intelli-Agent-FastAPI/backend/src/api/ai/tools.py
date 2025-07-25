from langchain_core.tools import tool

from api.emailer.sender import send_mail
from api.ai.services import generate_email_message


@tool
def send_me_email(subject: str, content: str) -> str:
    """
    Send an email to myself with a subject and content.

    Arguments:
    - subject: str - Text subject of the email
    - content: str - Text body content of the email
    """
    try:
        send_mail(subject=subject, content=content)
    except:
        return "Email not successfully sent"
    return "Email successfully sent"


@tool
def research_email(query: str):
    """
    Perform research based on the query

    Arguments:
    - query: str - Topic of research
    """
    response = generate_email_message(query=query)
    msg = f"Subject {response.subject}:\nBody: {response.content}"
    return msg
