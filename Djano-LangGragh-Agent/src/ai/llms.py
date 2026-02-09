from django.conf import settings
from langchain_openai import ChatOpenAI


def get_openai_api_key():
    return settings.OPENAI_API_KEY


def get_base_url():
    return settings.OPENAI_BASE_URL


def get_openai_model(model="gpt-4o-mini"):
    if model is None:
        model = "gpt-4o-mini"
    return ChatOpenAI(
        model=model,
        temperature=0,
        max_retries=2,
        api_key=get_openai_api_key(),
        base_url=get_base_url(),
    )
