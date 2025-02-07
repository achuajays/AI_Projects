# Use an official Python runtime as a parent image
FROM python:3.11
# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first (to leverage caching)
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the port FastAPI runs on

CMD ["python", "caption_hashtag_recommender.py"]