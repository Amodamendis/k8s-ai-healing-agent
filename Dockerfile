FROM python:3.12-slim

WORKDIR /app

# Copy dependency definition
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and prompts
COPY src/ ./src/
COPY prompts/ ./prompts/

# Run the agent module
CMD ["python", "-m", "src.main"]