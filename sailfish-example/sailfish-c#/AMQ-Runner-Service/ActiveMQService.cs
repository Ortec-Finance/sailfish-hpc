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

        public async Task<bool> ConsumeRunTasksAndCommitResults(Func<string, double> compute)
        {

            var connectionFactory = new ConnectionFactory();
            var endpoint = Endpoint.Create(Host, Convert.ToInt32(Port), User, Password);

            IConnection connection = await connectionFactory.CreateAsync(endpoint);

            var consumer = await connection.CreateConsumerAsync(new ConsumerConfiguration
            {
                Address = TaskAddress,
                RoutingType = RoutingType.Anycast,
                Credit = 1 // Set message credit to 1
            });
            Console.WriteLine($"[{DateTime.Now}] Created consumer {consumer}");
            IProducer producer = await connection.CreateProducerAsync(ResultAddress, RoutingType.Anycast);
            Console.WriteLine($"[{DateTime.Now}] Created producer {producer}");
            Message? messageIn = null;
            while (connection.IsOpened)
            {
                Console.WriteLine($"==================================================");
                Console.WriteLine($"[{DateTime.Now}] Connection open");
                //Await a task for a certain amount of time and then throw an exception
                //Catch the exception and break the loop
                try
                {
                    var pullTimeout = TimeSpan.FromMilliseconds(1000 * Convert.ToInt32(Timeout));
                    messageIn = await consumer.ReceiveAsync().AsTask().WaitAsync(pullTimeout);
                }
                catch (TimeoutException)
                {
                    Console.WriteLine($"[{DateTime.Now}] Connection Timeout. Process is being shut down.");
                    break;
                }

                try
                {
                    //transaction assures everything or never
                    //either accept the task and put it on the return queue or do nothing
                    await using (var transaction = new Transaction())
                    {
                        Console.WriteLine($"[{DateTime.Now}] Recieved a message");
                        string json = messageIn.GetBody<string>();


                        Console.WriteLine($"[{DateTime.Now}] Deserialized a message ");
                        Console.WriteLine($"[{DateTime.Now}] Recieved the body of the message.Calculating.");
                        double result = compute(json);

                        Console.WriteLine($"[{DateTime.Now}] ===========================> Computed. Batch average is {result} " + DateTime.Now);

                        Message message = new Message(result);

                        message.MessageId = Guid.NewGuid().ToString();
                        message.GroupId = message.MessageId;
                        message.ApplicationProperties["ComputationID"] = messageIn.ApplicationProperties["ComputationID"];

                        await consumer.AcceptAsync(messageIn, transaction);
                        await producer.SendAsync(message, transaction);
                        Console.WriteLine($"[{DateTime.Now}] Added a result {message.ApplicationProperties["ComputationID"]}");
                        await transaction.CommitAsync();
                        Console.WriteLine($"[{DateTime.Now}] Commited transaction");
                    }


                }
                catch (Exception e)
                {
                    // Never fail the main loop.
                    // If we get here, this indicates programming error.
                    // Probably no use to reject the message and pick it up again later.
                    Console.WriteLine($"Message unhandled: {messageIn.MessageId}: error: {e}.");
                    await consumer.AcceptAsync(messageIn);
                }
                Console.WriteLine($"==================================================");
            }

            return true;
        }

    }
}
