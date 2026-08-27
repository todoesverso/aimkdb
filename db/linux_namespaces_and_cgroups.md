# Linux Namespaces and Cgroups

**Category:** Operating Systems
**Subcategory:** Linux
**Tags:** linux, namespaces, cgroups, containers, processes isolation, resource control, docker
**Type:** concept



## 1. Short Answer

**Linux namespaces** and **cgroups (control groups)** are two fundamental Linux kernel mechanisms that make containers possible.

They solve different problems:

* **Namespaces → isolation:** *What can this process see?*
* **Cgroups → resource control:** *What resources can this process use?*

A container is therefore **not a virtual machine**. A container normally consists of ordinary Linux processes running on the host kernel, but those processes are placed into namespaces that give them an isolated view of the system and cgroups that control their resource consumption.

Docker, containerd, Kubernetes, Podman, and other container technologies build higher-level functionality on top of these kernel primitives.

A useful mental model is:

```text
                         Linux Kernel
                              |
              +---------------+---------------+
              |                               |
        Namespaces                         Cgroups
        "Isolate"                           "Control"
              |                               |
       +------+-------+                +------+-------+
       |      |       |                |      |       |
      PID   Mount   Network           CPU   Memory   I/O
       |      |       |                |      |       |
       +------+-------+                +------+-------+
              |                               |
              +---------------+---------------+
                              |
                         Container
```

The important distinction is:

> **Namespaces change the process's view of the system. Cgroups constrain the process's access to resources.**



---

## 2. Core Idea

### 2.1 What is a Linux namespace?

A **namespace** isolates a particular type of global Linux resource.

Without namespaces, processes running on the same machine generally share the same view of things such as:

* processes
* network interfaces
* mounted filesystems
* hostnames
* users
* IPC objects

Namespaces allow the kernel to provide different processes with different views.

For example, imagine the host has:

```text
Host processes:

PID 1
PID 2
PID 100
PID 101
PID 102
...
```

A process inside a PID namespace might see:

```text
Container:

PID 1
PID 2
PID 3
```

The process thinks it is PID 1, while the host kernel may see it as PID 17234.

So:

```text
                Host PID namespace

        PID 17234
            |
            | process
            v
    +-------------------+
    | Container PID NS  |
    |                   |
    | PID 1             |
    | PID 2             |
    | PID 3             |
    +-------------------+
```

This is **not a second kernel**.

The host kernel is still responsible for all of these processes.

---

### 2.2 What are cgroups?

A **cgroup** is a kernel mechanism for organizing processes into groups and controlling or accounting for their resource usage.

For example:

```text
Docker container A
        |
        +-- cgroup
             |
             +-- CPU limit: 2 CPUs
             +-- Memory limit: 512 MB
             +-- I/O controls
             +-- process accounting
```

If the processes inside that cgroup try to consume more memory than their configured limit, the kernel can enforce the configured memory policy.

So while namespaces answer:

> "What can I see?"

cgroups answer:

> "How much can I consume?"

---

## 3. How They Work

A container combines several mechanisms.

Consider:

```bash
docker run --memory=512m --cpus=2 nginx
```

Conceptually, Docker/containerd creates something like:

```text
                        Linux Host
                            |
             +--------------+--------------+
             |                             |
       Container processes             Host processes
             |
      +------+------+
      |             |
 Namespaces       Cgroup
      |             |
      |             +-- CPU limit
      |             +-- Memory limit
      |             +-- I/O controls
      |
      +-- PID namespace
      +-- Mount namespace
      +-- Network namespace
      +-- UTS namespace
      +-- IPC namespace
      +-- User namespace
```

The exact implementation depends on the runtime and configuration, but this is the essential model.

---

# 4. Linux Namespaces

Linux currently provides several namespace types.

