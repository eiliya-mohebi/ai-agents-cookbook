FROM python:latest

WORKDIR /app

RUN python -m venv /opt/venv/
ENV PATH=/opt/venv/bin:$PATH

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY gradio_app.py .

CMD ["python", "gradio_app.py"]
