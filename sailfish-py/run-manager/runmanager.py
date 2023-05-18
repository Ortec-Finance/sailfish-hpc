from __future__ import print_function
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container
import os
import json


class Recv(MessagingHandler):
    def __init__(self, url, address, count, username, password):
        super(Recv, self).__init__()

        # amqp broker host url
        self.url = url

        # amqp node address
        self.address = address

        # authentication credentials
        self.username = username
        self.password = password
        
        # messaging counters
        self.expected = count
        self.received = 0

    def on_start(self, event):
        # select authentication options for connection
        if self.username:
            # basic username and password authentication
            conn = event.container.connect(url=self.url, 
                                           user=self.username, 
                                           password=self.password, 
                                           allow_insecure_mechs=True)
        else:
            # Anonymous authentication
            conn = event.container.connect(url=self.url)
        # create receiver link to consume messages
        if conn:
            event.container.create_receiver(conn, source=self.address)
            print("Listening to", self.address)

    def on_message(self, event):
        if event.message.id and event.message.id < self.received:
            # ignore duplicate message
            return
        if self.expected == 0 or self.received < self.expected:
            print(event.message.body)
            
            self.received += 1
            if self.received == self.expected:
                print('received all', self.expected, 'messages')
                tasks = event.message.body['Tasks']  # This is already a list of tasks
                
                print('Splitting job to tasks and sending them to sailfishTask Queue ')
                Container(Send(url,"sailfishTask", tasks, username, password)).run()
                event.receiver.close()
                event.connection.close()

    # the on_transport_error event catches socket and authentication failures
    def on_transport_error(self, event):
        print("Transport error:", event.transport.condition)
        MessagingHandler.on_transport_error(self, event)

    def on_disconnected(self, event):
        print("Disconnected")
        
"""
Proton event handler class
Demonstrates how to create an amqp connection and a sender to publish messages.
"""
class Send(MessagingHandler):
    def __init__(self, url, address, jobs, username, password, QoS=1):
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
        self.total = len(jobs)
        self.tasks = jobs

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
                          body=self.tasks[self.sent], 
                          durable=self.message_durability)
            # sends message
            print("Sending")
            print(str(msg))
            event.sender.send(msg)
            self.sent += 1

    def on_accepted(self, event):
        self.confirmed += 1
        if self.confirmed == self.total:
            print("all messages confirmed")
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


print("READING ENV VARIABLES")
username = os.getenv('AMQ_USER')
password = os.getenv('AMQ_PASSWORD')
host = os.getenv('HOST')
port = int(os.getenv('QUEUE_PORT')) 
url = f'amqp://{host}:{port}'


Container(Recv(url, "sailfishJob", 1, username, password)).run()