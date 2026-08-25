# Linux Networking Stack

**Category:** Operating Systems
**Subcategory:** Linux Networking / Kernel / Network Programming
**Tags:** Linux, networking, kernel, TCP/IP, sockets, Ethernet, IP, TCP, UDP, Netfilter, routing, NIC, packets

---

## 1. The Big Picture

The Linux networking stack is the set of kernel subsystems that take network data from a **physical/network interface**, process it through protocols such as Ethernet, IP and TCP/UDP, and eventually deliver it to a **userspace application**.

At a simplified level:

```text
                         USER SPACE
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Application                                                │
│     │                                                       │
│     │ socket(), send(), recv()                              │
│     ▼                                                       │
│  Socket API                                                 │
│                                                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
════════════════════════╪══════════════════════════════════════
                        │
                         KERNEL
                        │
                        ▼
                 Socket subsystem
                        │
                        ▼
                  TCP / UDP / SCTP
                        │
                        ▼
                     IP layer
                IPv4 / IPv6
                        │
                        ▼
               Routing / Netfilter
                        │
                        ▼
                Network device layer
                        │
                        ▼
                     qdisc
                        │
                        ▼
                       NIC
════════════════════════╪══════════════════════════════════════
                        │
                        ▼
                     HARDWARE
```

For incoming packets, the direction is reversed.

---

# 2. The Most Important Mental Model

Think of Linux networking as a **packet processing pipeline**.

For an outgoing TCP packet:

```text
Application
    │
    │ write()
    ▼
Socket
    │
    ▼
TCP
    │
    ▼
IP
    │
    ▼
Routing
    │
    ▼
Netfilter
    │
    ▼
qdisc
    │
    ▼
Network driver
    │
    ▼
NIC
    │
    ▼
Ethernet
    │
    ▼
Network
```

For an incoming packet:

```text
Network
    │
    ▼
NIC
    │
    ▼
Network driver
    │
    ▼
Kernel networking receive path
    │
    ▼
Ethernet
    │
    ▼
IP
    │
    ▼
TCP / UDP
    │
    ▼
Socket
    │
    ▼
recv()
    │
    ▼
Application
```

The important thing is that **TCP/IP is not one monolithic subsystem**. Linux has multiple layers and subsystems interacting with each other.

---

# 3. Network Interface Card — NIC

The NIC is the hardware that actually transmits and receives frames.

Examples:

```text
eth0
enp3s0
ens33
wlan0
```

Linux represents the network interface with a `struct net_device`.

Conceptually:

```text
struct net_device
        │
        ├── device name
        ├── MAC address
        ├── MTU
        ├── driver operations
        ├── transmit queues
        └── statistics
```

You can inspect interfaces with:

```bash
ip link
```

Example:

```text
$ ip link

2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>
    mtu 1500
    link/ether 52:54:00:12:34:56
```

---

# 4. Network Driver

The network driver connects the Linux networking subsystem to the hardware.

Conceptually:

```text
Linux networking
       │
       ▼
network driver
       │
       ▼
NIC hardware
```

Examples of Linux drivers include:

```text
e1000
igb
ixgbe
virtio_net
mlx5
```

The driver handles things such as:

* DMA
* hardware queues
* interrupts
* packet buffers
* device configuration
* transmission
* reception

---

# 5. DMA

Modern NICs generally don't copy every packet byte directly through the CPU.

Instead, the NIC and kernel cooperate using **DMA — Direct Memory Access**.

Simplified receive path:

```text
NIC
 │
 │ DMA
 ▼
RAM
 │
 ▼
kernel packet buffer
```

The NIC can place received packet data directly into memory.

This dramatically reduces CPU overhead.

---

# 6. `sk_buff`

One of the most important structures in Linux networking is:

```c
struct sk_buff
```

Usually abbreviated:

```text
skb
```

An `sk_buff` represents a network packet/buffer as it moves through the networking stack.

Conceptually:

