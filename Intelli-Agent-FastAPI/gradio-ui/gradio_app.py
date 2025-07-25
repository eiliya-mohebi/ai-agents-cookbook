import gradio as gr
import requests
import json
import os
import textwrap
import time

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://backend:8000/api/chats/")


def process_prompt(prompt: str):
    start_time = time.time()

    yield "Thinking...", "Researching...", "Processing...", "Calculating..."

    if not prompt:
        duration = f"{time.time() - start_time:.2f} seconds"
        yield (
            "Please enter a prompt.",
            "Email content will appear here.",
            "{}",
            duration,
        )

    payload = {"message": prompt}
    headers = {"Content-Type": "application/json"}
    final_message, email_content, technical_details = "Error", "Error", "{}"

    try:
        response = requests.post(FASTAPI_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()

        response_data = response.json()

        final_message = (
            response_data.get("final_message") or "Could not extract the final message."
        )
        email_content = (
            response_data.get("email_content")
            or "No detailed email content was returned."
        )
        technical_details = json.dumps(response_data, indent=2)

    except requests.exceptions.RequestException as e:
        error_message = f"Error connecting to backend: {e}"
        final_message, email_content, technical_details = (
            error_message,
            error_message,
            error_message,
        )
    except json.JSONDecodeError:
        error_message = f"Error: Invalid JSON from server. Response: {response.text}"
        final_message, email_content, technical_details = (
            error_message,
            error_message,
            error_message,
        )

    duration = f"{time.time() - start_time:.2f} seconds"
    yield final_message, email_content, technical_details, duration


theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="sky",
).set(
    block_radius="8px",
)

css = """
:root {
    --text-lg: 1.1rem;
    --text-md: 1rem;
    --text-sm: 0.9rem;
}
.gradio-container {
    max-width: 1280px !important;
    margin: auto;
    background-color: #f0f2f6;
}
#tech-info-column {
    background-color: #e6e9f0;
    padding: 1.5rem;
    border-radius: 8px;
}
#time-output .svelte-cmf5p3 {
    font-size: 1.2rem !important;
    font-weight: bold;
    color: #1d4ed8;
}
"""

tech_info_markdown = textwrap.dedent("""
    ### ⚙️ Project Technical Info
    This UI interacts with a multi-agent backend system built with FastAPI and LangChain.

    **Core Components:**
    - **Supervisor Agent**: The main router that decides which specialist agent to use.
    - **Research Agent**: Uses tools to search for information.
    - **Email Agent**: Formats the research into an email.

    **Backend Stack:**
    - **Framework**: FastAPI
    - **AI Orchestration**: LangChain
    - **LLM**: GPT-4o-mini
    - **Database**: PostgreSQL

    ---
    *Developed by Eiliya Mohebi*
""")

with gr.Blocks(theme=theme, css=css) as demo:
    gr.Markdown("# 📧 AI Research & Email Agent")

    with gr.Row(equal_height=False):
        with gr.Column(scale=1, elem_id="tech-info-column"):
            gr.Markdown(tech_info_markdown)
            gr.Markdown("---")
            gr.Markdown("### ⏱️ Time Elapsed")
            time_output = gr.Markdown("0.00 seconds", elem_id="time-output")

        with gr.Column(scale=3):
            prompt_input = gr.Textbox(
                lines=3,
                label="Research Prompt",
                placeholder="e.g., Summarize the latest advancements in battery technology.",
            )
            submit_button = gr.Button("🚀 Generate & Email", variant="primary")

            gr.Markdown("## ✅ Final Confirmation")
            final_message_output = gr.Markdown(
                "The agent's final message will appear here..."
            )

            gr.Markdown("---")
            gr.Markdown("## ✉️ Generated Email Body")
            email_body_output = gr.Markdown(
                "The detailed email content will be displayed here."
            )

            with gr.Accordion("🛠️ Full API Response", open=False):
                technical_output = gr.Code(label="Full JSON Response", language="json")

    # Define the outputs list
    all_outputs = [
        final_message_output,
        email_body_output,
        technical_output,
        time_output,
    ]

    submit_button.click(fn=process_prompt, inputs=prompt_input, outputs=all_outputs)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
