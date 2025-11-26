# Use a Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt


# Copy the agent code
COPY . .

# Expose the port the agent will run on
EXPOSE 3232

# Command to run the agent
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3232"]
