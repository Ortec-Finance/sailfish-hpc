from __future__ import print_function
from proton import Delivery,Message

from proton.handlers import MessagingHandler
from proton.reactor import Container
import os
import json
import sys
import time
import random
import sys

class Recv(MessagingHandler):
    def __init__(self, url, address, max_batch_count, username, password, timeout=60):
        super(Recv, self).__init__(prefetch=0, auto_accept=False)
        self.url = url
        self.address = address
        self.username = username
        self.password = password
        
        self.max_batch_count = max_batch_count
        self.received = 0
        self.committed = 0
        self.current_batch = 0
        self.timeout = timeout
        print("Listener initialized")

    def on_timer_task(self, event):
        print("No Message Received within Timeout. Terminating process.")
        if self.receiver:
            self.receiver.close()
        if self.conn:
            self.conn.close()
        sys.exit(0)

    def on_start(self, event):
        self.timer = event.reactor.schedule(self.timeout, self)
        self.container = event.container
        self.conn = self.container.connect(url=self.url, user=self.username, password=self.password, allow_insecure_mechs=True) if self.username else self.container.connect(url=self.url)
        if self.conn:
            self.receiver = self.container.create_receiver(self.conn, source=self.address)
            self.receiver.flow(self.max_batch_count)
            print("Listening to", self.address)

             
    def on_message(self, event):
        print("Message Retrieved")
        print(event.message.body)
        self.timer.cancel()
        self.current_batch = 1
        
        # Accept the message before processing so other workers don't compute the same message
        event.delivery.update(Delivery.ACCEPTED)
        
        print("Processing")
        self.process_message(event.message)

        # Update counters and reschedule timer
        self.received += 1
        event.connection.close()
        
    def on_transport_error(self, event):
        print("Transport error:", event.transport.condition)
        MessagingHandler.on_transport_error(self, event)

    def on_disconnected(self, event):
        self.current_batch = 0
        print("Disconnected")

    def process_message(self, message):
        print('Processing message:', message.body['ID'])
        number = int(message.body['Number'])
        print("Computing the Factorial of", number)
        
        # Add a random delay between 1 and 5 seconds
        delay = random.uniform(1, 5)
        time.sleep(delay)
        
        result = self.highly_inefficient_factorial(number)
        print("The factorial of", number, "is:", result)

    def highly_inefficient_factorial(self, n):
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
recvQueue = os.getenv('AMQ_RECV_QUEUE', 'sailfishTask')

host = os.getenv('HOST')
port = int(os.getenv('QUEUE_PORT'))
timeout = int(os.getenv('SELF_TERMINATION_TIMEOUT_SECONDS', 60))

url = f'amqp://{host}:{port}'
iteration = 0

print("Worker Configuration:")
print("Connection to Broker: ", url)
print("Will terminate in ", timeout, " seconds if no message is received.")

while True:
    iteration +=1
    print("Compute Iteration: ", iteration)
    Container(Recv(url, recvQueue, 1, username, password, timeout)).run()
    