```text
              sk_buff
                 │
        ┌────────┼────────┐
        │        │        │
      data     length   metadata
        │
        ▼
┌─────────────────────────────┐
│ Ethernet │ IP │ TCP │ data │
└─────────────────────────────┘
```

The `skb` contains metadata describing the packet and references the actual packet memory.

This is one of the fundamental objects to understand if you're interested in Linux kernel networking.

---

# 7. Ethernet Layer

At the bottom of the traditional protocol stack is Ethernet.

An Ethernet frame looks approximately like:

```text
┌────────────┬────────────┬──────┬──────────────┬─────┐
│ Dest MAC   │ Source MAC │ Type │ Payload      │ FCS │
└────────────┴────────────┴──────┴──────────────┴─────┘
```

Example:

```text
Destination MAC
        ↓
aa:bb:cc:dd:ee:ff

Source MAC
        ↓
11:22:33:44:55:66
```

Linux handles Ethernet frames through its link-layer networking subsystem.

---

# 8. IP Layer

Above Ethernet is IP.

Linux supports:

```text
IPv4
IPv6
```

An IPv4 packet contains information such as:

```text
Source IP
Destination IP
TTL
Protocol
Length
Fragmentation information
Payload
```

Example:

```text
192.168.1.10
      │
      │ IP
      ▼
8.8.8.8
```

The IP layer's primary job is **packet delivery/routing**, not reliable delivery.

---

# 9. Routing

One of the most important things Linux does is decide:

> Where should this packet go?

Linux has a routing table.

Inspect it:

```bash
ip route
```

Example:

```text
default via 192.168.1.1 dev eth0
192.168.1.0/24 dev eth0
```

This means roughly:

```text
192.168.1.0/24
       │
       ▼
     eth0

everything else
       │
       ▼
192.168.1.1
       │
       ▼
     eth0
```

---

# 10. Routing Decision

Suppose an application sends:

```text
10.0.0.5 → 8.8.8.8
```

Linux performs a routing lookup.

Conceptually:

```text
Destination = 8.8.8.8
       │
       ▼
Routing table
       │
       ▼
best matching route
       │
       ├── next hop
       └── output interface
```

The kernel determines:

```text
next hop = 192.168.1.1
interface = eth0
```

---

# 11. ARP

IPv4 introduces another problem.

Suppose Linux knows:

```text
next hop = 192.168.1.1
```

But Ethernet needs a MAC address.

So Linux uses **ARP**:

```text
Who has 192.168.1.1?
```

The router responds:

```text
192.168.1.1 is at
aa:bb:cc:dd:ee:ff
```

Linux caches this mapping.

Inspect:

```bash
ip neigh
```

Conceptually:

```text
IP address
    │
    ▼
ARP / neighbor table
    │
    ▼
MAC address
```

IPv6 uses **Neighbor Discovery Protocol (NDP)** instead of ARP.

---

# 12. TCP

TCP sits above IP.

TCP provides:

* reliable delivery
* ordering
* retransmission
* flow control
* congestion control
* connection semantics

Conceptually:

```text
Application
     │
     ▼
    TCP
     │
     ▼
     IP
```

A TCP connection is identified by the classic 4-tuple:

```text
source IP
source port
destination IP
destination port
```

For example:

```text
192.168.1.10:54321
        ↓
142.250.72.14:443
```

---

# 13. TCP Is Stateful

UDP can be thought of as:

```text
send datagram
```

TCP maintains substantial state.

A connection has states such as:

```text
CLOSED
LISTEN
SYN-SENT
SYN-RECEIVED
ESTABLISHED
FIN-WAIT
CLOSE-WAIT
TIME-WAIT
...
```

Inspect sockets:

```bash
ss -tan
```

---

# 14. TCP Send Path

Suppose an application executes:

```c
send(fd, data, len, 0);
```

Conceptually:

