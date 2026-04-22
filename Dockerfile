# Use this version of python image, slim strips unnecessary system packages
FROM python:3.10-slim

# Set the app dir as working directory, also create app dir if it doesn't exist 
WORKDIR /app

# Stops python from writing .pyc files, __pycache__ folders
ENV PYTHONDONTWRITEBYTECODE=1

# Forces python to flush output immediately, print statement and logs show up in real time, imp for debugging
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

# Copy requirements.txt file from our project folder to current working dir
COPY requirements.txt .

# Install dependencies without storing local cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy files and folders of our project to current working dir
COPY . .

# Signals this container expects to recieve traffic on 8000
EXPOSE 8000
