# Kubernetes

**Category:** DevOps
**Subcategory:** Containers
**Tags:** kubernetes, containers, orchestration, pods, nodes, cluster, container runtime, control plane
**Type:** concept



## 1. Short Answer

**Kubernetes (K8s)** is a system for running and managing containers across one or more machines.

Docker answers a question like:

> **"How do I build and run this container?"**

Kubernetes answers a much larger question:

> **"How do I continuously run hundreds or thousands of containers across a cluster of machines, keep them healthy, scale them, network them, and replace them when they fail?"**

Kubernetes is therefore a **container orchestration system**.

A useful mental model is:

```text
                    Kubernetes Cluster
                           |
             +-------------+-------------+
             |                           |
        Control Plane                 Worker Nodes
        "Decides"                     "Execute"
             |                           |
       +-----+------+              +-----+------+
       |     |      |              |            |
      API  Scheduler Controller   Kubelet   Containers
       |            Manager          |            |
       +-------------+---------------+            |
                     |                            |
                     +----------------------------+
```

The most important idea is that Kubernetes is **declarative**.

You don't normally tell Kubernetes:

```text
Start container A.
Then start container B.
If A crashes, restart it.
If there are too many requests, start another A.
Put A behind this load balancer.
Move A to another machine if this machine dies.
```

Instead, you declare the desired state:

```text
I want 3 replicas of this application,
with this container image,
this amount of CPU/memory,
and this network service.
```

Kubernetes continuously works to make the actual state match that desired state.

---

# 2. Core Idea

## 2.1 Kubernetes is a control system

The best way to understand Kubernetes is not as "a tool that runs Docker containers."

Think of it as a **distributed control system**.

You describe:

```text
Desired state
     |
     v
Kubernetes
     |
     v
Actual state
```

Kubernetes continuously observes the actual state and takes actions when it differs from the desired state.

For example:

```text
Desired:

3 nginx Pods


Actual:

2 nginx Pods
```

Kubernetes notices:

```text
desired replicas = 3
actual replicas  = 2
```

and creates another Pod.

If instead:

```text
desired replicas = 3
actual replicas  = 4
```

Kubernetes can remove one.

This repeated reconciliation process is fundamental to Kubernetes.

---

# 3. Kubernetes vs Docker

It is important not to think of Kubernetes as "Docker but bigger."

They operate at different levels.

| Technology     | Main responsibility                    |
| -------------- | -------------------------------------- |
| Docker         | Build/run/manage containers            |
| containerd     | Container lifecycle/runtime management |
| runc           | Low-level OCI container runtime        |
| Kubernetes     | Orchestrate workloads across machines  |
| Kubernetes API | Control interface for the cluster      |

A simplified relationship is:

```text
                    Kubernetes
                         |
                  container runtime
                         |
                    containerd
                         |
                       runc
                         |
                   Linux kernel
              +----------+----------+
              |                     |
         Namespaces              Cgroups
              |                     |
              +----------+----------+
                         |
                      Process
```

Modern Kubernetes does **not require Docker Engine** to run containers.

Kubernetes communicates with a container runtime through the **Container Runtime Interface (CRI)**.

Common runtimes include:

* containerd
* CRI-O

The runtime ultimately relies on Linux primitives such as namespaces and cgroups.

---

# 4. The Kubernetes Cluster

A Kubernetes installation is called a **cluster**.

A cluster consists primarily of:

```text
Kubernetes Cluster
│
├── Control Plane
│
└── Worker Nodes
    ├── Node 1
    ├── Node 2
    └── Node 3
```

The two major roles are:

### Control plane

Responsible for deciding what should happen.

### Worker node

Responsible for actually running workloads.

---

# 5. Control Plane

The control plane contains several important components.

```text
                 Control Plane
                       |
       +---------------+----------------+
       |               |                |
   API Server      Scheduler      Controller
                                       Manager
       |
       v
   etcd
```

The exact deployment architecture can vary, but these are the core components.

---

## 5.1 kube-apiserver

The **Kubernetes API server** is the primary interface to the cluster.

Commands such as:

```bash
kubectl get pods
```

ultimately communicate with the Kubernetes API.

Conceptually:

```text
kubectl
   |
   | HTTPS
   v
kube-apiserver
   |
   +----> authentication
   +----> authorization
   +----> validation
   +----> cluster state
```

