from __future__ import print_function
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container
import os
import json
import sys

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
        
        print("Listener initialized")

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
        print("Message Retrieved")
        if event.message.id and event.message.id < self.received:
            # ignore duplicate message
            return
        if self.expected == 0 or self.received < self.expected:
            print(event.message.body)
            
            self.received += 1
            if self.received == self.expected:
                print('received all', self.expected, 'messages')
                print('Computing task:', event.message.body['ID'])

                number = int(event.message.body['Number'])
                print("Computing the Factorial of", number)

                print("The factorial of", number, "is:", self.highly_inefficient_factorial(number))

                print("Computation completed")
                event.receiver.close()
                event.connection.close()

    # the on_transport_error event catches socket and authentication failures
    def on_transport_error(self, event):
        print("Transport error:", event.transport.condition)
        MessagingHandler.on_transport_error(self, event)

    def on_disconnected(self, event):
        print("Disconnected")

    def highly_inefficient_factorial(self,n):
        if n == 0:
            return 1
        else:
            result = 1
            for i in range(n):
                result *= self.highly_inefficient_factorial(i)
            return result

sys.setrecursionlimit(2147483646)
print("READING ENV VARIABLES")
username = os.getenv('AMQ_USER')
password = os.getenv('AMQ_PASSWORD')
host = os.getenv('HOST')
port = int(os.getenv('QUEUE_PORT')) 
url = f'amqp://{host}:{port}'


Container(Recv(url, "sailfishTask", 1, username, password)).run()