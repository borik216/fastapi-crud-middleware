FROM python:3.11-slim

# 1. Set the anchor point
WORKDIR /code

# 2. Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy your code into the container (for production)
COPY . .

# 4. Tell Python where to look
ENV PYTHONPATH=/code

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]