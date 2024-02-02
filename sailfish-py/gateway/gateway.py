from __future__ import print_function
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container
from flask import Flask, request
import time
import socket

import os
import json

app = Flask(__name__)

"""
Proton event handler class
Demonstrates how to create an amqp connection and a sender to publish messages.
"""
class Send(MessagingHandler):
    def __init__(self, url, address, job, username, password, QoS=1):
        super(Send, self).__init__()

        # amqp broker host url
        self.url = url

        # target amqp node address
        self.address = address

        # authentication credentials
        self.username = username
        self.password = password

        # the message durability flag must be set to True for persistent messages
        self.message_durability = True if QoS==2 else False

        # messaging counters        
        self.sent = 0
        self.confirmed = 0
        self.total = len(job)
        self.job = job

    def on_start(self, event):
        # select connection authenticate
        if self.username:
            # creates and establishes an amqp connection with the user credentials
            conn = event.container.connect(url=self.url, 
                                           user=self.username, 
                                           password = self.password, 
                                           allow_insecure_mechs=True)
        else:
            # creates and establishes an amqp connection with anonymous credentials
            conn = event.container.connect(url=self.url)
        if conn:
            event.container.create_sender(conn, target=self.address)
            print("Connected")

    def on_sendable(self, event):
        while event.sender.credit and self.sent < self.total:
            # creates message to send
            msg = Message(id=(self.sent+1), 
                          body=self.job, 
                          durable=self.message_durability)
            # sends message
            print("Submitting Job")
            print(str(msg))
            event.sender.send(msg)
            self.sent += 1

    def on_accepted(self, event):
        self.confirmed += 1
        if self.confirmed == self.total:
            print("Job Submitted")
            event.connection.close()

    def on_rejected(self, event):
        self.confirmed += 1
        print("Broker", self.url, "Reject message:", event.delivery.tag)
        if self.confirmed == self.total:
            event.connection.close()

    # catches event for socket and authentication failures
    def on_transport_error(self, event):
        print("Transport error:", event.transport.condition)
        MessagingHandler.on_transport_error(self, event)

    def on_disconnected(self, event):
        if event.transport and event.transport.condition :
            print('disconnected with error : ', event.transport.condition)
            event.connection.close()

        self.sent = self.confirmed

@app.route('/jobs', methods=['POST'])
def post_job():
    print("READING ENV VARIABLES")
    username = os.getenv('AMQ_USER')
    password = os.getenv('AMQ_PASSWORD')
    host = os.getenv('HOST')
    port = int(os.getenv('QUEUE_PORT')) 
    url = f'amqp://{host}:{port}'
    
    job = request.get_json()

    print("Received Job:")
    print(job)

    while not check_amq_broker(host,port):
        print("Waiting for broker to scale up...")
        time.sleep(5)  # wait for 5 seconds before trying again

    print("Connected to broker, sending message...")
    
    time.sleep(5)
    Container(Send(url,"sailfishJob", job, username, password)).run()

    return "Success\n", 201


def check_amq_broker(host, port, timeout=5):
    """Check if the AMQ broker is up by attempting a socket connection."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            print("Connection to AMQ broker successful.")
            return True
    except socket.error as err:
        print(f"Failed to connect to AMQ broker: {err}")
    return False
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)