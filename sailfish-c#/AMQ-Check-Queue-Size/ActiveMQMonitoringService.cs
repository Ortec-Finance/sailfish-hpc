using System.Threading.Tasks;
using System.Net;
using System.IO;
using System;
using System.Net.Http;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace RNMartingaleCloudApp
{
    public class ActiveMQMonitoringService : IQueueMonitoringService
    {
        public async Task<int> GetResultQueueSize(string id)
        {

            HttpMessageHandler handler = new HttpClientHandler()
            {
            };

            var httpClient = new HttpClient(handler)
            {
                BaseAddress = new Uri("http://localhost:8161/console/jolokia/?maxDepth=7&maxCollectionSize=50000&ignoreErrors=true&canonicalNaming=false"),
                Timeout = new TimeSpan(0, 2, 0)
            };

            httpClient.DefaultRequestHeaders.Add("ContentType", "application/json");
            string body = "{\"type\":\"exec\",\"mbean\":\"org.apache.activemq.artemis:broker=\\\"28b86c9f9c58\\\",component=addresses,address=\\\"SailfishWork\\\",subcomponent=queues,routing-type=\\\"anycast\\\",queue=\\\"SailfishWork\\\"\",\"operation\":\"countMessages(java.lang.String)\",\"arguments\":[\"ComputationID='" + id + "'\"]}";
            string uri = "http://localhost:8161/console/jolokia/?maxDepth=7&maxCollectionSize=50000&ignoreErrors=true&canonicalNaming=false";
            //This is the key section you were missing    
            var plainTextBytes = Encoding.UTF8.GetBytes("guest:guest");
            string val = Convert.ToBase64String(plainTextBytes);
            httpClient.DefaultRequestHeaders.Add("Authorization", "Basic " + val);
            httpClient.DefaultRequestHeaders.Add("Origin", "http://localhost");
            var content = new StringContent(body ?? String.Empty, Encoding.UTF8);
            HttpResponseMessage response = await httpClient.PostAsync(uri, content);
            var responseString = await response.Content.ReadAsStringAsync();
            var data = (JObject)JsonConvert.DeserializeObject(responseString);
            string value = data["value"].Value<string>();
            return Convert.ToInt32(value);
        }
    }
}
