# NUMA — Non-Uniform Memory Access

**Category:** Operating Systems
**Subcategory:** Memory Architecture
**Tags:** NUMA, Non-Uniform Memory Access, Linux, CPU, memory, SMP, affinity, performance
**Type:** concept



## 1. Short Answer

**NUMA (Non-Uniform Memory Access)** is a computer architecture where a machine has multiple CPUs and/or CPU sockets, each physically closer to some memory than other memory.

The important idea is:

> **Not all RAM costs the same to access.**

On a traditional UMA system:

```text
             CPU
              │
              ▼
        ┌───────────┐
        │    RAM    │
        └───────────┘

Every CPU → roughly same memory latency
```

On a NUMA system:

```text
             NUMA Node 0
        ┌─────────────────┐
        │ CPU 0           │
        │ CPU 1           │
        │                 │
        │ Local RAM       │
        └────────┬────────┘
                 │
                 │ interconnect
                 │
        ┌────────┴────────┐
        │ CPU 2           │
        │ CPU 3           │
        │                 │
        │ Local RAM       │
        └─────────────────┘
             NUMA Node 1
```

CPU 0 accessing Node 0 memory is **local**.

CPU 0 accessing Node 1 memory is **remote**.

Remote memory generally has higher latency and may have different bandwidth characteristics.

---

# 2. Why Does NUMA Exist?

NUMA exists primarily because building one enormous shared-memory system becomes increasingly difficult as CPU counts increase.

Imagine a server with:

```text
2 CPUs
128 cores
1 TB RAM
```

or:

```text
4 CPUs
256 cores
4 TB RAM
```

Connecting every CPU to every memory module with equal latency becomes expensive and difficult to scale.

Instead, the system can be divided into nodes:

```text
              NUMA system

       Node 0             Node 1
   ┌────────────┐      ┌────────────┐
   │ CPUs       │      │ CPUs       │
   │            │      │            │
   │ RAM        │      │ RAM        │
   └─────┬──────┘      └─────┬──────┘
         │                   │
         └───────┬───────────┘
                 │
             Interconnect
```

Each CPU gets relatively fast access to its local memory.

---

# 3. UMA vs NUMA

## UMA

**Uniform Memory Access**:

```text
           CPU0
             │
           CPU1
             │
           CPU2
             │
           CPU3
             │
             ▼
          ┌─────┐
          │ RAM │
          └─────┘
```

Memory latency is approximately uniform.

---

## NUMA

```text
       Node 0                    Node 1

   CPU0   CPU1                CPU2   CPU3
     │      │                   │      │
     └──┬───┘                   └──┬───┘
        │                          │
      RAM0                       RAM1
        │                          │
        └──────────┬───────────────┘
                   │
             interconnect
```

Now:

```text
CPU0 → RAM0    fast
CPU0 → RAM1    slower

CPU3 → RAM1    fast
CPU3 → RAM0    slower
```

That's the "non-uniform" part.

---

# 4. NUMA Is More Than CPU Sockets

It is tempting to think:

> NUMA = multiple CPU sockets.

That's often true on servers, but the more accurate concept is a **NUMA node**.

A NUMA node is a locality domain containing CPUs and memory with relatively similar access characteristics.

For example, Linux might report:

```text
NUMA node0 CPUs: 0-31
NUMA node1 CPUs: 32-63
```

with:

```text
node0 → 256 GB RAM
node1 → 256 GB RAM
```

The physical hardware determines the topology.

---

# 5. NUMA Distance

NUMA systems can have different distances between nodes.

Imagine:

```text
        Node 0
           │
        distance 10
           │
        Node 1
```

Linux might report something like:

```text
node distances:

       0   1
   0  10  20
   1  20  10
```

The exact values depend on the machine.

The important interpretation is:

```text
10 = local
20 = remote
```

The values are **relative distance metrics**, not simply "20 ns".

---

