# Kubernetes with a cloud provider

> **Warning**
>
> This strategy was not tested on an actual cluster yet, so it is highly experimental at this point.

If you run `kubectl` from your computer to manage the Kubernetes cluster, you will need to install it.
You can check the guide for [Single computer](41-kubernetes-single-computer.md), and ignore the minikube installation.

You have to configure access to the cluster, and since that depends on the cloud provider, I will leave that to you.
Please remember that all commands will assume that you are connecting to the cluster, which might involve additional flags to pass your credentials.

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

### Retrieving the output

The easiest way to manipulate the output when you have an NFS server is to mount the NFS server.
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