The API server is therefore the central entry point into Kubernetes.

---

# 6. etcd

**etcd** is a distributed key-value store used by Kubernetes to persist cluster state.

Conceptually:

```text
etcd

cluster configuration
desired state
objects
metadata
```

For example, Kubernetes needs to know:

```text
Deployment:
    name = web
    replicas = 3
    image = nginx:...
```

That information is persisted as Kubernetes API state.

A simplified architecture is:

```text
kubectl
   |
   v
API Server
   |
   v
etcd
```

The API server is the interface; etcd is the persistent backing store.

---

# 7. Scheduler

The **kube-scheduler** decides which worker node should run a newly created Pod.

Suppose you have:

```text
Node A
CPU: 80% used

Node B
CPU: 20% used

Node C
CPU: 40% used
```

and Kubernetes needs to schedule a Pod.

The scheduler evaluates the nodes according to scheduling constraints and selects an appropriate node.

Conceptually:

```text
                 New Pod
                    |
                    v
               Scheduler
                    |
          +---------+---------+
          |         |         |
          v         v         v
        Node A    Node B    Node C
          X         ✓         ?
```

Scheduling can consider things such as:

* available resources
* CPU/memory requests
* node selectors
* affinity/anti-affinity
* taints/tolerations
* topology constraints
* other scheduling policies

---

# 8. Controllers

Controllers are one of the most important Kubernetes concepts.

A controller continuously compares:

```text
Desired state
      vs
Actual state
```

and attempts to reconcile the difference.

For example:

```text
Desired:
3 replicas

Actual:
2 replicas

        |
        v
Controller
        |
        v
Create Pod
```

This is called the **reconciliation loop**.

Conceptually:

```text
        +--------------------+
        |                    |
        v                    |
 Observe actual state       |
        |                    |
        v                    |
 Compare with desired       |
        |                    |
        v                    |
 Calculate required action  |
        |                    |
        v                    |
 Perform action ------------+
```

This pattern is used throughout Kubernetes.

---

# 9. Worker Nodes

A worker node is a machine that runs workloads.

A simplified node looks like:

```text
Worker Node
│
├── kubelet
│
├── container runtime
│
└── Pods
    ├── Pod
    │   └── Container
    │
    ├── Pod
    │   └── Container
    │
    └── Pod
        └── Containers
```

The major components are:

* **kubelet**
* **container runtime**
* networking components
* storage components
* the actual workload containers

---

# 10. kubelet

The **kubelet** is the Kubernetes agent running on each worker node.

Its job is approximately:

> "Make sure the Pods assigned to this node are actually running according to their specification."

The kubelet communicates with the API server and interacts with the container runtime.

Conceptually:

```text
             API Server
                  |
                  | Pod specification
                  v
               kubelet
                  |
                  v
          Container Runtime
                  |
                  v
              Containers
```

If a container crashes, the kubelet/runtime can restart it according to the Pod's configuration.

---

# 11. Pods

A **Pod** is the smallest deployable unit in Kubernetes.

This is one of the most important concepts.

A Pod is **not necessarily one container**.

It can contain one or more tightly coupled containers.

For example:

```text
Pod
│
├── Container A
│
└── Container B
```

The containers in a Pod share important resources, particularly:

* network namespace
* IP address
* localhost networking
* volumes mounted into the Pod

They can communicate through:

```text
localhost
```

For example:

```text
Pod
│
├── web :8080
│
└── sidecar :9000
```

The two containers can communicate using:

```text
localhost:8080
localhost:9000
```

---

# 12. Why Kubernetes Has Pods

You might wonder:

> Why not simply schedule containers?

Pods provide a unit for grouping processes that need to be colocated.

For example:

```text
Pod
│
├── Application
│
└── Logging sidecar
```

Both containers should:

* run on the same node
* share networking
* potentially share storage
* have the same lifecycle

The Pod provides this grouping abstraction.

At the Linux level, the containers within a Pod can share namespaces and other resources.

This connects directly to the previous topic:

```text
Kubernetes Pod
      |
      v
Container runtime
      |
      v
Linux namespaces
      |
      +-- network namespace
      +-- PID namespace
      +-- mount namespace
      |
      v
Linux processes
```

---