```text
Application
     │
     ▼
socket
     │
     ▼
TCP
     │
     ├── sequence numbers
     ├── congestion control
     ├── retransmission state
     └── segmentation
     │
     ▼
IP
     │
     ▼
routing
     │
     ▼
NIC
```

TCP may divide the application's byte stream into multiple network segments.

---

# 15. TCP Receive Path

Incoming:

```text
NIC
 │
 ▼
Ethernet
 │
 ▼
IP
 │
 ▼
TCP
 │
 ├── validate checksum
 ├── sequence numbers
 ├── reorder
 ├── ACK
 └── congestion/flow state
 │
 ▼
socket receive buffer
 │
 ▼
recv()
 │
 ▼
application
```

The application doesn't normally receive "packets."

It receives a **byte stream**.

This distinction is extremely important.

---

# 16. UDP

UDP is much simpler.

```text
Application
     │
     ▼
    UDP
     │
     ▼
    IP
     │
     ▼
 Ethernet
```

UDP preserves datagram boundaries.

For example:

```c
send(sock, "hello", 5, 0);
send(sock, "world", 5, 0);
```

The receiver gets two datagrams rather than one arbitrary byte stream.

UDP does **not** provide TCP-like:

```text
retransmission
ordering
connection semantics
congestion control
```

---

# 17. Sockets

Applications normally interact with networking through the **socket API**.

Create:

```c
int fd = socket(
    AF_INET,
    SOCK_STREAM,
    0
);
```

Common domains:

```text
AF_INET
    IPv4

AF_INET6
    IPv6

AF_UNIX
    Unix domain sockets
```

Common types:

```text
SOCK_STREAM
    TCP

SOCK_DGRAM
    UDP
```

---

# 18. TCP Server

Typical lifecycle:

```c
socket()
   ↓
bind()
   ↓
listen()
   ↓
accept()
   ↓
recv()/send()
   ↓
close()
```

TCP client:

```c
socket()
   ↓
connect()
   ↓
send()/recv()
   ↓
close()
```

---

# 19. Socket Layer Inside the Kernel

A userspace file descriptor ultimately refers to kernel objects.

Conceptually:

```text
userspace

fd = 5
 │
 ▼
file
 │
 ▼
socket
 │
 ▼
sock
 │
 ▼
TCP / UDP state
```

This is an important Linux concept:

> A socket is exposed to userspace as a file descriptor.

That's why sockets participate in APIs such as:

```text
read()
write()
poll()
select()
epoll()
close()
```

---

# 20. `epoll`

For servers with many connections:

```text
10 connections
100 connections
10,000 connections
100,000 connections
```

you don't want to constantly scan every socket.

Linux provides:

```c
epoll_create1()
epoll_ctl()
epoll_wait()
```

Conceptually:

```text
             epoll
               │
       ┌───────┼────────┐
       ▼       ▼        ▼
      fd1     fd2      fd3
       │       │        │
       ▼       ▼        ▼
     socket  socket   socket
```

When a socket becomes ready:

```text
network event
      ↓
socket becomes readable
      ↓
epoll_wait() wakes
      ↓
application reads
```

---

# 21. Network Namespaces

Linux can create isolated network stacks.

This is fundamental to containers.

```text
Host
 │
 ├── network namespace A
 │      ├── eth0
 │      ├── routes
 │      └── sockets
 │
 └── network namespace B
        ├── eth0
        ├── routes
        └── sockets
```

Each network namespace can have its own:

* interfaces
* IP addresses
* routing tables
* firewall state
* sockets
* ports

This is one of the core technologies behind container networking.

---

# 22. Virtual Ethernet — `veth`

A `veth` pair behaves like a virtual Ethernet cable.

```text
namespace A                 namespace B

   eth0                       eth0
     │                          │
     └──────── veth pair ───────┘
```

More precisely:

```text
vethA  ←──────────────→  vethB
```

One end can live in the host namespace while the other lives in a container namespace.

---

# 23. Linux Bridges

A bridge operates approximately like a virtual Ethernet switch.

