# Using Kubernetes with a single computer

Note: If you don't have a Kubernetes cloud provider, running this on a single computer is less efficient than using the other suggested parallelization strategy because we will use some of the CPU and memory available for other tasks.

If you have many many cores, though, it might still make sense to do it in a single computer because the relative cost will decrease, and you have control over your CPU and memory resources.

## Installing minikube and required packages

Install `minikube` from your package provider or look into the [official documentation](https://minikube.sigs.k8s.io/docs/start/).
You should have the `kubectl` command as well.

Below, we have a more detailed explanation of the installation, which can be skipped if you want to follow a different strategy, e.g., installing with your linux package manager.

> **Note**
>
> We tested this installation procedure on SURF using a workspace with "Ubuntu 20.04 (SUDO enabled)".

Install docker following [the official documentation](https://docs.docker.com/engine/install/ubuntu/).
At the time of writing, the commands are:

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Then, add your user to the docker group:

```bash
sudo usermod -aG docker $USER
```

Log out and log in again. Test that you can run `docker run hello-world`.

Download minikube and install it.
Following the [official documentation](https://minikube.sigs.k8s.io/docs/start/) at the time of writing, you can run:

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb
sudo dpkg -i minikube_latest_amd64.deb
```

Install `kubectl` following the [official documentation](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#install-using-native-package-management), **however, fix the curl command** following [this issue](https://github.com/kubernetes/release/issues/2862):

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
# sudo curl -fsSLo /etc/apt/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
sudo curl -fsSLo /etc/apt/keyrings/kubernetes-archive-keyring.gpg https://dl.k8s.io/apt/doc/apt-key.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl
```

You can install bash completions using

```bash
kubectl completion bash | sudo tee /etc/bash_completion.d/kubectl > /dev/null
```

Log out and log in after installing bash completions.

## Start minikube

Run

```bash
minikube start --cpus CPU_NUMBER --memory HOW_MUCH_MEMORY
```

The `CPU_NUMBER` argument is the number of CPUs you want to dedicate to `minikube`.
The `HOW_MUCH_MEMORY` argument is how much memory.

## Create a namespace for asreview things

The configuration files use the namespace `asreview-cloud` by default, so if you want to change it, you need to change in the file below and all other places that have `# namespace: asreview-cloud`.

```bash
kubectl apply -f asreview-cloud-namespace.yml
```

## Create a volume

To share data between the worker and taskers, and to keep that data after using it, we need to create a volume.
The volume is necessary to hold the `data`, `scripts`, and the `output`, for instance.

We show how to configure a local volume, but you are free to use other volumes as well, as long as they accept `ReadWriteMany`.
Please notice that this assumes that you use a single node.

Below we have the command for `minikube`.

```bash
minikube ssh -- sudo mkdir -p /mnt/asreview-storage
```

Then, run

```bash
kubectl apply -f storage-local.yml
```

The [storage-local.yml](k8-config/storage-local.yml) file contains a `StorageClass`, a `PersistentVolume`, and a `PersistentVolumeClaim`.
It uses a local storage inside `minikube`, and it assumes that **2 GB** are sufficient for the project.
Change as necessary.

Then, uncomment the [worker.yml](k8-config/worker.yml) and [tasker.yml](k8-config/tasker.yml) relevant part at the `volumes` section in the end.
For this case, it should look like

```yml
volumes:
  - name: asreview-storage
    persistentVolumeClaim:
      claimName: asreview-storage
```

## Multi-node minikube

If you are using a multi-node minikube setup (for testing reasons, hopefully), also run the following:

```bash
minikube addons disable storage-provisioner
kubectl delete storageclasses.storage.k8s.io standard
kubectl apply -f kubevirt-hostpath-provisioner.yml
```