# 13. A Pod Is Not a VM

A Pod does not contain:

```text
a Linux kernel
```

Instead:

```text
Linux Kernel
     |
     +-------------------------+
     |                         |
   Pod A                     Pod B
     |                         |
 containers                containers
```

The workloads share the host kernel.

---

# 14. Deployments

You normally don't create Pods directly for long-running applications.

Instead, you use higher-level objects such as a **Deployment**.

For example:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx:1.29
```

This says approximately:

> Maintain three Pods running the specified container.

The relationship is:

```text
Deployment
     |
     v
ReplicaSet
     |
     +--------+--------+
     |        |        |
    Pod      Pod      Pod
     |        |        |
  nginx    nginx    nginx
```

If one Pod disappears:

```text
Deployment
     |
     v
ReplicaSet
     |
     +--------+--------+
     |        |        |
    Pod      Pod      Pod
              ^
              |
          new Pod
```

The ReplicaSet reconciles the desired replica count.

---

# 15. Services

Pods are intentionally replaceable.

Their IP addresses can change.

Therefore, applications should not normally depend directly on Pod IPs.

Kubernetes provides **Services** to give workloads a stable network abstraction.

```text
                    Service
                 10.96.x.x:80
                       |
            +----------+----------+
            |          |          |
            v          v          v
          Pod A      Pod B      Pod C
        10.x.x.1   10.x.x.2   10.x.x.3
```

The Service provides stable discovery and traffic distribution to the matching Pods.

For example:

```text
frontend
    |
    | HTTP
    v
web-service
    |
    +----> web-pod-1
    +----> web-pod-2
    +----> web-pod-3
```

---

# 16. Kubernetes Networking

Kubernetes networking builds on Linux networking primitives.

A simplified node might look like:

```text
                    Node
                     |
              Linux network
                     |
              +------+------+
              |             |
           Pod A          Pod B
              |             |
            eth0          eth0
              |             |
              +------+------+
                     |
               Node network
```

The exact implementation depends on the **Container Network Interface (CNI)** plugin.

Common CNI implementations include:

* Cilium
* Calico
* Flannel

The important distinction is:

> Kubernetes defines networking expectations; a CNI implementation provides much of the actual network implementation.

---

# 17. Kubernetes and Cgroups

Now we can connect Kubernetes directly to the previous topic.

Suppose you specify:

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "256Mi"
  limits:
    cpu: "1"
    memory: "512Mi"
```

Kubernetes uses this information for scheduling and resource management.

Conceptually:

```text
Pod
 |
 +-- Container
       |
       v
    cgroup
       |
       +-- CPU
       +-- memory
       +-- PIDs
       +-- I/O
```

The container runtime configures the underlying Linux cgroups.

So the complete relationship becomes:

```text
Kubernetes
    |
    v
Pod specification
    |
    v
kubelet
    |
    v
Container runtime
    |
    +--------------------+
    |                    |
Namespaces             Cgroups
    |                    |
Isolation           Resource control
    |                    |
    +---------+----------+
              |
              v
        Linux processes
```

---

# 18. Kubernetes Is a Layer Above Containers

This is perhaps the most important architectural picture:

```text
┌─────────────────────────────────────────────┐
│                  Kubernetes                 │
│                                             │
│ Deployments, Services, Jobs, Pods, etc.    │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│              Container Runtime              │
│             containerd / CRI-O              │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│                   Linux                    │
│                                             │
│ Namespaces | Cgroups | OverlayFS | Network │
│ Capabilities | seccomp | etc.               │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│                 Linux Kernel                │
└─────────────────────────────────────────────┘
```

Each layer has a different responsibility.

---

# 19. Declarative Configuration

Instead of imperative commands such as:

```bash
start-container
```

Kubernetes commonly uses YAML describing the desired state.

For example:

```yaml
replicas: 3
```

means:

```text
"I want 3 instances."
```

Kubernetes then determines how to achieve that state.

This is fundamentally different from a simple shell script that says:

```text
start container
wait
start another
wait
start another
```

The Kubernetes approach is:

```text
               Desired State
                     |
                     v
             Kubernetes API
                     |
                     v
              Controllers
                     |
                     v
              Actual State
                     |
                     |
                     +------ reconcile ------+
```

---

# 20. Failure Handling

Suppose:

