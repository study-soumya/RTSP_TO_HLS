FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENV=1

# Install pkg-config and MySQL development libraries
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy the local code to the container image
COPY . /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Collect static files
RUN python3 manage.py collectstatic --noinput

# Expose port 8000
EXPOSE 8000

# Command to run Gunicorn
CMD ["gunicorn", "your_project.wsgi:application", "--bind", "0.0.0.0:8000"]
