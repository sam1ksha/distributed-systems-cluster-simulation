FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install requests==2.25.0

# Copy the node script
COPY node.py .

# Default command - will be overridden by docker run
CMD ["python", "node.py"]
