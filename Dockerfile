# Use the official Rasa Docker image as the base image
FROM rasa/rasa:3.6.20-full

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any additional dependencies if needed
# Uncomment and modify the following line if you have additional dependencies
# RUN pip install -r requirements.txt

# Switch to a non-root user
USER 1001

# Set the entrypoint to Rasa
ENTRYPOINT ["rasa"]