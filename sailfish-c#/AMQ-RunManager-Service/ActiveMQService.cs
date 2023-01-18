using ActiveMQ.Artemis.Client;
using ActiveMQ.Artemis.Client.Transactions;
using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
namespace RNMartingaleCloudApp
{
    public class ActiveMQService : IQueueService
    {

        private string Host = Environment.GetEnvironmentVariable("HOST") ?? "0";
        private string Port = Environment.GetEnvironmentVariable("QUEUE_PORT") ?? "0";
        private string User = Environment.GetEnvironmentVariable("USER") ?? "0";
        private string Password = Environment.GetEnvironmentVariable("PASSWORD") ?? "0";
        private string TaskAddress = Environment.GetEnvironmentVariable("TASK_ADDRESS") ?? "0";
        private string ResultAddress = Environment.GetEnvironmentVariable("RESULT_ADDRESS") ?? "0";
        private string JobAddress = Environment.GetEnvironmentVariable("JOB_ADDRESS") ?? "0";
        private string Timeout = Environment.GetEnvironmentVariable("TIMEOUT") ?? "0";

        public async Task AddTaskAsync(List<string> tasks, string id)
        {
            var connectionFactory = new ConnectionFactory();
            var endpoint = Endpoint.Create(Host, Convert.ToInt32(Port), User, Password);
            IConnection connection = await connectionFactory.CreateAsync(endpoint);

            IProducer producer = await connection.CreateProducerAsync(TaskAddress, RoutingType.Anycast);

            foreach (string task in tasks)
            {
                Message message = new Message(task);

                message.MessageId = Guid.NewGuid().ToString();
                message.GroupId = message.MessageId;
                message.ApplicationProperties["ComputationID"] = id;
                Console.WriteLine($"[{DateTime.Now}] Added a task {id}");
                await producer.SendAsync(message);
            }
            await connection.DisposeAsync();
        }

        public async Task<(IConsumer, Message)> ConsumeJobAsync()
        {
            var connectionFactory = new ConnectionFactory();
            var endpoint = Endpoint.Create(Host, Convert.ToInt32(Port), User, Password);

            Console.WriteLine($"[{DateTime.Now}] Created endpoint {endpoint}");
            IConnection connection = await connectionFactory.CreateAsync(endpoint);
            Console.WriteLine($"[{DateTime.Now}] Opened connection {connection}");


            var consumer = await connection.CreateConsumerAsync(new ConsumerConfiguration
            {
                Address = JobAddress,
                RoutingType = RoutingType.Anycast,
                Credit = 1 // Set message credit to 1
            });
            Console.WriteLine($"[{DateTime.Now}] Created consumer {consumer}");
            Message? messageIn = null;
            try
            {
                var pullTimeout = TimeSpan.FromMilliseconds(10000 * Convert.ToInt32(Timeout));
                messageIn = await consumer.ReceiveAsync().AsTask().WaitAsync(pullTimeout);
            }
            catch (TimeoutException ex)
            {
                Console.WriteLine($"[{DateTime.Now}] Connection Timeout. Process is being shut down.");
            }
            return (consumer, messageIn);

        }

        public async Task<List<double>> ConsumeResults(int tasks, string id)
        {
            List<double> list = new List<double>();
            bool pullTasks = true;

            var connectionFactory = new ConnectionFactory();
            var endpoint = Endpoint.Create(Host, Convert.ToInt32(Port), User, Password);

            IConnection connection = await connectionFactory.CreateAsync(endpoint);

            var consumer = await connection.CreateConsumerAsync(new ConsumerConfiguration
            {
                Address = ResultAddress,
                RoutingType = RoutingType.Anycast,
                Credit = 1,
                FilterExpression = $"ComputationID='{id}'"
            });
            while (connection.IsOpened && pullTasks)
            {
                var messageIn = await consumer.ReceiveAsync();
                double result = messageIn.GetBody<double>();
                Console.WriteLine($"[{DateTime.Now}] Recieved result {result}. Computation: {id}");
                list.Add(result);
                try
                {
                    await using var transaction = new Transaction();
                    await consumer.AcceptAsync(messageIn, transaction);
                    await transaction.CommitAsync();
                    if (list.Count == tasks)
                    {
                        pullTasks = false;
                        await connection.DisposeAsync();
                    }
                }
                catch (Exception)
                {
                    // Never fail the main loop.
                    // If we get here, this indicates programming error.
                    // Probably no use to reject the message and pick it up again later.
                    await consumer.AcceptAsync(messageIn);
                }
            }

            return list;
        }


    }
}
