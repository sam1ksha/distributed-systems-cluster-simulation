FROM python:3.9-slim
WORKDIR /app
# Copy only the node.py file from the node_sim directory
COPY node.py .
RUN pip install requests
CMD ["python", "node.py", "default-node"]