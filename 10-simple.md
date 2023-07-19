# Simple simulations on a remote computer

The simplest thing you can do remotely is running simulations that you generate with Makita.
This should be a very straightforward process, assuming that you have some permissions to install what you need.

## SSH into your remote computer

The first thing you have to do is login into your remote computer.
Find the IP address and your user name.
You might also need to perform additional steps, such as configure SSH keys.
These depend on which cloud provider you use (SURF, Digital Ocean, AWS, Azure, etc.), so make sure you follow the provider's instructions.

Connect to the remote computer using SSH.
If you are using Windows, use [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) or some other SSH client.
On Linux, OSX, and WSL you should be able to use the terminal:

```bash
ssh USER@IPADRESS
```

It is normal to receive a message such as "The authenticity ... can't be established".
Write "yes" and press "enter".

For more information on using ssh, check <https://www.digitalocean.com/community/tutorials/ssh-essentials-working-with-ssh-servers-clients-and-keys>.

## Copying data

To copy the `data` folder and other possible files, use the `scp` command.

```bash
scp -r data USER@IPADDRESS:/location/data
```

The `-r` is only necessary for folders.

## Install and run tmux

The main issue with running things remotely is that when you close the SSH connection, the commands that you are running will be killed.
To avoid that, we run [tmux](https://github.com/tmux/tmux/wiki), which is like a virtual terminal that we can detach (it's more than that, read their link).

Install `tmux` through whatever means your remote computer allows.
E.g., for Ubuntu you can run

```bash
apt install tmux
```

To run tmux just enter

```bash
tmux
```

## Run your simulations

This is where you do what you know.
For example, let's assume that we want to run Makita with an arfi template on one or more files in our `data` folder.
For that, we will install `makita` in a python environment, install the packages from pip, and run the `jobs.sh` file.
**This is exactly what we would do in a local machine.**

```bash
apt install python3-venv
python3 -m venv env
. env/bin/activate
pip3 install --upgrade pip setuptools
pip3 install asreview asreview-makita asreview-insights asreview-wordcloud asreview-datatools
asreview makita template arfi
bash jobs.sh
```

Now, the remote computer will be running the simulations.
To leave it running and come back later, follow the steps below

## Detach and attach tmux and close ssh session

Since your simulations are running inside tmux, you have to *detach* it pressing CTRL+b and then d (hold the CTRL key, press b, release both, press d).

You will be back in the terminal, with some `[detached (from session 0)]` or similar message.

**Your simulations are still running on tmux.**

To go back to them, attach back using

```bash
tmux attach
```

It will be as if you never left.

Most importantly, you can now exit from your SSH session and come back and the tmux session should still be reachable.

To close a ssh session, simply enter `exit` on the terminal.

### Test the persistence of your simulation run

To make sure that things work as expected before you leave your remote computer unnatended, do the following:

- Connect through ssh, open tmux.
- Run some simulation that takes a few minutes.
- Detach, exit the ssh session.
- Connect back, attach tmux.

The simulation should still be running but it should have made some progress.
To make sure that it is making progress, you can repeat and wait longer before reconnecting.

## Copy things back to your local machine

We use `scp` again to copy from the remote machine back to the local machine.

```bash
scp -r USER@IPADDRESS:/location/output ./
```
