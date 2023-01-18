using ActiveMQ.Artemis.Client;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace RNMartingaleCloudApp
{
    public interface IQueueService
    {
        Task AddTaskAsync(List<string> tasks, string id);
        Task<(IConsumer, Message)> ConsumeJobAsync();
        Task<List<double>> ConsumeResults(int tasks, string id);
    }
}