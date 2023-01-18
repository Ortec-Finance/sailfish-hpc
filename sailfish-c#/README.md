# Sailfish HPC C# 

This folder contains example files for a ActiveMQ Configuration in C#.


# The AMQ Service
There will be two AMQ Services, one for the Run Manager and one for the Runner

## Run Manager Service
The Purpose of this Service is once it is booted up, it will watch and consume items from the Job Queue. Once it fetches a Job it will proceed with splitting up the Job into Tasks for the Runner Service to consume.

For Example, in the startup of the Service, inside `Program.cs`:  
> `(IConsumer consumer, Message message) = await QueueService.ConsumeJobAsync();`

The Program will await to consume an item from the JobQueue. Once a Job successfully is retreived, then the code will proceed to split the job into smaller bits and in a loop add those to the Work Queue.
> `await QueueService.AddTaskAsync(serializedTasks, compSpec.ID);`


## Runner Service
The runner service is a lot simpler, and only consists of one large function.
`ConsumeRunTasksAndCommitResults`

Similar to the Run Manager, on the startup of the Service it will immediately listen to the Work Queue.
After a message has been received the runner will start computing, when finished it will commit to the results queue. It is optional to have this results queue, but how the code is currently written, the Run Manager does listen to the result queue. 

# AMQ C# Library limitations
The ActiveMQ Library is limited to just a few basic actions, more advanced features like checking the size of a queue has to be done directly using the Broker's API.

## Check Queue size
In the folder AMQ-Check-Queue-Size there is an implementation for exactly that, checking the size of a Queue. 

We encourage to add more of these implementations to this Repository!