# 6. Linux and NUMA

Linux has extensive NUMA support.

You can inspect the topology with:

```bash
numactl --hardware
```

For example:

```text
available: 2 nodes (0-1)

node 0 cpus: 0-15
node 1 cpus: 16-31

node 0 size: 128000 MB
node 1 size: 128000 MB

node distances:
node   0   1
  0:  10  20
  1:  20  10
```

This tells you:

```text
NUMA node 0
    CPUs 0-15
    128 GB RAM

NUMA node 1
    CPUs 16-31
    128 GB RAM
```

---

# 7. See NUMA Nodes Directly

Linux exposes NUMA information through sysfs.

For example:

```bash
ls /sys/devices/system/node/
```

You might see:

```text
node0
node1
online
possible
```

Inspect a node:

```bash
ls /sys/devices/system/node/node0/
```

You can find its CPUs:

```bash
cat /sys/devices/system/node/node0/cpulist
```

and:

```bash
cat /sys/devices/system/node/node1/cpulist
```

You can also inspect memory:

```bash
cat /sys/devices/system/node/node0/meminfo
```

---

# 8. CPU Affinity

NUMA becomes particularly important when you control **which CPU executes a thread**.

Suppose:

```text
Node 0                 Node 1

CPU 0                   CPU 8
 │                       │
 │                       │
RAM 0                    RAM 1
```

Your program allocates a large data structure on RAM 0:

```text
data → RAM 0
```

Then you run the thread on CPU 8:

```text
CPU 8
  │
  │ remote access
  ▼
RAM 0
```

You may lose performance.

Ideally:

```text
CPU 0
 │
 ▼
RAM 0
```

---

# 9. Memory Locality

NUMA optimization is largely about **locality**.

You want:

```text
thread
   │
   ▼
CPU
   │
   ▼
local memory
```

rather than:

```text
thread
   │
   ▼
CPU 0
   │
   │ remote
   ▼
NUMA node 1 memory
```

This is especially important for applications that perform huge numbers of memory accesses.

---

# 10. First-Touch Policy

One important Linux NUMA behavior is the **first-touch** principle.

Consider:

```c
int *data = malloc(size);
```

Simply allocating virtual memory does not necessarily establish physical memory locality.

Later:

```c
data[i] = 0;
```

causes pages to be physically allocated/mapped.

If the thread performing the first access is running on NUMA node 1, the memory may be allocated on node 1.

Conceptually:

```text
Thread on Node 1
       │
       │ first write
       ▼
   Page fault
       │
       ▼
Physical page allocated
on Node 1
```

This is why parallel initialization can be important.

---

# 11. A NUMA-Aware Initialization Example

Bad pattern:

```c
for (size_t i = 0; i < size; ++i) {
    data[i] = 0;
}
```

performed by one thread on Node 0.

Then:

```text
Node 0
  │
  └── initializes ALL memory
              │
              ▼
          RAM on Node 0

Node 1 workers
  │
  └── access Node 0 memory
```

A NUMA-aware parallel program may instead initialize chunks from threads running on the corresponding nodes:

```text
Node 0 thread
     │
     └── initialize chunk 0

Node 1 thread
     │
     └── initialize chunk 1
```

leading to:

```text
chunk 0 → Node 0 memory
chunk 1 → Node 1 memory
```

This is sometimes called **first-touch placement**.

---

# 12. `numactl`

Linux provides `numactl` for controlling NUMA policy.

For example:

```bash
numactl --hardware
```

Run a program on CPUs belonging to node 0:

```bash
numactl --cpunodebind=0 ./program
```

Allocate memory from node 0:

```bash
numactl --membind=0 ./program
```

Run using node 0 CPUs and allocate memory from node 0:

```bash
numactl \
    --cpunodebind=0 \
    --membind=0 \
    ./program
```

You can also prefer a node rather than strictly requiring it:

