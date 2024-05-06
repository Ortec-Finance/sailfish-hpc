# Use Red Hat's Universal Base Image 8 (UBI 8) as the base
FROM registry.access.redhat.com/ubi8/ubi:latest

RUN yum install -y gcc-c++ make cmake python3-devel libuuid-devel && yum clean all

# Install Python 3 and pip
RUN dnf install -y python38 python38-pip && \
    dnf clean all && \
    alternatives --set python /usr/bin/python3 && \
    pip3 install --upgrade pip setuptools

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container
COPY . .

# Set the Python path to include /app
ENV PYTHONPATH=/app:${PYTHONPATH}
ENV PYTHONUNBUFFERED=1

# Run the command you want to start your app
CMD ["python3", "app.py"]