```text
             bridge0
          ┌────┼────┐
          │    │    │
        eth0  veth1 veth2
```

It learns MAC addresses and forwards Ethernet frames between ports.

This is commonly used in virtual machines and containers.

---

# 24. Network Virtualization

Linux can combine:

```text
Network namespace
        +
veth
        +
bridge
        +
routing
        +
iptables/nftables
        +
NAT
```

to create sophisticated virtual networks.

For example:

```text
             Host
              │
           bridge
        ┌─────┼─────┐
        │     │     │
      veth   veth   veth
        │     │     │
      C1     C2     C3
```

---

# 25. Netfilter

**Netfilter** is the kernel framework used for packet filtering, NAT and related packet-processing operations.

Tools such as:

```text
iptables
nftables
```

interact with this subsystem.

Conceptually:

```text
                 Network packet
                       │
                       ▼
                 Netfilter
                 ┌─────┼─────┐
                 │     │     │
              filter  NAT   ...
```

---

# 26. Netfilter Hooks

Packets pass through important hook points.

A simplified IPv4 picture:

```text
                       INPUT
                         ▲
                         │
Network ──► PREROUTING ──┼──► Routing ──► POSTROUTING ──► Network
                         │
                         ▼
                       FORWARD
                         │
                         ▼
                       OUTPUT
```

The exact path depends on whether the packet is:

* locally generated
* destined for the local machine
* being forwarded

---

# 27. Forwarding

Linux can function as a router.

For example:

```text
Network A
    │
    ▼
 eth0
 Linux router
 eth1
    │
    ▼
Network B
```

Enable IPv4 forwarding:

```bash
sysctl net.ipv4.ip_forward
```

Conceptually:

```text
incoming packet
      │
      ▼
   routing
      │
      ▼
   FORWARD
      │
      ▼
 outgoing interface
```

This is fundamental to Linux routers, VPNs, containers and network appliances.

---

# 28. NAT

NAT changes addresses and/or ports as packets cross a boundary.

Example:

```text
Private network

192.168.1.100:50000
        │
        ▼
     Linux NAT
        │
        ▼
203.0.113.20:40001
```

Return traffic is translated back.

NAT is commonly used for Internet sharing.

---

# 29. Traffic Control — `tc`

Linux can control how packets are transmitted.

The main command is:

```bash
tc
```

It can implement things such as:

* queues
* shaping
* scheduling
* prioritization
* rate limiting
* packet delay
* packet loss simulation

Conceptually:

```text
Application
     │
     ▼
network stack
     │
     ▼
    qdisc
     │
     ▼
    NIC
```

---

# 30. Qdisc

**Qdisc** means **queueing discipline**.

It controls packets waiting to leave an interface.

```text
             packets
                │
                ▼
          ┌───────────┐
          │   qdisc   │
          └─────┬─────┘
                │
                ▼
               NIC
```

Examples include:

```text
pfifo_fast
fq
fq_codel
cake
```

Qdisc selection can significantly affect latency and throughput.

---

# 31. MTU

MTU = **Maximum Transmission Unit**.

Typical Ethernet:

```text
MTU = 1500 bytes
```

Check:

```bash
ip link
```

If an IP packet is larger than the path allows, fragmentation or other mechanisms may become relevant.

For TCP, the effective segment size is influenced by MTU:

```text
MTU
 ↓
IP header
 ↓
TCP header
 ↓
payload
```

This leads to concepts such as:

```text
MSS
Path MTU Discovery
fragmentation
```

---

# 32. Checksums

Networking protocols use checksums to detect corruption.

For example:

```text
TCP checksum
UDP checksum
IP header checksum (IPv4)
```

Modern NICs may perform checksum calculations in hardware.

This is called **checksum offloading**.

---

# 33. Hardware Offloading

Modern Linux networking often doesn't perform every operation purely in software.

NICs can offload things such as:

