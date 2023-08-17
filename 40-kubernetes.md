# Running very large simulations using Kubernetes

**Warning**: This parallelization strategy requires time, patience, and probably some troubleshooting using Kubernetes that is not included in this guide.

---

The idea behind using Kubernetes is to allow scaling the parallelization across many computers while containerizing the different tasks.
This means that if you have more money and needs results faster, you can run more tasks in parallel.

The basic strategy of this Kubernetes use is to extend the parallelization in ["Running the jobs.sh file with GNU parallel"](20-parallel.md) to multiple computers.

However, even if you have several computer laying around, installing a Kubernetes cluster is not a trivial task.
For that reason, we will consider two situations:

1. You have a single computer in which you will run _minikube_; or
2. You are using a Kubernetes cluster from a cloud provider.

The first case is useful for testing some things out, or when your computer is powerful enough, but you need more control over CPU and memory usage.
The second case is the expected use case.

## How it works

The basic idea behind this Kubernetes implementation is to have a **Tasker** pod and as many **Worker** pods as we can.
The Tasker will send the individual simulate commands (and other less time-consuming commands) to the Workers.

The Tasker and Workers communicate using [RabbitMQ](https://www.rabbitmq.com).
The Tasker sends every command as a message and the Worker sends a confirmation when the command is completed.

The Tasker and Workers share the same volume, where both the input and output data will be stored.
The Workers can, optionally and if provided, upload the output to S3.

Each of these pods run a Docker image that install necessary packages.
Each of these images run a bash file.
Each bash file uses a python script and the Python package [pika](https://pika.readthedocs.io/en/stable/) to send and receive messages.

In the Worker case, the [Worker Dockerfile](code/worker.Dockerfile) must have the packages to run the models that you need to run, in addition to some basic things, and it runs the Worker bash file.
The [Worker bash file](code/worker.sh) just runs the [Worker receiver](code/worker-receiver.py) file.
The Worker receiver keeps the Worker alive waiting for messages; runs received messages as commands; tells the Tasker that it is done with a message; and sends files to S3, if configured to do so.

In the Tasker case, the [Tasker Dockerfile](code/tasker.Dockerfile) only needs the basic things, and it runs the Tasker bash file.
The [Tasker bash file](code/tasker.sh) is responsible for very important tasks.
It starts by cleaning up the volume and moving files to the correct location inside it.
Then, it runs whatever you need it to run, and this is where you have to edit to do what you need.

In the default case, the Tasker bash file runs makita once, then splits the file using the [split-file.py](code/split-file.py) script that we mentioned before.
Then it runs the first part itself (which can't be parallelized), and sends the next two parts to the Workers using the script [tasker-send.py](code/tasker-send.py).

The [tasker-send.py](code/tasker-send.py) script sends each line of the input file to the Workers as messages, and then waits for all messages to be completed.
This ensures that the part 2 is completed before part 3 starts being executed.

We have created a visual representation below:

![Workflow representation](workflow.jpg)

## Guide

As we said in the beginning, we will consider two situtations.
Either you have a single computer in which you will install `minikube`, or you have a Kubernetes cluster already set up, probably from a cloud provider.

The "single computer" strategy can also be followed to test your scripts before using the real cluster, although there are many small differences that need to be addressed.

In both cases, start by cloning this repo, as you will need the configuration files provided here:

```bash
git clone https://github.com/asreview/cloud-usage
cd cloud-usage
```

All the `.yml` files that you need to run below are inside the `k8-config` folder.
The Dockerfiles and scripts are inside `code`.
Remember to change to the correct folder as necessary.

## Specific preparation

First, follow the specific guides to setup your local computer or cluster:

- [Single computer](41-kubernetes-single-computer.md)
- [Kubernetes cluster](42-kubernetes-cloud-provider.md)

## Install RabbitMQ

We need to install and run RabbitMQ on Kubernetes.
Run the following command taken from [RabbitMQ Cluster Operator](https://www.rabbitmq.com/kubernetes/operator/quickstart-operator.html), and then the [rabbitmq.yml](k8-config/rabbitmq.yml) service.

```bash
kubectl apply -f "https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml"
```

## Start RabbitMQ configuration

Run

```bash
kubectl apply -f rabbitmq.yml
```

Check that the `rabbitmq-server-0` pod starts running after a minute or two:

```bash
kubectl -n asreview-cloud get pods
```

## S3 storage (_Optional step_)

You might want to setup S3 storage for some files after running the simulation.
You have to find your own S3 service, e.g. AWS S3 or Scaleway - looks like you can use [Scaleway](https://scaleway.com) for free under some limitations, but do that under your own risk.

After setting up S3 storage, edit the [s3-secret.yml](k8-config/s3-secret.yml) file with the relevant values.
The file must store the base 64 encoded strings, not the raw strings.
To encode, use

```bash
echo -n 'WHATEVER' | base64
```

Copy that value and paste in the appropriate field of the file.

Finally, apply the secret configuration:

```bash
kubectl apply -f s3-secret.yml
```

Edit the [worker.yml](k8-config/worker.yml) file and uncomment the lines related to S3.

By default, only the metrics file are uploaded to S3.
Edit [worker-receiver.py](code/worker-receiver.py) to change that.

By default, the prefix of the folder on S3 is the date and time.
To change that, edit [tasker.sh](code/tasker.sh).

## Prepare the tasker script and Docker image

The [tasker.sh](code/tasker.sh) defines everything that will be executed by the tasker, and indirectly by the workers.
The [tasker.Dockerfile](code/tasker.Dockerfile) will create the image that will be executed in the tasker pod.
You can modify these files as you see fit.

The default commands used inside the tasker script and Dockerfile assume that you are:

- simulating using data from a `data` folder.
- running various settings, classifiers, and/or feature extractors.
- running a custom ARFI template.
- aggregating all jobs.sh into a single one.

### Data

If you are providing the data, create a `data` folder inside the `code` folder and put your csv files in there.

> **Warning**
>
> Don't skip this part, you either need to create a data folder, or change below.

If, instead, you want to use the Synergy data set, edit [tasker.Dockerfile](code/tasker.Dockerfile) and look for the relevant lines.

### Settings, classifiers and feature extractors

Like we did for the use case ["Running many jobs.sh files one after the other"](30-many-jobs.md), each line of the file [makita-args.txt](code/makita-args.txt) contains a different setting that you can pass to the asreview command.

By default, we are running `-m logistic -e tfidf` and `-m nb -e tfidf`.
Edit the file if you want to change or add more.

### Custom ARFI template

We also assume that we are running a custom ARFI template [custom_arfi.txt.template](code/custom_arfi.txt.template).
The template contains placeholder values related to the settings mentioned in the section above.
The placeholder `SETTINGS_PLACEHOLDER` will be substituded by each line of the [makita-args.txt](code/makita-args.txt) file.
The placeholder `SETTINGS_DIR` is used to create a folder one level above the data.
By default, the value of `SETTINGS_DIR` is equal to `SETTINGS_PLACEHOLDER`, except that spaces are substituded by `_`.

This template also removes some unnecessary lines for our case (such as creating images and aggregating the results).

Furthermore, it runs a new command `rm -f ...` to remove the `.asreview` project file after use.
This ensures that the disk space does not grow to absurd proportions.

Finally, it moves three commands to the same line, to ensure that the same worker will run these in order:

- simulate (which creates the project file);
- create metrics using the project file;
- delete the project file.

### Aggregating all jobs.sh into a single jobs.sh file

Instead of following ["Running many jobs.sh files one after the other"](30-many-jobs.md), we want to parallelize even between different jobs files.
To do that, we aggregate all `jobs.sh` files into a single one.
Then, when we split the file, all of the simulation calls of all jobs will be sent to the workers at the same time.
This allows scaling the number of workers even more.

To keep things organized, we create an additional folder level before the dataset, which was described in the custom template above.

### Build and push

After you are done with modifications, compile and push the image:

```bash
docker build -t YOURUSER/tasker -f tasker.Dockerfile .
docker push YOURUSER/tasker
```

> **Note**
>
> This will push the image to Docker. You will need to create an account an login in your terminal with `docker login`.

## Prepare the worker script and Docker image

The [worker.sh](code/worker.sh) script simply runs [worker-receiver.py](code/worker-receiver.py).
You can do other things before that, but tasks that are meant to be run before **all** workers start working should go on [tasker.sh](code/tasker.sh).
The [worker-receiver.py](code/worker-receiver.py) runs continuously, waiting for new tasks from the tasker.

```bash
docker build -t YOURUSER/worker -f worker.Dockerfile .
docker push YOURUSER/worker
```

> **Note**
>
> We have created a small script that builds and pushes both images called [build-and-push.sh](code/build-and-push.sh).
> You can run it with `bash build-and-push.sh YOURUSER`.

## Running the workers

The file [worker.yml](k8-config/worker.yml) contains the configuration of the deployment of the workers.
Change the `image` to reflect the path to the image that you pushed.

> **Warning**
>
> Don't forget to change the image in the worker.yml file.

You can select the number of `replicas` to change the number of workers.
Pay attention to the resource limits, and change as you see fit.

Run with

```bash
kubectl apply -f worker.yml
```

Check that the workers are running with the following:

```bash
kubectl get pods
```

You should see some `asreview-worker-FULL-NAME` pods with "Running" status after a while.
Follow the logs of a single pod with

```bash
kubectl logs asreview-worker-FULL-NAME -f
```

You should see something like

```plaintext
Logging as ...
[*] Waiting for messages. CTRL+C to exit
```

## Running the tasker

Similarly, the [tasker.yml](k8-config/tasker.yml) allows you to run the tasker as a Kubernetes job.
Change the `image`, and optionally add a `ttlSecondsAfterFinished` to auto delete the task - I prefer to keep it until I review the log.

> **Warning**
>
> Don't forget to change the image in the tasker.yml file.

Run

```bash
kubectl apply -f tasker.yml
```

Similarly, you should see a `tasker` pod, and you can follow its log.

## Retrieving the output

You can copy the `output` folder from the volume with

```bash
kubectl -n asreview-cloud cp asreview-worker-FULL-NAME:/app/workdir/output ./output
```

Also, check the `/app/workdir/issues` folder.
It should be empty, because it contains errors while running the simulate code.
If it is not empty, the infringing lines will be shown.

### If you used NFS

When you have an NFS server you can mount it.
Run the following command in a terminal:

```bash
kubectl -n asreview-cloud port-forward nfs-server-FULL-NAME 2049
```

In another terminal, run

```bash
mkdir asreview-storage
sudo mount -v -o vers=4,loud localhost:/ asreview-storage
```

Copy things out as necessary.
When you're done, run

```bash
sudo umount asreview-storage
```

And hit CTRL-C on the running `kubectl port-forward` command.

## Deleting and restarting

If you plan to make modifications to the tasker or the worker, they have to be deleted, respectivelly.

The workers keep running after the tasker is done.
They don't know when to stop.
To stop and delete them, run

```bash
kubectl delete -f worker.yml
```

If you did not set a `ttlSecondsAfterFinished` for the tasker, it will keep existing, although not running.
You can delete it the same way as you did the workers, but using [tasker.yml](k8-config/tasker.yml).

You can then delete the volume and the [rabbitmq.yml](k8-config/rabbitmq.yml), but if you are running new tests, you don't need to.

Since the volume is mounted separately, you don't lose the data.
You will lose the execution log, though.

Running everything again is simply a matter of using `kubectl apply` again.
Of course, if you modify the `.sh` or `.py` files, you have to build the corresponding docker image again.

> **Warning**
>
> The default **tasker** deletes the whole workdir folder to make sure that it is clean when it starts.
> If you don't want this behaviour, look for the "rm -rf" line and comment it out or remove it.
> However, if you run into a "Project already exists" error, this is why.

## Troubleshooting and FAQ

### After running the tasker, the workers are in CrashLoopBackOff/Error

Probably some command in the tasker resulted in the worker failure, and now the queue is populated and the worker keep trying and failing.
Looking at the logs of the worker should give insight in the real issue.

To verify if you have a queue issue, run

```bash
kubectl -n asreview-cloud  exec rabbitmq-server-0 -- rabbitmqctl list_queues
```

If any of the queues has more than 0 messages, then this confirms the issue.
Delete the queue with messages:

```bash
kubectl -n asreview-cloud  exec rabbitmq-server-0 -- rabbitmqctl delete_queue asreview_queue
```

You should see the workers go back to "Running" state.
