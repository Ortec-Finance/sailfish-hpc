using ActiveMQ.Artemis.Client;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace RNMartingaleCloudApp
{
    public interface IQueueService
    {
        Task<bool> ConsumeRunTasksAndCommitResults(Func<string, double> compute);
    }
}