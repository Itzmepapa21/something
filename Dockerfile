# Stage 1: Build environment with Telethon and dependencies
FROM python:3.9-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your bot code
COPY . .

# Stage 2: Final image with minimal dependencies
FROM python:3.9-slim

WORKDIR /app

COPY --from=builder /app/your_bot_script.py .

# Entrypoint to run your bot script
CMD ["python", "your_bot_script.py"]
