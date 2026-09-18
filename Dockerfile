FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# In a container we must bind to all interfaces and not open a browser.
ENV HOST=0.0.0.0 \
    PORT=5000 \
    HREA_OPEN_BROWSER=0

EXPOSE 5000

CMD ["python", "app.py"]
