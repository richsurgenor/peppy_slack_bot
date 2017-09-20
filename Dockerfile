# Use an official Python runtime as a parent image
FROM python:3.6-slim

# Set this environment variable to true to set timezone on container start.
ENV SET_CONTAINER_TIMEZONE true

# Default container timezone as found under the directory /usr/share/zoneinfo/.
ENV CONTAINER_TIMEZONE America/Chicago

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

RUN chmod +x ./startup.sh
RUN ./startup.sh

ENV TOKEN "xb-145318380262-GDqgBNxoaR0FazurLZi4lW4e"
CMD ["python3", "bot.py"]
