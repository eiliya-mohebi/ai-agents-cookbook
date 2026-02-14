import requests
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

API_BASE_URL = "http://127.0.0.1:8000/api/docs/"


def get_user_id(config: RunnableConfig):
    configurable = config.get("configurable") or config.get("metadata")
    user_id = configurable.get("user_id")
    if user_id is None:
        raise Exception("Invalid request for user.")
    return user_id


@tool
def search_query_documents(query: str, limit: int = 5, config: RunnableConfig = {}):
    """
    Search the most recent LIMIT documents for the current user.
    """
    user_id = get_user_id(config)
    params = {
        "search": query,
        "limit": limit if limit <= 25 else 25,
        "user_id": user_id,
    }

    try:
        response = requests.get(API_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", data) if isinstance(data, dict) else data

        return [{"id": item["id"], "title": item["title"]} for item in results]
    except Exception as e:
        return f"Error searching documents: {str(e)}"


@tool
def list_documents(limit: int = 5, config: RunnableConfig = {}):
    """
    List the most recent documents for the current user.
    """
    user_id = get_user_id(config)
    params = {"limit": limit if limit <= 25 else 25, "user_id": user_id}

    try:
        response = requests.get(API_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", data) if isinstance(data, dict) else data

        return [{"id": item["id"], "title": item["title"]} for item in results]
    except Exception as e:
        return f"Error listing documents: {str(e)}"


@tool
def get_document(document_id: int, config: RunnableConfig):
    """
    Get the details of a document.
    """
    user_id = get_user_id(config)
    params = {"user_id": user_id}

    try:
        response = requests.get(f"{API_BASE_URL}{document_id}/", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return "Document not found."
        return f"Error retrieving document: {str(e)}"


@tool
def create_document(title: str, content: str, config: RunnableConfig):
    """
    Create a new document.
    """
    user_id = get_user_id(config)
    payload = {"title": title, "content": content, "user_id": user_id}

    try:
        response = requests.post(API_BASE_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error creating document: {str(e)}"


@tool
def update_document(
    document_id: int,
    title: str = None,
    content: str = None,
    config: RunnableConfig = {},
):
    """
    Update a document.
    """
    user_id = get_user_id(config)
    payload = {"user_id": user_id}
    if title:
        payload["title"] = title
    if content:
        payload["content"] = content

    try:
        response = requests.patch(f"{API_BASE_URL}{document_id}/", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return "Document not found."
        return f"Error updating document: {str(e)}"


@tool
def delete_document(document_id: int, config: RunnableConfig):
    """
    Delete a document.
    """
    user_id = get_user_id(config)
    params = {"user_id": user_id}

    try:
        response = requests.delete(f"{API_BASE_URL}{document_id}/", params=params)
        response.raise_for_status()
        return {"message": "success"}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return "Document not found."
        return f"Error deleting document: {str(e)}"


document_tools = [
    create_document,
    list_documents,
    get_document,
    delete_document,
    update_document,
]