```text
Deployment
replicas = 3

Pod A
Pod B
Pod C
```

Then Pod B crashes.

Actual state becomes:

```text
Pod A
Pod C
```

The controller detects:

```text
desired = 3
actual  = 2
```

and creates another Pod:

```text
Pod A
Pod C
Pod D
```

Now:

```text
desired = 3
actual  = 3
```

This is the core Kubernetes philosophy.

Kubernetes does not necessarily try to preserve the exact original Pod.

It tries to preserve the **desired state**.

---

# 21. Node Failure

Now imagine:

```text
Node 1
    Pod A
    Pod B

Node 2
    Pod C
```

Node 1 fails.

The control plane eventually observes that Node 1 is unavailable.

The workloads previously running there may need to be recreated elsewhere:

```text
Node 1
    X DEAD

Node 2
    Pod C
    Pod A'
    Pod B'
```

Again, Kubernetes is not necessarily "moving" the original processes.

It creates replacement workloads so that the declared desired state is restored.

---

# 22. Scaling

Suppose:

```yaml
replicas: 3
```

You change it to:

```yaml
replicas: 10
```

The controller sees:

```text
desired = 10
actual  = 3
```

and creates seven additional Pods.

```text
Before:

Pod Pod Pod


After:

Pod Pod Pod Pod Pod Pod Pod Pod Pod Pod
```

This is one of the foundations of Kubernetes horizontal scaling.

---

# 23. Kubernetes Objects

Kubernetes represents configuration and state through **objects**.

Some important ones are:

| Object                | Purpose                                            |
| --------------------- | -------------------------------------------------- |
| Pod                   | Smallest deployable workload                       |
| Deployment            | Manage replicated stateless workloads              |
| ReplicaSet            | Maintain a number of Pod replicas                  |
| StatefulSet           | Manage stateful workloads                          |
| DaemonSet             | Run a Pod on selected/all nodes                    |
| Job                   | Run work to completion                             |
| CronJob               | Schedule Jobs                                      |
| Service               | Stable network endpoint                            |
| ConfigMap             | Non-secret configuration                           |
| Secret                | Sensitive configuration data                       |
| Namespace             | Kubernetes API/resource organization and isolation |
| PersistentVolume      | Storage resource                                   |
| PersistentVolumeClaim | Request storage                                    |

Notice that **Kubernetes Namespace** is not the same thing as a **Linux namespace**.

They have completely different meanings.

---

# 24. Kubernetes Namespaces vs Linux Namespaces

This is a particularly common source of confusion.

### Linux namespace

Kernel-level isolation mechanism:

```text
PID namespace
Network namespace
Mount namespace
User namespace
...
```

### Kubernetes Namespace

A Kubernetes API-level organizational boundary:

```text
Kubernetes cluster
│
├── namespace: production
│   ├── Deployment
│   ├── Service
│   └── Pods
│
└── namespace: development
    ├── Deployment
    ├── Service
    └── Pods
```

They are **not the same mechanism**.

The naming is unfortunate but historical.

---

# 25. Deep Dive: The Complete Stack

A useful way to visualize the entire system is:

```text
                     Kubernetes API
                           |
              +------------+-------------+
              |                          |
        Control Plane               Scheduler
              |
       Controllers
              |
              v
          Pod desired state
              |
              v
          Worker Node
              |
            kubelet
              |
        Container Runtime
              |
       +------+-------+
       |              |
  Namespaces       Cgroups
       |              |
       |              +-- CPU
       |              +-- memory
       |              +-- PIDs
       |
       +-- PID
       +-- network
       +-- mount
       +-- UTS
       +-- user
              |
              v
       Linux processes
              |
              v
          Linux kernel
```

This connects all the concepts:

```text
Kubernetes
    ↓
Pod
    ↓
Container Runtime
    ↓
Linux container primitives
    ↓
Linux process
```

---

# 26. Kubernetes Is More Than Container Orchestration

Although Kubernetes is commonly described as a container orchestrator, it is useful to think of it as a **platform for declarative distributed systems**.

The container is just one part of the system.

Kubernetes also provides abstractions for:

* service discovery
* networking
* storage
* configuration
* secrets
* scheduling
* health checking
* rolling deployments
* scaling
* workload management
* access control
* extensibility

