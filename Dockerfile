FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENV=1

# Work Directory
WORKDIR /app

# Copy the local code to the container image
COPY . /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py collectstatic --noinput
# Expose port 8000
EXPOSE 8000
