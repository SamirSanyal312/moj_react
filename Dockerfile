# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV FLASK_APP=moj
ENV FLASK_ENV=development
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port for Flask
EXPOSE 5500

# Start the app
CMD ["sh", "./entrypoint.sh"]