```text
checksum calculation
TCP segmentation
receive aggregation
VLAN processing
RSS
```

Examples:

```text
TSO
GSO
GRO
LRO
RSS
```

These can make packet processing substantially more efficient.

---

# 34. TSO / GSO

### TSO

**TCP Segmentation Offload**

The kernel can hand a relatively large TCP packet to the NIC and let hardware split it into segments.

```text
large TCP buffer
       │
       ▼
      NIC
       │
   ┌───┼───┐
   ▼   ▼   ▼
 seg seg seg
```

### GSO

**Generic Segmentation Offload**

Similar concept, but performed in software at the appropriate point rather than requiring NIC hardware support.

---

# 35. GRO

**Generic Receive Offload**

Instead of processing every small packet individually, Linux can combine packets before higher-level processing.

```text
packet 1 ─┐
packet 2 ─┼──► GRO ──► larger logical packet
packet 3 ─┘
```

This reduces per-packet processing overhead.

---

# 36. RSS

**Receive Side Scaling** distributes received packets across CPU cores.

```text
                 NIC
                  │
           ┌──────┼──────┐
           ▼      ▼      ▼
         CPU0   CPU1   CPU2
```

This is critical on high-throughput systems.

---

# 37. Interrupts

Traditionally, the NIC can interrupt the CPU when packets arrive.

But interrupting the CPU for every packet would be expensive.

Linux therefore uses mechanisms such as:

```text
interrupt
   ↓
NAPI
   ↓
poll packets in batches
```

---

# 38. NAPI

**NAPI** is one of the key mechanisms in Linux network receive processing.

Instead of:

```text
packet
 ↓
interrupt
 ↓
CPU
```

for every packet, Linux can:

```text
packet burst
     ↓
interrupt
     ↓
schedule NAPI poll
     ↓
process batch
```

This greatly reduces interrupt overhead under load.

---

# 39. Receive Path — More Detailed

A simplified modern receive path:

```text
                 NIC
                  │
                  │ DMA
                  ▼
              RX ring
                  │
                  ▼
               driver
                  │
                  ▼
                 NAPI
                  │
                  ▼
               sk_buff
                  │
                  ▼
            Ethernet layer
                  │
                  ▼
               IP layer
                  │
                  ▼
             routing lookup
                  │
          ┌───────┴────────┐
          │                │
       local              forward
          │                │
          ▼                ▼
       TCP/UDP          routing
          │
          ▼
        socket
          │
          ▼
      userspace
```

---

# 40. Transmit Path — More Detailed

Outgoing:

```text
userspace
    │
    ▼
socket
    │
    ▼
TCP / UDP
    │
    ▼
IP
    │
    ▼
routing
    │
    ▼
Netfilter
    │
    ▼
qdisc
    │
    ▼
driver
    │
    ▼
TX ring
    │
    ▼
DMA
    │
    ▼
NIC
```

---

# 41. The Packet's Journey

Suppose you run:

```bash
curl https://example.com
```

A simplified journey is:

```text
curl
 │
 ▼
socket()
 │
 ▼
connect()
 │
 ▼
TCP
 │
 ▼
TLS
 │
 ▼
HTTP
```

At the kernel boundary:

```text
write()
 │
 ▼
TCP
 │
 ▼
IP
 │
 ▼
routing
 │
 ▼
Ethernet
 │
 ▼
NIC
```

Then:

```text
NIC
 │
 ▼
remote network
 │
 ▼
Internet
 │
 ▼
remote server
```

The response reverses the process.

---

# 42. Important Distinction: Protocol vs Interface

These are different concepts.

```text
eth0
```

is an **interface**.

```text
TCP
UDP
IPv4
IPv6
```

are **protocols**.

```text
192.168.1.10
```

is an IP address.

```text
aa:bb:cc:dd:ee:ff
```

is a MAC address.

```text
443
```

is a TCP/UDP port.

---

# 43. Useful Linux Commands

### Interfaces

```bash
ip link
ip addr
```