| Namespace | Isolates                                    | Example                                             |
| --------- | ------------------------------------------- | --------------------------------------------------- |
| PID       | Process ID numbering and process visibility | Container sees its own process tree                 |
| Mount     | Filesystem mount points                     | Container gets its own filesystem view              |
| Network   | Network interfaces, routing, ports          | Container gets its own network stack                |
| UTS       | Hostname and domain name                    | Container can have its own hostname                 |
| IPC       | System V IPC and POSIX message queues       | Isolate IPC resources                               |
| User      | User/group IDs                              | Container root can map to an unprivileged host user |
| Cgroup    | Cgroup hierarchy view                       | Isolate visibility of cgroups                       |
| Time      | System clocks                               | Containers can have isolated clock offsets          |

Not every container necessarily uses every namespace.

---

## 5. PID Namespaces

The **PID namespace** controls process visibility and PID numbering.

Suppose the host has:

```text
Host:

PID 1       systemd
PID 500     sshd
PID 1000    docker
PID 17234   nginx
PID 17235   worker
```

Inside a container, the same processes might appear as:

```text
Container:

PID 1       nginx
PID 2       worker
```

The kernel maintains the relationship between these PID namespaces.

Conceptually:

```text
Host PID        Container PID
---------       -------------
17234    --->       1
17235    --->       2
```

This is why the first process in a container often has PID 1.

### Why PID 1 matters

PID 1 has special responsibilities inside a PID namespace.

For example, it becomes the process responsible for reaping orphaned child processes.

This is one reason container images that simply run an application as PID 1 can sometimes encounter process-management problems.

---

# 6. Mount Namespaces

A **mount namespace** gives a process its own view of the filesystem mount hierarchy.

This is extremely important for containers.

For example, the host might have:

```text
/
├── bin
├── etc
├── home
├── usr
├── var
└── ...
```

A container can instead see:

```text
/
├── bin
├── etc
├── usr
├── var
└── app
```

The container isn't necessarily storing an entirely independent filesystem.

Instead, the process has a different **mount view**.

Container runtimes combine mount namespaces with technologies such as:

* overlay filesystems
* bind mounts
* tmpfs
* image layers

to construct the filesystem that the container sees.

---

# 7. Network Namespaces

A **network namespace** provides an isolated network stack.

A container can therefore have its own:

```text
Network namespace

eth0
lo
routing table
ARP/neighbour state
iptables/nftables state
network ports
```

For example:

```text
Host
 |
 +-- docker bridge
       |
       +-- veth pair
              |
              v
       Container network namespace
              |
              +-- eth0
              +-- lo
              +-- routes
```

A common implementation uses a **veth pair**.

A veth pair behaves approximately like a virtual Ethernet cable:

```text
Host namespace                 Container namespace

   veth-host  <================>  eth0
```

The host side can connect to a Linux bridge, while the container side lives inside the container's network namespace.

This is how a container can have its own IP address and network interfaces despite using the host's physical network hardware.

---

# 8. UTS Namespace

The UTS namespace isolates:

* hostname
* NIS domain name

This means:

```bash
hostname
```

can return a different value inside the container than on the host.

For example:

```text
Host:
server01

Container:
web-01
```

---

# 9. User Namespaces

User namespaces are particularly interesting from a security perspective.

They allow user and group IDs inside a namespace to map to different IDs outside it.

For example:

```text
Container                 Host

UID 0 (root)   ------->   UID 100000
UID 1          ------->   UID 100001
UID 2          ------->   UID 100002
```

Therefore:

> Being UID 0 inside a user namespace does not necessarily mean being UID 0 on the host.

This can substantially reduce the consequences of container compromise when correctly configured.

However, **root inside a container should not automatically be assumed to be harmless**. Container isolation is not equivalent to a security boundary as strong as a VM in every configuration.

---

# 10. Cgroups

Cgroups solve a fundamentally different problem.

Imagine two containers:

```text
Container A                  Container B

CPU-intensive                CPU-intensive
memory-intensive             memory-intensive
```

Without resource controls, one workload could potentially consume a disproportionate amount of system resources.

Cgroups allow the administrator/runtime to organize processes into resource-controlled groups:

