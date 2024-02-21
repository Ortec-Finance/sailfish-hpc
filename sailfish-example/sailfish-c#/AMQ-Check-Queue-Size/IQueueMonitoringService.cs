using System.Threading.Tasks;

namespace RNMartingaleCloudApp
{
    public interface IQueueMonitoringService
    {
        Task<int> GetResultQueueSize(string id);
    }
}