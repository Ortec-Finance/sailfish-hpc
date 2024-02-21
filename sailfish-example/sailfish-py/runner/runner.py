from __future__ import print_function
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container
import os
import json
import sys

class TxRecv(MessagingHandler):
    def __init__(self, url, address, count, username, password):
        super(TxRecv, self).__init__(prefetch=0, auto_accept=False)

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
        self.committed = 0
        print("Listener initialized")

    def on_transaction_declared(self, event):
        self.receiver.flow(self.expected)
        self.transaction = event.transaction

    def on_transaction_committed(self, event):
        self.committed += self.expected
        if self.expected == 0 or self.committed < self.expected:
            self.container.declare_transaction(self.conn, handler=self)
        else:
            event.connection.close()

    def on_start(self, event):
        # select authentication options for connection
        self.container = event.container
        if self.username:
            # basic username and password authentication
            self.conn = self.container.connect(url=self.url, 
                                           user=self.username, 
                                           password=self.password, 
                                           allow_insecure_mechs=True)
        else:
            # Anonymous authentication
            self.conn = self.container.connect(url=self.url)
        # create receiver link to consume messages
        if self.conn:
            self.receiver = self.container.create_receiver(self.conn, source=self.address)
            print("Listening to", self.address)
            self.container.declare_transaction(self.conn, handler=self)
            self.transaction = None


    def on_message(self, event):
        print("Message Retrieved")
        if event.message.id and event.message.id < self.received:
            # ignore duplicate message
            return
        if self.expected == 0 or self.received < self.expected:
            print(event.message.body)
            self.receiver.flow(self.expected)
            self.transaction.accept(event.delivery)

            self.received += 1
            if self.received == self.expected:
                self.transaction.commit()
                self.transaction = None 
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


Container(TxRecv(url, "sailfishTask", 1, username, password)).run()