```text
                 cgroup hierarchy
                       |
              +--------+--------+
              |                 |
         container A       container B
              |                 |
          processes          processes
```

Different controllers can enforce different policies.

---

## 11. Cgroup Controllers

Important cgroup controllers include:

| Controller | Purpose                                            |
| ---------- | -------------------------------------------------- |
| `cpu`      | CPU scheduling/resource control                    |
| `cpuset`   | Restrict CPUs and NUMA nodes                       |
| `memory`   | Memory limits/accounting                           |
| `io`       | Block I/O control                                  |
| `pids`     | Limit number of processes                          |
| `hugetlb`  | Huge-page accounting/limits                        |
| `devices`  | Device access control in applicable configurations |

Modern Linux systems primarily use **cgroup v2**, which provides a unified hierarchy.

Older systems commonly used **cgroup v1**, which had separate controller hierarchies.

---

# 12. Namespaces vs Cgroups

The easiest way to remember the difference:

| Question                              | Namespace | Cgroup |
| ------------------------------------- | --------- | ------ |
| What processes can I see?             | Yes       | No     |
| What network interfaces can I see?    | Yes       | No     |
| What filesystem mounts can I see?     | Yes       | No     |
| What hostname do I see?               | Yes       | No     |
| How much memory can I consume?        | No        | Yes    |
| How much CPU can I consume?           | No        | Yes    |
| How many processes can I create?      | No        | Yes    |
| Can I isolate a network stack?        | Yes       | No     |
| Can I account/control resource usage? | No        | Yes    |

A useful mnemonic:

```text
Namespaces = ISOLATION
Cgroups    = RESOURCE CONTROL
```

---

# 13. How Docker Uses Them

Docker is **not itself the mechanism that creates process isolation**.

Docker provides a higher-level container interface.

A simplified architecture looks like:

```text
                    Docker CLI
                        |
                        v
                  Docker Engine
                        |
                        v
                    containerd
                        |
                        v
                  OCI runtime
                  (e.g. runc)
                        |
                        v
                  Linux kernel
              +---------+---------+
              |                   |
         Namespaces            Cgroups
              |                   |
              +---------+---------+
                        |
                   Container
```

The exact Docker architecture can vary by version and configuration, but this is the important conceptual relationship.

The container runtime ultimately asks the Linux kernel to create/configure things such as:

```text
Namespaces
    ├── PID
    ├── Mount
    ├── Network
    ├── UTS
    ├── IPC
    └── User

Cgroup
    ├── CPU
    ├── Memory
    ├── PIDs
    └── I/O
```

Docker adds many other pieces around these mechanisms, including:

* image management
* container lifecycle
* networking configuration
* storage
* volumes
* logging
* security configuration
* CLI/API
* registry integration

But the **Linux kernel provides the fundamental isolation/resource-control primitives**.

---

# 14. What Actually Happens When You Run a Container?

Consider:

```bash
docker run --rm -it ubuntu bash
```

Conceptually, the runtime does something similar to:

```text
1. Obtain container image
             |
             v
2. Construct container root filesystem
             |
             v
3. Create namespaces
             |
             +-- PID
             +-- Mount
             +-- Network
             +-- UTS
             +-- IPC
             +-- User (if configured)
             |
             v
4. Create/configure cgroup
             |
             +-- CPU
             +-- Memory
             +-- PIDs
             |
             v
5. Configure networking
             |
             v
6. Configure mounts/filesystem
             |
             v
7. Start container process
             |
             v
          bash
```

The important part is that `bash` is ultimately just a Linux process.

There is no miniature Linux kernel inside it.

---

# 15. Containers vs Virtual Machines

This distinction is fundamental.

### Virtual machine

```text
Hardware
   |
   v
Host OS
   |
Hypervisor
   |
   +--------------------+
   | Guest OS           |
   |                    |
   | Kernel             |
   | Applications       |
   +--------------------+
```

A VM normally contains a **guest kernel**.

### Container