### Routing

```bash
ip route
ip rule
```

### Neighbor/ARP

```bash
ip neigh
```

### Sockets

```bash
ss -tuln
ss -tan
ss -uan
```

### Statistics

```bash
ip -s link
```

### Network namespaces

```bash
ip netns list
```

### Traffic control

```bash
tc qdisc show
```

### Firewall

```bash
nft list ruleset
```

### Packet capture

```bash
tcpdump -i eth0
```

---

# 44. `tcpdump`

One of the most useful tools for understanding networking.

```bash
sudo tcpdump -i eth0
```

TCP only:

```bash
sudo tcpdump -i eth0 tcp
```

Specific port:

```bash
sudo tcpdump -i eth0 port 443
```

Show numeric addresses:

```bash
sudo tcpdump -n -i eth0
```

This lets you observe what is actually crossing an interface rather than what you *think* is happening.

---

# 45. `ss`

Instead of older `netstat`, use:

```bash
ss
```

Listening TCP sockets:

```bash
ss -ltn
```

Listening UDP sockets:

```bash
ss -lun
```

All TCP connections:

```bash
ss -tan
```

Show processes:

```bash
sudo ss -tlnp
```

Example:

```text
LISTEN
0.0.0.0:8080
```

means a process is listening for TCP connections on port 8080 on all IPv4 interfaces.

---

# 46. Network Namespaces + Containers

A simplified container network:

```text
                       HOST
                         │
                    docker bridge
                         │
             ┌───────────┼───────────┐
             │           │           │
           veth         veth        veth
             │           │           │
             ▼           ▼           ▼
          Container   Container   Container
          namespace   namespace   namespace
```

Inside each container:

```text
eth0
IP address
routing table
sockets
```

The container effectively sees its own network stack.

---

# 47. Where Docker/Kubernetes Fit

Container networking isn't a separate magical networking system.

It uses Linux primitives such as:

```text
network namespaces
veth pairs
bridges
routing
Netfilter/nftables
iptables
VXLAN
```

Kubernetes networking adds additional abstractions and often plugins such as CNI implementations.

---

# 48. Performance Model

Network performance is often limited by **per-packet cost**, not simply bandwidth.

Suppose you have:

```text
10 Gbit/s
```

with tiny packets.

You may process vastly more packets per second than with large packets.

Therefore:

```text
throughput ≈ packets/sec × bytes/packet
```

and Linux networking performance depends heavily on:

```text
packets/sec
CPU cores
cache behavior
interrupts
DMA
memory bandwidth
NIC queues
socket processing
TCP state
```

---

# 49. Why Networking Gets Expensive

Every packet can involve:

```text
NIC
 ↓
DMA
 ↓
driver
 ↓
NAPI
 ↓
skb
 ↓
Ethernet processing
 ↓
IP processing
 ↓
routing
 ↓
TCP/UDP
 ↓
socket
 ↓
userspace
```

If you have millions of packets per second, even small amounts of work per packet become expensive.

This is why Linux has developed mechanisms such as:

```text
NAPI
GRO
GSO
TSO
RSS
XDP
eBPF
io_uring
busy polling
```

---

# 50. XDP

**eXpress Data Path (XDP)** allows programs, typically eBPF programs, to execute extremely early in packet reception.

Conceptually:

```text
NIC
 │
 ▼
driver
 │
 ▼
XDP
 │
 ├── DROP
 ├── PASS
 ├── TX
 └── REDIRECT
 │
 ▼
normal networking stack
```

This is useful when you need extremely fast packet processing.

For example, a packet filter can drop unwanted traffic before it travels through much of the normal networking stack.

---

# 51. eBPF

eBPF allows programs to run at various points in the Linux kernel.

Networking is one of its major uses.

Examples:

```text
XDP
TC
socket filters
cgroup networking
tracing
observability
```

This gives Linux a programmable networking architecture without requiring you to modify and rebuild the kernel for every new packet-processing behavior.

