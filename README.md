# ContainerService
Container Service is a fast container management service that makes it easy to run, stop, and manage containers on a cluster.
Container Service enables you to launch and stop your container-based applications by using simple API calls. You can also retrieve the state of your application containers.

You can schedule the placement of your containers across your cluster based on your resource needs and availability requirements.

With Container Service, we can setup the cluster and scale the cluster very easily through automated ansible scripts.

Container Service also supports HA for both nodes and master's. If active master goes down, second master which is in standby automatically becomes active.

Using etcd for supporting master's HA and storing service configuration.

This Project uses two bridges which are directly connected by virtual ethernet pair

   1. Docker Bridge
   2. OpenVSwitch Bridge

Uses Docker Bridge for IPAM.
OpenVSwicth for Inter-node Communication.

Docker is a single node agent, i.e a container in node-1 can't communicate with the container in node-2, So to have inter-node communication, this project uses OpenVSwitch which is a distributed virtual multilayer switch for inter-node communication.



# Tasks

1. Make uninstallation script more robust.
2. Write Test Scripts
    1. Test Scripts for Network cofiguration
3. Floating ip i.e floating interface
    Which helps in abstracting master's HA from computing nodes by making nodes to use floating ip to point to active master.
4. Agent on master
5. Etcd on master's for HA and storing config
6. Define schema in etcd
7. Agents should subscribe to etcd for any change in data and take appropriate action
8. Playbooks for scaling master and node
9. Create internal N/W for nodes in cluster to communicate
10. Make etcd listen on internal N/W
11. Update master agent code to send requests to floating ip
12. Update node agent code to pull container spec from etcd
13. Use etcd watches, instead of polling continously
14. Find the network loops and fix them
15. Assign unique nodeId to nodes
16. Support Subnet Change

# Provisioning
With ContainerService we can setup cluster with a single touch using ansible configuration management tool

# Features
## HighAvailability

1. Master's and nodes are HighAvailable
2. Abstration of Masters from nodes using floatingIp

# Security

1. ContainerService uses private subnet


# Issues and fixes

1. Using STP for network loops

## Architecture

![alt text](https://github.com/kandulaganesh/ContainerService/blob/d98b71ee30155da02985b64d8c5d7b19346bebba/images/ContainerService.jpeg?raw=true)

Using gre tunnels for inter-node communication