```bash
numactl --preferred=0 ./program
```

The distinction matters:

```text
--membind
    strict placement policy

--preferred
    prefer this node, but allow fallback
```

---

# 13. `numastat`

Linux also provides:

```bash
numastat
```

which can show NUMA-related memory statistics.

For a particular process:

```bash
numastat -p <PID>
```

This can help identify whether a process is using memory across multiple NUMA nodes.

---

# 14. NUMA and the Linux Scheduler

You might wonder:

> If NUMA matters so much, does Linux automatically handle it?

Yes, Linux has NUMA-aware scheduling and memory management.

The kernel attempts to keep workloads and memory appropriately localized.

However:

> **The kernel cannot always know the application's ideal data locality.**

A sophisticated application can sometimes do much better by explicitly designing its workload around NUMA topology.

---

# 15. NUMA and Multithreading

Consider a server with:

```text
Node 0
  CPU 0-15
  RAM 0

Node 1
  CPU 16-31
  RAM 1
```

Suppose you have 16 worker threads.

A NUMA-friendly design could be:

```text
Node 0
 ├── Thread 0
 ├── Thread 1
 ├── ...
 ├── Thread 7
 └── local data

Node 1
 ├── Thread 8
 ├── Thread 9
 ├── ...
 ├── Thread 15
 └── local data
```

Each group mostly accesses its own memory.

This is generally much better than:

```text
All threads
     │
     ▼
one huge shared data structure
     │
     ├── Node 0
     └── Node 1
```

with heavy cross-node traffic.

---

# 16. NUMA and Cache

NUMA does **not** replace CPU caches.

A modern NUMA machine has multiple layers:

```text
Thread
  │
  ▼
CPU core
  │
  ├── L1
  ├── L2
  └── L3
       │
       ▼
   memory controller
       │
       ▼
   local DRAM
       │
       │ remote
       ▼
 other NUMA node
       │
       ▼
   remote DRAM
```

So the access hierarchy is roughly:

```text
L1
 ↓
L2
 ↓
L3
 ↓
Local RAM
 ↓
Remote NUMA RAM
```

The exact hierarchy varies by CPU architecture.

---

# 17. NUMA and Cache Coherency

Another important issue is **cache coherency**.

Suppose:

```text
CPU 0             CPU 1
 │                  │
cache              cache
 │                  │
 └────── shared variable ──────┘
```

Both CPUs may have cached copies of the same memory.

If CPU 0 modifies it, the system needs to maintain a coherent view.

On NUMA systems, maintaining coherence across sockets/nodes can be expensive.

This is why data structures with heavy cross-thread sharing can scale poorly.

---

# 18. False Sharing

NUMA optimization overlaps with another important performance problem: **false sharing**.

Suppose two threads update different variables:

```c
struct {
    long counter_a;
    long counter_b;
};
```

Thread 0:

```c
counter_a++;
```

Thread 1:

```c
counter_b++;
```

Even though the variables are logically independent, they may occupy the same cache line.

```text
Cache line
┌───────────────────────────┐
│ counter_a │ counter_b    │
└───────────────────────────┘
       ↑             ↑
     CPU 0          CPU 1
```

The cache line can bounce between CPUs.

With NUMA and multiple sockets, this can become particularly expensive.

---

# 19. NUMA-Friendly Data Structures

A common strategy is to partition data.

Instead of:

```text
Global data
 ├── item 0
 ├── item 1
 ├── item 2
 ├── ...
 └── item N
```

use:

```text
Node 0
 └── local data

Node 1
 └── local data

Node 2
 └── local data

Node 3
 └── local data
```

Then each worker mostly operates on local data.

This architecture is often called:

> **partitioned / sharded data**

---

# 20. NUMA and Databases

NUMA can have a major impact on database performance.

For example:

```text
Node 0                  Node 1
CPU + RAM                CPU + RAM
   │                        │
   └──── database workload ─┘
```

