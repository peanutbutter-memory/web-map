FROM python:3.11-slim-bookworm

# rasterio requires libexpat1
RUN apt-get update && apt-get install -y libexpat1

# Set the working directory in the container
RUN mkdir app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

COPY . /app

CMD ["python", "app.py"]
