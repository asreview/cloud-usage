# asreview-cloud

In this repository, we keep files used to run (very) large simulations in parallel in the cloud.
The approach we use here is to run a Kubernetes cluster, and send individual simulation commands to different workers.
This assumes that you already know how to run simulations with [Makita](https://github.com/asreview/asreview-makita).

This documentation should help you get Kubernetes installed locally on a Linux machine or on SURF, and to run some examples of simulations.
For more advanced usage, for instance, using an existing Kubernetes cluster, we provide no official support, but the community might have some tips.

## Explanation

The basic explanation of how this work is: one core of the machine reads the `jobs.sh` Makita file and sends each line to a different core of the machine.

The more convoluted explanation is:

- We have various _worker_ pods.
- We have a _tasker_ pod.
- The tasker runs a **shell file** (`tasker.sh`) that prepares the ground for the workers.
  - This file can be heavilly modified by the user, to handle specific use cases.
- One possible script is `python tasker-send.py FILE`, which send each line of the `FILE` to the workers as message through RabbitMQ.
  - If you don't use `tasker-send.py`, there is no parallel execution of the tasks.
- The worker receives the message and runs it as a shell command.
- When the worker completes the command, it sends a message back to the `tasker-send.py`, so it can keep track of what was executed.
- `tasker-send.py` will block the execution of further commands until `FILE` is completed.
- Another possible command is `python split-file.py FILE`, which reads the `FILE` and creates three new files:
  - `FILE.part1` contains every command before the first line containing the word `simulate`.
  - `FILE.part2` contains every `simulate` line.
  - `FILE.part3` contains all other lines.
- The most basic workflow is to take the Makita `jobs.sh`, split it into three, run the first part directly with the tasker (to create folders), then send the second part with `tasker-send.py`, and finally send the third part as well.

## Installing locally

Install `minikube` from your package provider or look into the [official documentation](https://minikube.sigs.k8s.io/docs/start/).

You should have the `kubectl` command as well.

## Install on SURF

TODO

## Start minikube and install RabbitMQ

You can read more on installing [RabbitMQ Cluster Operator](https://www.rabbitmq.com/kubernetes/operator/quickstart-operator.html).

```bash
minikube start
kubectl apply -f "https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml"
kubectl apply -f rabbitmq.yml
```

## Create a volume

The volume is necessary to hold the `data`, `scripts`, and the `output`.

```bash
kubectl apply -f volume.yml
```

The volume contains a `StorageClass`, a `PersistentVolume`, and a `PersistentVolumeClaim`.
It uses a local storage inside `minikube`, and it assumes that **2 GB** are sufficient for the project.

## Prepare the tasker script and Docker image

The `tasker.sh` defines everything that will be executed by the tasker, and indirectly by the workers.
The `tasker.Dockerfile` will create the image that will be executed in the tasker pod.
You can modify these as you see fit.
After you are done, compile and push the image:

```bash
docker build -t tasker -f tasker.Dockerfile .
docker tag tasker YOURUSER/tasker
docker push YOURUSER/tasker
```

> Note: This will push the image to Docker. You will need to create an account an login in your terminal with `docker login`.

## Prepare the worker script and Docker image

The `worker.sh` defines a very short list of tasks: running `worker-receiver.py`.
You can do other things before that, but tasks that are meant to be run before **all** workers start working should go on `tasker.sh`.
The `worker-receiver.py` runs continuously, waiting for new tasks from the tasker.

```bash
docker build -t worker -f worker.Dockerfile .
docker tag worker YOURUSER/worker
docker push YOURUSER/worker
```

## Running the workers

The file `worker.yml` contains the configuration of the deployment of the workers.
Change the `image` to reflect the path to the image that you pushed.
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

You should see some `asreview-worker-FULL-NAME` pods with "Running" status.
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

Similarly, the `tasker.yml` allows you to run the tasker as a Kubernetes job.
Change the `image`, and optionally add a `ttlSecondsAfterFinished` to auto delete the task - I prefer to keep it until I review the log.
Run

```bash
kubectl apply -f tasker.yml
```

Similarly, you should see a `tasker` pod, and you can follow its log.

## Copying the output out of the minikube to your machine

You can copy the `output` folder from the volume with

```bash
kubectl cp asreview-worker-FULL-NAME:/app/workdir/output ./output
```
