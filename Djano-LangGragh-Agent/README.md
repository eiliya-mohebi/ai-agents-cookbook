# Django LangGraph AI Agent

This project is a Django-based backend that integrates a **LangGraph** agent to manage and interact with documents via a REST API. The agent uses OpenAI (via AvalAI) to search, create, and retrieve document information based on natural language prompts.

## 🚀 Features

* **AI-Powered Document Management**: Uses a ReAct agent built with LangGraph to handle CRUD operations on documents.
* **RESTful API**: Built with Django Rest Framework (DRF) for document management and agent interaction.
* **Integrated AI Tools**: Custom tools allow the agent to:
    * List recent documents.
    * Search documents by title or content.
    * Retrieve specific document details.
    * Create new documents.
    * Update or delete existing ones.
* **API Documentation**: Automatic Swagger and Redoc documentation using `drf-spectacular`.

## 🛠️ Project Structure

* `src/ai/`: Contains the LangGraph agent logic, LLM configurations, and specialized tools.
* `src/documents/`: Django app managing the `Document` model, serializers, and ViewSets.
* `src/backend/`: Project configuration, settings, and URL routing.

## ⚙️ Setup & Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/eiliya-mohebi/ai-agents-cookbook
    cd Djano-LangGragh-Agent/src
    ```

2.  **Environment Variables**:
    Create a `.env` file in the `src/` directory and configure your keys:
    ```env
    OPENAI_API_KEY = "YOUR_API_KEY"
    OPENAI_BASE_URL = "https://api.avalai.ir/v1"
    ORS_API_KEY = "your-django-secret-key"
    ```

3.  **Install Dependencies**:
    Ensure you have Python 3.10+ installed, then install the required packages:
    ```bash
    pip install django djangorestframework langgraph langchain-openai python-decouple drf-spectacular requests
    ```

4.  **Database Migration**:
    ```bash
    python manage.py migrate
    ```

5.  **Run the Server**:
    ```bash
    python manage.py runserver
    ```

## 🤖 AI Agent Implementation

The agent is defined in `src/ai/agents.py` and uses a ReAct pattern. It is equipped with tools from `src/ai/tools/documents.py` that communicate with the local API endpoints to manage documents.

### Available AI Tools:
* `list_documents`: Returns the most recent documents for the authenticated user.
* `search_query_documents`: Searches documents by query string.
* `get_document`: Retrieves details for a specific document ID.
* `create_document`: Creates a new document with a title and content.

## 📡 API Endpoints

### Documents CRUD
* `GET /api/docs/`: List documents (supports `user_id` filtering and searching).
* `POST /api/docs/`: Create a new document.
* `GET /api/docs/{id}/`: Retrieve document details.

### AI Agent Chat
* `POST /api/agent/chat/`: Send a natural language prompt to the agent.
    * **Payload**: `{"prompt": "Search for my machine learning documents"}`.

### Documentation
* **Swagger UI**: `/api/schema/swagger-ui/`.
* **Redoc**: `/api/schema/redoc/`.

## 🧪 Database Schema

The system uses a SQLite database with the following primary `Document` fields:
* `owner`: Reference to the `auth_user`.
* `title`: Document title.
* `content`: Main text body.
* `active`: Boolean flag for soft-deletion.
* `created_at` / `updated_at`: Timestamps.