A database may partition:

```text
worker threads
buffer pools
indexes
tables
queues
```

to improve locality.

High-performance databases often pay considerable attention to:

* CPU affinity
* memory placement
* cache locality
* NUMA topology
* lock contention

---

# 21. NUMA and Networking

NUMA is particularly important for high-speed networking.

Imagine:

```text
NIC
 │
 ▼
PCIe
 │
 ▼
NUMA Node 1
 │
 ▼
CPU 16
```

If the NIC is physically attached to Node 1, you generally want packet-processing threads close to Node 1.

Bad:

```text
NIC → Node 1
          │
          ▼
       Node 0 CPU
          │
          ▼
     remote memory
```

Better:

```text
NIC → Node 1 CPU → Node 1 RAM
```

This is important for:

* 10/25/40/100+ GbE
* DPDK
* high-frequency trading
* packet processing
* storage
* NFV
* distributed systems

---

# 22. NUMA and Containers

Containers **do not eliminate NUMA**.

A container normally shares the host kernel and hardware.

Conceptually:

```text
Physical server
│
├── NUMA Node 0
│   ├── CPU
│   └── RAM
│
├── NUMA Node 1
│   ├── CPU
│   └── RAM
│
└── Linux kernel
     │
     ├── Container A
     ├── Container B
     └── Container C
```

Containers can have CPU and memory restrictions, but the underlying NUMA topology still exists.

---

# 23. Containers and NUMA

For performance-sensitive containers, you can configure CPU and memory locality.

For example, Kubernetes can use CPU pinning and topology-aware resource management.

Conceptually:

```text
NUMA Node 0
 ├── CPU 0-7
 └── RAM

NUMA Node 1
 ├── CPU 8-15
 └── RAM
```

A workload might be configured to stay within:

```text
Node 0
```

rather than bouncing between nodes.

This is especially useful for:

* databases
* telecom workloads
* packet processing
* real-time applications
* large JVM applications
* scientific computing

---

# 24. NUMA and Kubernetes

The relationship looks like:

```text
                 Kubernetes
                     │
                  kubelet
                     │
          topology / CPU management
                     │
                     ▼
                Linux kernel
                     │
            ┌────────┴────────┐
            ▼                 ▼
         NUMA 0             NUMA 1
         CPU/RAM            CPU/RAM
```

Kubernetes can use topology information to make better placement decisions.

For particularly demanding workloads, concepts such as:

```text
CPU Manager
Topology Manager
Memory Manager
```

become relevant.

The important point is:

> Kubernetes scheduling happens above the Linux NUMA machinery; the kernel ultimately controls CPU and memory placement.

---

# 25. NUMA Is a Performance Problem, Not a Correctness Problem

Your program normally works correctly regardless of whether memory is local or remote.

For example:

```text
CPU 0 → Node 1 memory
```

is perfectly legal.

The issue is:

```text
performance
```

You may get:

* higher latency
* lower effective bandwidth
* more interconnect traffic
* more cache-coherency traffic

So NUMA is primarily an optimization concern.

---

# 26. When Should You Care About NUMA?

For a normal desktop application:

> Usually, don't worry about it.

For:

```text
8+ cores
large memory footprint
multiple CPU sockets
high-performance networking
large databases
HPC
high-throughput servers
real-time workloads
```

NUMA can become very important.

A useful rule:

```text
small workload
     │
     ▼
ignore NUMA


large, memory-intensive workload
     │
     ▼
measure NUMA behavior


very large/high-performance workload
     │
     ▼
design explicitly for NUMA
```

---

# 27. A Useful Mental Model

Think of a NUMA machine as a collection of small computers that happen to share one address space:

```text
       NUMA 0                    NUMA 1

    ┌─────────┐               ┌─────────┐
    │ CPU     │               │ CPU     │
    │ Cache   │               │ Cache   │
    │ RAM     │               │ RAM     │
    └────┬────┘               └────┬────┘
         │                          │
         └──────────┬───────────────┘
                    │
              interconnect
```

