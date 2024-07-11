FROM python

# Install the OpenShift CLI
RUN curl -s https://mirror.openshift.com/pub/openshift-v4/clients/ocp/4.12.53/openshift-client-linux.tar.gz | \
    tar xz -C /usr/local/bin oc kubectl && \
    oc version

# Set a working directory
WORKDIR /workspace

# Copy the requirements.txt file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

RUN apt-get update
RUN apt-get -qq -y install pv

ENV SHELL /bin/bash

CMD ["/bin/bash"]