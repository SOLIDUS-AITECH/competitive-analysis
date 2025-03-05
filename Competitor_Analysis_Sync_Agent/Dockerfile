# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory to /
WORKDIR /

# Copy the requirements file into the container and install dependencies
COPY Competitor_Analysis_Sync_Agent/requirements.txt Competitor_Analysis_Sync_Agent/requirements.txt

RUN pip install --no-cache-dir -r Competitor_Analysis_Sync_Agent/requirements.txt

# Copy the rest of the application files into the container
COPY . .

# Set the default port to 3000 (can be overridden by passing a different PORT env var at runtime)
ENV PORT=3000

# Expose port 3000 (Note: if you override PORT during runtime, update the exposed port accordingly)
EXPOSE 3000

# Run the application
CMD ["python", "Competitor_Analysis_Sync_Agent/run.py"]
