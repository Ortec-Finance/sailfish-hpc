using System;
using System.ComponentModel.DataAnnotations;

namespace calculator
{
    class Result
    {
        public Result(string resultsGroup, int taskId, byte[] content)
        {
            ResultsGroup = resultsGroup;
            TaskId = taskId;
            Content = content;
        }

        public Result()
        {
        }

        [Key]
        public String ResultsGroup
        {
            get;
            set;
        }

        [Key]
        public int TaskId
        {
            get;
            set;
        }

        public byte[] Content
        {
            get;
            set;
        }
    }
}