```text
Hardware
   |
   v
Linux Kernel
   |
   +-------------------+
   | Container         |
   |                   |
   | Namespaces        |
   | Cgroups           |
   | Filesystem        |
   | Application       |
   +-------------------+
```

The container normally **shares the host kernel**.

Therefore:

> A container image contains user-space software, not a complete independent operating-system kernel.

This explains why Linux containers are fundamentally different from VMs.

---

# 16. Example: Two Containers

Imagine:

```bash
docker run -d --name web nginx
docker run -d --name db postgres
```

Conceptually:

```text
                         Linux Kernel
                              |
          +-------------------+-------------------+
          |                                       |
     Container: web                         Container: db
          |                                       |
    Namespaces                              Namespaces
      PID                                      PID
      NET                                      NET
      MNT                                      MNT
      UTS                                      UTS
          |                                       |
       Cgroup                                  Cgroup
          |                                       |
       CPU/mem                                 CPU/mem
          |                                       |
        nginx                                  postgres
```

The two applications share:

* the Linux kernel
* physical CPU
* physical memory
* physical network hardware
* storage hardware

But their views and resource policies can be isolated.

---

# 17. Deep Dive: Namespace Creation

Linux exposes namespace operations through system calls such as:

```text
clone()
unshare()
setns()
```

### `clone()`

A process can create a child with selected namespace isolation.

Conceptually:

```c
clone(..., CLONE_NEWPID | CLONE_NEWNET | ...);
```

### `unshare()`

A process can detach itself from selected namespaces and create new ones.

### `setns()`

A process can enter an existing namespace.

This is important because a container runtime doesn't need a magical "container" primitive in the kernel.

Instead, it composes existing kernel mechanisms.

---

# 18. Deep Dive: Cgroup Hierarchies

Cgroups are hierarchical.

For example:

```text
/
├── system.slice
│   ├── ssh.service
│   └── nginx.service
│
└── containers
    ├── container-A
    │   ├── process 1000
    │   └── process 1001
    │
    └── container-B
        ├── process 2000
        └── process 2001
```

A parent cgroup can establish limits that apply to descendants.

This makes cgroups useful not only for containers but also for general system resource management.

For example, systemd itself heavily uses cgroups.

Therefore:

> **Cgroups are not a Docker technology.**

Docker is one important user of cgroups.

---

# 19. The Filesystem Is a Separate Piece

One common misconception is:

> "Namespaces provide the container filesystem."

Not exactly.

The filesystem view is primarily achieved through the **mount namespace**, but the actual filesystem contents are constructed using other mechanisms.

For example, Docker images commonly use layered filesystems:

```text
Container filesystem

       Application layer
             |
       Writable layer
             |
       Image layer
             |
       Image layer
             |
       Base layer
             |
       Linux filesystem
```

Overlay filesystems such as **OverlayFS** can combine these layers into a unified filesystem view.

So a container involves several independent technologies:

```text
Process isolation
      |
   Namespaces

Resource control
      |
    Cgroups

Filesystem
      |
Mount namespaces
      +
OverlayFS / bind mounts / volumes

Networking
      |
Network namespaces
      +
veth / bridge / routing / NAT

Security
      |
Capabilities
seccomp
LSM
user namespaces
```

This composition is one of the most important things to understand about Linux containers.

---

# 20. Containers Are a Composition, Not a Single Kernel Feature

There is no single Linux kernel feature called "container."

Instead:

```text
                   Container
                       |
       +---------------+---------------+
       |               |               |
   Namespaces       Cgroups        Filesystem
       |               |               |
   isolation       resources       rootfs
       |               |               |
       +---------------+---------------+
                       |
                  Networking
                       |
                Security controls
                       |
                       v
                 Linux process
```

This is why different container runtimes can implement containers differently while still using the same underlying Linux primitives.

---

# 21. What Docker Adds

Docker essentially turns this collection of mechanisms into a usable platform.

Without Docker, you could theoretically construct a container manually using Linux primitives.

For example, tools such as:

