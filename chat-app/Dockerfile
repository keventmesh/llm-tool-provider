FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

EXPOSE 8000

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["chainlit", "run", "chat.py"]