Its API and controller architecture allow additional systems to build on Kubernetes.

---

# 27. Example: Deploying a Web Application

Imagine you have:

```text
web application
database
```

A simplified Kubernetes architecture could be:

```text
                       Internet
                           |
                           v
                    LoadBalancer
                           |
                           v
                    web-service
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
          Web Pod       Web Pod       Web Pod
             |             |             |
             +-------------+-------------+
                           |
                       DB Service
                           |
                           v
                       DB Pod(s)
```

Behind the scenes:

```text
Deployment
    |
    +-- ReplicaSet
           |
           +-- Web Pod
           +-- Web Pod
           +-- Web Pod

Service
    |
    +-- selects Web Pods
```

The Kubernetes control plane continuously ensures that this desired architecture is maintained.

---

# 28. Why Kubernetes Became Important

Running one container is easy:

```bash
docker run nginx
```

Running a production system with:

```text
100 applications
20 machines
500 containers
automatic failover
rolling deployments
service discovery
storage
TLS
monitoring
scaling
```

is much harder.

Kubernetes provides a common model for managing that complexity.

The progression is roughly:

```text
Single process
     ↓
Container
     ↓
Multiple containers
     ↓
Multiple machines
     ↓
Cluster
     ↓
Orchestration
     ↓
Kubernetes
```

---

# 29. Trade-offs and Alternatives

## Advantages

* Declarative infrastructure.
* Automatic reconciliation.
* Scheduling across many machines.
* Self-healing workloads.
* Horizontal scaling.
* Service discovery.
* Rolling updates and rollbacks.
* Large ecosystem.
* Extensible API and controller architecture.
* Works with multiple container runtimes.

## Disadvantages

* Significant operational complexity.
* Large conceptual surface area.
* Requires understanding networking, storage, scheduling, security, and distributed systems.
* Often excessive for a single server or a small application.
* Debugging can involve many layers.
* Kubernetes itself becomes another distributed system that must be operated.

## Alternatives

Depending on the problem, simpler alternatives can include:

* Docker Compose
* Podman
* systemd
* Nomad
* managed container platforms
* traditional VM-based deployment

The important question is not:

> "Should I use Kubernetes because it is standard?"

but:

> **"Do I have enough distributed deployment complexity to justify Kubernetes?"**

---

# 30. Common Pitfalls

### "Kubernetes runs Docker containers."

Not necessarily.

Modern Kubernetes communicates with container runtimes through CRI. Docker Engine is not required.

### "A Pod is a container."

No.

A Pod is a Kubernetes workload unit that can contain one or more containers.

### "A Kubernetes Namespace is a Linux namespace."

No.

They are unrelated abstractions.

### "Kubernetes provides container isolation."

Indirectly.

The actual low-level process isolation is provided by mechanisms such as Linux namespaces and security controls.

### "Kubernetes restarts the same container."

Conceptually, Kubernetes tries to restore desired state. Depending on the failure, the runtime may restart a container or Kubernetes may create a replacement Pod.

### "Kubernetes automatically makes an application highly available."

Not by itself.

You need appropriate:

* replicas
* scheduling policies
* health checks
* networking
* storage architecture
* failure-domain distribution
* application design

### "More replicas always means more performance."

Not necessarily.

The bottleneck could be:

```text
database
network
storage
CPU
lock contention
external API
```

Adding Pods doesn't automatically remove the bottleneck.

---

# 31. The Mental Model

If you remember only one hierarchy, remember this:

```text
                         KUBERNETES
                              |
                   "What should exist?"
                              |
                              v
                            PODS
                              |
                   "Where should they run?"
                              |
                              v
                           KUBELET
                              |
                  "How do I run the workload?"
                              |
                              v
                    CONTAINER RUNTIME
                              |
                    +---------+---------+
                    |                   |
               NAMESPACES           CGROUPS
               "Isolate"            "Control"
                    |                   |
                    +---------+---------+
                              |
                              v
                       LINUX PROCESSES
                              |
                              v
                         LINUX KERNEL
```

And at the architectural level:

```text
Kubernetes = distributed desired-state management

Containers = isolated processes

Namespaces = isolation

Cgroups = resource control

Linux kernel = underlying execution environment
```

That distinction is the foundation for understanding how **Docker → containers → Kubernetes** fit together.