```bash
unshare
nsenter
mount
ip
systemd-run
```

can be used to interact directly with namespaces and cgroups.

Docker automates the enormous amount of work required to make this practical.

Instead of manually doing:

```text
create namespace
create cgroup
configure network
mount filesystem
configure capabilities
configure seccomp
start process
monitor process
clean everything up
```

you can do:

```bash
docker run nginx
```

Docker/containerd/runc handle the orchestration of these mechanisms.

---

# 22. Security: Isolation Is Not Just Namespaces

Namespaces and cgroups are **not the entire container security model**.

A container runtime can additionally use:

### Linux capabilities

Instead of giving a process unrestricted root privileges, Linux capabilities divide privileges into smaller units.

For example:

```text
CAP_NET_ADMIN
CAP_SYS_ADMIN
CAP_CHOWN
CAP_DAC_OVERRIDE
...
```

### seccomp

**seccomp** can restrict which system calls a process can make.

Conceptually:

```text
Application
     |
     v
system call
     |
     v
seccomp filter
     |
     +---- allowed ----> kernel
     |
     +---- denied
```

### Linux Security Modules

Systems such as:

* SELinux
* AppArmor

can impose additional security policies.

So a more complete model is:

```text
                   Container
                       |
       +---------------+----------------+
       |               |                |
 Namespaces         Cgroups         Security
       |               |                |
  isolation       resources       capabilities
                                  seccomp
                                  SELinux/AppArmor
```

---

# 23. A Better Mental Model

Instead of thinking:

> "Docker creates a little Linux computer."

Think:

> **Docker creates a group of ordinary Linux processes and gives them an isolated view of the operating system, controlled resources, a filesystem, networking, and security restrictions.**

This model explains many container behaviors.

For example, if you run:

```bash
docker exec -it mycontainer bash
```

you are not connecting to another machine.

You are starting another process that joins the container's relevant namespaces and cgroup context.

Likewise:

```bash
docker ps
```

is not querying a list of virtual machines.

It is querying Docker's container/process management state.

---

# 24. Example: Seeing the Relationship on Linux

You can inspect namespaces of a process with:

```bash
ls -l /proc/<PID>/ns/
```

You may see:

```text
ipc
mnt
net
pid
user
uts
cgroup
```

For example:

```bash
readlink /proc/1234/ns/pid
readlink /proc/1234/ns/net
readlink /proc/1234/ns/mnt
```

Processes sharing the same namespace will generally show the same namespace identifier.

You can also inspect cgroups:

```bash
cat /proc/1234/cgroup
```

On a cgroup v2 system you may see a unified hierarchy such as:

```text
0::/system.slice/docker-<container-id>.scope
```

The exact paths depend on the container runtime and system configuration.

---

# 25. Namespace + Cgroup Together

Suppose you have:

```text
Container A
    nginx
    worker
```

The kernel might conceptually maintain:

```text
Namespaces
──────────────────────────────

PID namespace A
    PID 1 nginx
    PID 2 worker

Network namespace A
    eth0
    lo

Mount namespace A
    /

UTS namespace A
    hostname = web


Cgroup
──────────────────────────────

container-A
    CPU    = 2 CPUs
    Memory = 512 MB
    PIDs   = 100
```

Now we can see the division of responsibilities:

```text
PID namespace
    "Which processes can I see?"

Network namespace
    "Which network stack can I see?"

Mount namespace
    "Which filesystem hierarchy can I see?"

Cgroup
    "How much CPU/memory/etc. can these processes consume?"
```

Together these create the illusion of an independent environment.

---

# 26. Why Containers Are Lightweight

A VM might require:

```text
Guest kernel
Kernel memory
Guest OS services
Virtual hardware
Device emulation/paravirtualization
```

A container doesn't normally need another kernel.

Instead:

```text
                  One Linux kernel
                         |
       +-----------------+-----------------+
       |                 |                 |
   Container A       Container B       Container C
       |                 |                 |
    processes          processes         processes
```

