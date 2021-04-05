# ContainerService
Container Service is a fast container management service that makes it easy to run, stop, and manage containers on a cluster.
Container Service enables you to launch and stop your container-based applications by using simple API calls. You can also retrieve the state of your application containers.

You can schedule the placement of your containers across your cluster based on your resource needs and availability requirements.

With Container Service, we can setup the cluster and scale the cluster very easily through automated ansible scripts.

Container Service also supports HA for both nodes and master's. If active master goes down, second master which is in standby automatically becomes active.

Using etcd cluster for supporting master's HA.

# Pending

1. Write script for uninstalling the setup
2. Write Test Scripts
    1. Test Scripts for Network cofiguration
3. Floating ip i.e floating interface
    Which helps in abstracting master's HA from computing nodes by making nodes to use floating ip to point to active master.
4. Agent on master
5. Etcd on master's for HA and storing config
6. Define schema in etcd
7. Agents should subscribe to etcd for any change in data and take appropriate action
8. Playbooks for scaling master and node
 
