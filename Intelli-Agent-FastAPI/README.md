# 📧 Intelli-Agent-FastAPI: End-to-End Multi-Agent Email Automation System

<div align="center">
  <img src="./demo.gif" alt="Demo""/>
</div>

**Intelli-Agent-FastAPI** is a powerful, end-to-end multi-agent system designed for intelligent email automation. This project showcases a complete workflow from development to deployment, leveraging **FastAPI** for the backend, a multi-agent architecture for complex task handling, and **Docker** for seamless deployment.

## 🚀 Technical Deep Dive

This project is a complete ecosystem with a decoupled frontend and backend, orchestrated by a sophisticated multi-agent system.

### Backend (`/backend`)

The backend is a robust **FastAPI** application that serves as the core of the system.

- **API Routes**: The chat and agent interactions are managed through API routes defined in `backend/src/api/chat/routing.py`.
- **Database**: **PostgreSQL** is used for data persistence, with **SQLModel** for ORM operations. The database connection is managed in `backend/src/api/db.py`.
- **AI Services**: The AI logic is encapsulated in services that handle tasks like generating email messages. These services are defined in `backend/src/api/ai/services.py`.

### Frontend (`/gradio-ui`)

The user interface is built with **Gradio**, providing an intuitive way to interact with the multi-agent system.

- **UI Components**: The interface is defined in `gradio-ui/gradio_app.py` and includes text inputs for prompts, and outputs for the final response and generated email content.
- **API Interaction**: The Gradio app communicates with the FastAPI backend via HTTP requests, as seen in the `process_prompt` function.

### Deployment (`/compose.yaml`)

The entire application is containerized using **Docker**, making it easy to deploy and scale. The `compose.yaml` file defines the services for the backend, frontend, and database, and manages their networking and volumes.

---

## 🤖 Multi-Agent System

The intelligence of this project lies in its multi-agent architecture, which is designed to handle complex queries by breaking them down into smaller, manageable tasks.

### Agents

- **Supervisor Agent**: This is the master agent that routes tasks to the appropriate specialist agent. It is created in `backend/src/api/ai/agents.py`.
- **Research Agent**: This agent is responsible for conducting research based on a user's query. It uses the `research_email` tool to gather information.
- **Email Agent**: This agent takes the researched information and formats it into a well-structured email. It has access to the `send_me_email` tool to dispatch the email.

### Tools

The agents are equipped with a set of tools that allow them to perform specific actions:

- **`research_email`**: This tool, defined in `backend/src/api/ai/tools.py`, is used by the Research Agent to generate email content based on a query.
- **`send_me_email`**: This tool allows the Email Agent to send emails. It is also defined in `backend/src/api/ai/tools.py`.

---

## 🏁 Getting Started

To get the project up and running, you will need to have **Docker** and **Docker Compose** installed.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/eiliya-mohebi/ai-agents-cookbook/
    ```
2.  **Navigate to the project directory**:
    ```bash
    cd Intelli-Agent-FastAPI
    ```
3.  **Set up your environment variables**:
    -   Copy the `.env.sample` file to a new file named `.env` and update the values with your credentials.
4.  **Run the application**:
    ```bash
    docker-compose up -d --build
    ```
5.  **Access the application**:
    -   The **Gradio UI** will be available at [http://localhost:7860](http://localhost:7860).
    -   The **FastAPI backend** will be running at [http://localhost:8000](http://localhost:8000).

---

## ✨ Key Features

- **End-to-End System**: A complete, deployable application.
- **Multi-Agent Architecture**: Efficiently handles complex tasks by delegating to specialized agents.
- **Dockerized**: Easy to set up, deploy, and scale.
- **RESTful API**: A robust backend built with FastAPI.
- **Interactive UI**: An intuitive user interface built with Gradio.

---

## 🛠️ Technologies Used

-   **Backend**: FastAPI, Python, SQLModel
-   **Frontend**: Gradio
-   **Database**: PostgreSQL
-   **AI**: LangChain, LangGraph, OpenAI
-   **Deployment**: Docker, Docker Compose
