# Use an official Python runtime as a parent image
FROM python:3.6-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

ENV TOKEN "xb-145318380262-GDqgBNxoaR0FazurLZi4lW4e"

CMD ["python3", "bot.py"]
