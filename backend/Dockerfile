FROM python:3.11-slim

WORKDIR /app

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

# Upgrade pip inside venv and install dependencies
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# fixed
RUN pip install mysql-connector

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]