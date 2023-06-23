# Kubernetes with a cloud provider

> **Warning**
>
> This strategy was not tested on an actual cluster yet, so it is highly experimental at this point.

If you run `kubectl` from your computer to manage the Kubernetes cluster, you will need to install it.
You can check the guide for [Single computer](41-kubernetes-single-computer.md), and ignore the minikube installation.

You have to configure access to the cluster, and since that depends on the cloud provider, I will leave that to you.
Please remember that all commands will assume that you are connecting to the cluster, which might involve additional flags to pass your credentials.

## Create a namespace for asreview things

The configuration files use the namespace `asreview-cloud` by default, so if you want to change it, you need to change in the file below and all other places that have `# namespace: asreview-cloud`.

```bash
kubectl apply -f asreview-cloud-namespace.yml
```

## Create a volume

To share data between the worker and taskers, and to keep that data after using it, we need to create a volume.
The volume is necessary to hold the `data`, `scripts`, and the `output`, for instance.

If you have some volume provider that accepts `ReadWriteMany`, use that.
Otherwise, we show below how to set up a NFS server using Kubernetes resources, and then how to use that server as volume for your pods.

The file [storage-nfs.yml](k8-config/storage-nfs.yml) will run an NFS server inside one of the nodes.
Simple run

```bash
kubectl apply -f storage-nfs.yml
```

Then, run

```bash
kubectl -n asreview-cloud get services
```

You should see something like

```plaintext
NAME             TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                        AGE
...
nfs-service      ClusterIP   NFS_SERVICE_IP   <none>        2049/TCP,20048/TCP,111/TCP     82m
...
```

Copy the `NFS_SERVICE_IP`.
Then, uncomment the [worker.yml](k8-config/worker.yml) and [tasker.yml](k8-config/tasker.yml) relevant part at the `volumes` section in the end.
For this case, it should look like

```yml
volumes:
  - name: asreview-storage
    nfs:
      server: NFS_SERVICE_IP
      path: "/"
```

## StorageClass provisioner

If your cluster does not have a StorageClass provisioner, you can try the following:

```bash
kubectl apply -f kubevirt-hostpath-provisioner.yml
```