The CPUs can access all memory.

But:

```text
local memory
     ↓
cheap

remote memory
     ↓
more expensive
```

That single concept explains most of NUMA.

---

# 28. NUMA Programming Model

For high-performance software, the ideal architecture is often:

```text
                  Application
                      │
            ┌─────────┴─────────┐
            │                   │
         Partition            Partition
            │                   │
            ▼                   ▼
         NUMA 0               NUMA 1
            │                   │
         Threads             Threads
            │                   │
         Local data          Local data
```

Instead of:

```text
                  Application
                      │
                      ▼
                Shared data
                      │
            ┌─────────┴─────────┐
            ▼                   ▼
         NUMA 0               NUMA 1
            │ ←── traffic ──→   │
```

The first architecture generally scales better.

---

# 29. The Connection to What We Already Covered

NUMA fits into the larger Linux performance picture:

```text
                    Linux
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
    Processes      Threads        Memory
        │             │             │
        │             │             ▼
        │             │           NUMA
        │             │             │
        │             └──────┐      │
        │                    │      │
        ▼                    ▼      ▼
   CPU affinity         scheduling  locality
        │
        ▼
      cores
        │
        ▼
      caches
        │
        ▼
       RAM
```

This is particularly relevant when you start doing **systems programming in C/Rust**, because a program's performance can depend not only on its algorithm but also on:

```text
CPU
 ↓
cache
 ↓
NUMA locality
 ↓
memory bandwidth
 ↓
scheduler
 ↓
OS
```

---

# 30. Useful Linux Commands

For practical investigation, start with:

```bash
# NUMA topology
numactl --hardware

# NUMA statistics
numastat

# Process-specific NUMA statistics
numastat -p <PID>

# CPU topology
lscpu

# NUMA sysfs information
ls /sys/devices/system/node/

# CPUs belonging to a node
cat /sys/devices/system/node/node0/cpulist

# Memory information for a node
cat /sys/devices/system/node/node0/meminfo
```

For CPU topology, also:

```bash
lscpu -e
```

and:

```bash
lstopo
```

if `hwloc` is installed.

`lstopo` is particularly useful because it gives you a visual representation of the hardware topology.

---

# 31. Summary

The key ideas are:

| Concept         | Meaning                                        |
| --------------- | ---------------------------------------------- |
| UMA             | Memory has roughly uniform access cost         |
| NUMA            | Memory access cost depends on location         |
| NUMA node       | CPU/memory locality domain                     |
| Local memory    | Memory attached/close to the CPU's node        |
| Remote memory   | Memory belonging to another node               |
| NUMA distance   | Relative cost between nodes                    |
| First touch     | Initial page access often influences placement |
| CPU affinity    | Controls where threads execute                 |
| Memory affinity | Controls/prefer where memory is allocated      |
| Locality        | Keeping computation close to its data          |
| `numactl`       | Linux userspace NUMA policy tool               |

The most important mental model is:

```text
             NUMA MACHINE

       ┌─────────────────────┐
       │      NUMA Node 0    │
       │                     │
       │  CPU ── Cache ── RAM│
       └──────────┬──────────┘
                  │
             interconnect
                  │
       ┌──────────┴──────────┐
       │      NUMA Node 1    │
       │                     │
       │  CPU ── Cache ── RAM│
       └─────────────────────┘

CPU 0 → RAM 0       LOCAL
CPU 0 → RAM 1       REMOTE

CPU 1 → RAM 1       LOCAL
CPU 1 → RAM 0       REMOTE
```

And the fundamental optimization principle is:

> **Put the thread, CPU, and data as close to each other as possible.**

This becomes especially important when building **high-performance multithreaded C/Rust applications, databases, networking systems, or containerized workloads on multi-socket servers**.

