FROM python:3.11-bullseye

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir dspy==2.6.27

# Copy the test script
COPY test_memory_leak.py .

# Run the test
CMD ["python", "-u", "test_memory_leak.py"]