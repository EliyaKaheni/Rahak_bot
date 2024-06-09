# Use the official Python 3.12 image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY req.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r req.txt

# Copy the rest of the application code into the container
COPY BotRahak.py .
COPY Mooshak.csv .
COPY Charkhak.csv .

# Set the command to run the bot
CMD ["python", "BotRahak.py"]