This makes containers relatively cheap to start and allows many containers to share one kernel.

However, "lightweight" does **not** mean "free." Containers still consume:

* memory
* CPU
* filesystem space
* kernel resources
* networking resources
* process table entries
* cgroup resources

---

# 27. Trade-offs and Alternatives

## Advantages

* Very low overhead compared with full VMs.
* Fast startup.
* Strong process/environment isolation when configured correctly.
* Fine-grained resource control.
* Excellent fit for application packaging and deployment.
* Multiple applications can share one host kernel.

## Disadvantages

* Containers share the host kernel.
* A kernel vulnerability can potentially affect multiple containers.
* Incorrect privileges can weaken isolation substantially.
* Linux containers are tied to the host kernel's capabilities.
* Stateful storage and networking require additional infrastructure.
* Container isolation is not identical to VM isolation.

## Alternatives

### Virtual machines

Use a VM when you need:

* a separate kernel
* stronger isolation boundaries
* different operating systems
* hardware/OS virtualization

### Sandboxing technologies

Technologies such as:

* `sandbox`
* `Firecracker`
* `gVisor`
* Kata Containers

can provide additional isolation characteristics beyond conventional Linux containers.

## When to use containers

Containers are particularly useful for:

* application deployment
* microservices
* CI/CD
* reproducible development environments
* isolated services
* batch workloads
* Kubernetes workloads

## When not to use them

A VM may be more appropriate when:

* you need a different kernel
* you require stronger tenant isolation
* you need to run a non-Linux OS
* the workload depends heavily on kernel-level customization

---

# 28. Common Pitfalls

### "A container is a lightweight VM."

Not technically.

A conventional container is a set of isolated Linux processes sharing the host kernel.

### "Namespaces limit CPU and memory."

They don't.

**Cgroups** provide resource accounting and control.

### "Cgroups isolate processes."

Not in the same sense as namespaces.

A cgroup groups processes for resource management; a PID namespace determines which processes are visible to a process.

### "Docker invented containers."

Docker popularized containers as an application/deployment technology, but Linux already had the underlying primitives.

### "Root in a container is always harmless."

No.

Depending on configuration, capabilities, namespaces, devices, mounts, kernel vulnerabilities, and other settings, a privileged container can have significant access to the host.

### "The container has its own kernel."

Normally, no.

The container uses the host's Linux kernel.

### "The container filesystem is an isolated disk."

Not necessarily.

It is generally a filesystem view assembled from mounts, image layers, writable layers, volumes, and other mechanisms.

---

# 29. Related Concepts

* **Linux process model**
* **PID namespaces**
* **Mount namespaces**
* **Network namespaces**
* **User namespaces**
* **Linux cgroups v2**
* **OverlayFS**
* **Linux capabilities**
* **seccomp**
* **SELinux**
* **AppArmor**
* **containerd**
* **OCI**
* **runc**
* **Docker**
* **Podman**
* **Kubernetes**
* **Virtual machines**
* **Linux system calls**
* **Process isolation**
* **Resource scheduling**
* **Linux networking**

---

## The One Diagram to Remember

```text
                         CONTAINER
                             |
            +----------------+----------------+
            |                |                |
            v                v                v
       NAMESPACES         CGROUPS         SECURITY
       "Isolate"         "Control"        "Restrict"
            |                |                |
     +------+------+     +----+-----+     +----+------+
     |      |      |     |    |     |     |    |      |
    PID   NET     MNT   CPU MEM    PIDs  caps seccomp LSM
     |      |      |     |    |     |
     +------+------+     +----+-----+
            |                |
            +--------+-------+
                     |
                     v
              Linux processes
                     |
                     v
                Linux kernel
```

The fundamental relationship is therefore:

> **Containers are built by composing Linux kernel mechanisms. Namespaces provide isolation, cgroups provide resource control, and additional mechanisms such as mounts, capabilities, seccomp, and Linux security modules complete the container environment. Docker provides the tooling and orchestration that makes this composition practical.**