---

# 52. Classic Stack vs Modern Linux

The simplified textbook model:

```text
Application
    │
   TCP
    │
    IP
    │
 Ethernet
    │
   NIC
```

is useful but incomplete.

Modern Linux may look more like:

```text
                         Application
                              │
                         socket API
                              │
                        ┌─────┴─────┐
                        │ TCP / UDP │
                        └─────┬─────┘
                              │
                         Netfilter
                              │
                          Routing
                              │
                         TC / qdisc
                              │
                     ┌────────┴────────┐
                     │                 │
                    XDP               skb
                     │                 │
                     └───────┬─────────┘
                             NIC
```

And hardware offloads may move some work out of the CPU entirely.

---

# 53. The Three Levels You Should Learn

If your goal is to understand Linux networking deeply, learn it in three layers.

## Level 1 — Network Programming

Understand:

```text
socket()
bind()
listen()
accept()
connect()

send()
recv()

poll()
epoll()
```

You can build network applications without understanding the kernel internals.

---

## Level 2 — Linux Networking

Then learn:

```text
interfaces
addresses
routes
ARP/NDP
TCP
UDP
sockets
netfilter
namespaces
bridges
veth
qdisc
```

At this level you can understand:

```text
containers
VPNs
firewalls
routers
servers
network troubleshooting
```

---

## Level 3 — Kernel Networking

Then go deeper into:

```text
sk_buff
net_device
NAPI
RX/TX rings
DMA
GRO/GSO/TSO
RSS
XDP
eBPF
TCP internals
socket buffers
routing internals
Netfilter hooks
```

At this level you're studying how Linux actually processes packets.

---

# 54. The Most Useful Mental Picture

Keep this diagram in mind:

```text
                           USER SPACE
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                 Network Application                          │
│                         │                                    │
│                 socket()/send()/recv()                       │
│                         │                                    │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼
                     Socket Layer
                          │
                 ┌────────┴────────┐
                 ▼                 ▼
                TCP               UDP
                 │                 │
                 └────────┬────────┘
                          ▼
                     IP Layer
                   IPv4 / IPv6
                          │
                   ┌──────┴──────┐
                   │             │
                Routing       Netfilter
                   │             │
                   └──────┬──────┘
                          ▼
                    Traffic Control
                       / qdisc
                          │
                          ▼
                     Net Device
                          │
                       Driver
                          │
                     DMA / Rings
                          │
                          ▼
                         NIC
                          │
                          ▼
                       Network
```

And incoming traffic travels approximately upward through the same architecture.

---

## 55. The Key Idea

The Linux networking stack is best understood as **several cooperating subsystems rather than a simple seven-layer OSI stack**:

```text
               APPLICATION
                    │
              Socket API
                    │
             TCP / UDP
                    │
              IPv4 / IPv6
                    │
       ┌────────────┼────────────┐
       │            │            │
    Routing      Netfilter      XDP
       │            │            │
       └────────────┼────────────┘
                    │
                 qdisc
                    │
               net_device
                    │
                 driver
                    │
               DMA / NAPI
                    │
                   NIC
```

The **most important concepts to master** are:

1. **Sockets** — how applications interact with networking.
2. **`sk_buff`** — how Linux represents packets.
3. **TCP/UDP** — transport processing.
4. **IP + routing** — deciding where packets go.
5. **Netfilter** — filtering/NAT.
6. **`net_device` + drivers** — interface between kernel and hardware.
7. **NAPI + DMA + RX/TX rings** — how packets efficiently enter/leave the kernel.
8. **Namespaces/veth/bridges** — Linux virtualization.
9. **qdisc/TC** — traffic scheduling and shaping.
10. **XDP/eBPF** — modern programmable high-performance packet processing.

Once these pieces are understood, the Linux networking stack stops looking like a giant collection of kernel functions and starts looking like a **packet-processing pipeline with several optimization and policy points along the way**.
