# Linux Virtual Memory

**Category:** Operating Systems
**Subcategory:** Memory
**Tags:** virtual memory, Linux, paging, page tables, MMU, TLB
**Type:** concept

## Short Answer

**Virtual memory** is the mechanism that gives each Linux process its own virtual address space, even though all processes share the same physical RAM.

A process therefore does not normally access RAM directly. When it accesses an address such as `0x7f1234567000`, the CPU's **Memory Management Unit (MMU)** translates that virtual address into a physical address using **page tables** maintained by the kernel.

The basic relationship is:

```text
Process
   |
   | virtual address
   v
+--------+
|  MMU   |
+--------+
   |
   | page-table translation
   v
Physical address
   |
   v
+---------+
|   RAM   |
+---------+
```

Virtual memory provides several important properties:

* **Isolation** — one process normally cannot access another process's memory.
* **Protection** — pages can be read-only, executable, writable, etc.
* **Flexible memory layout** — virtual addresses do not need to correspond directly to physical RAM locations.
* **Demand paging** — memory can be allocated virtually before physical RAM is actually populated.
* **Memory sharing** — multiple processes can map the same physical pages.
* **Swapping** — inactive pages can potentially be moved from RAM to secondary storage.
* **Memory mapping** — files and devices can be mapped directly into virtual address spaces.

The key idea is:

> **A process operates on virtual addresses; the MMU translates those addresses into physical memory locations.**

---

## Core Idea

### Virtual address space vs. physical memory

Suppose a machine has:

```text
16 GiB RAM
```

A process might see an address space that is vastly larger than the amount of RAM physically installed.

For example:

```text
Process A

0x000000000000
        |
        | code
        | libraries
        | heap
        | ...
        | stack
        |
0x7fffffffffff
```

Process B has its **own virtual address space**:

```text
Process B

0x000000000000
        |
        | code
        | libraries
        | heap
        | ...
        | stack
        |
0x7fffffffffff
```

The same virtual address can therefore exist in both processes:

```text
Process A                     Process B

virtual 0x400000              virtual 0x400000
       |                              |
       v                              v
physical 0x123000              physical 0x8ab000
```

The processes don't necessarily refer to the same physical memory.

This is one of the fundamental abstractions provided by virtual memory.

---

## Pages

Linux does not normally translate every individual byte independently.

Instead, memory is divided into fixed-size units called **pages**.

On a typical x86-64 Linux system, the basic page size is:

```text
4096 bytes = 4 KiB
```

A virtual address can therefore be conceptually divided into:

```text
+----------------------+------------+
|    Virtual Page      | Page Offset|
+----------------------+------------+
          |                  |
          |                  |
          v                  v
      page number        byte within page
```

For a 4 KiB page:

```text
4 KiB = 4096 = 2^12
```

Therefore the lowest **12 bits** of the virtual address represent the offset inside the page.

The remaining bits identify the virtual page.

For example:

```text
Virtual address
        |
        +------------------------+
        | virtual page | offset  |
        +------------------------+
                       12 bits
```

The page table maps the virtual page to a **physical page frame**.

```text
Virtual page 123
       |
       | page table
       v
Physical frame 982
```

The offset remains unchanged.

---

## How It Works

Consider a process accessing:

```c
int x = *ptr;
```

The CPU eventually performs a memory access using the address contained in `ptr`.

Suppose:

```text
ptr = 0x00007f1234567000
```

The CPU treats this as a **virtual address**.

### 1. CPU generates a virtual address

```text
CPU
 |
 | virtual address
 v
0x00007f1234567000
```

### 2. MMU translates the address

The MMU needs to determine:

```text
virtual page
       ↓
physical frame
```

It uses the process's page-table hierarchy.

### 3. The physical address is constructed

Suppose the translation is:

```text
virtual page  -> physical frame 0x12345
```

The page offset is preserved.

Conceptually:

```text
Virtual:

+-------------------+------------+
| virtual page      |   offset   |
+-------------------+------------+
          |
          | page table
          v
+-------------------+------------+
| physical frame    |   offset   |
+-------------------+------------+
```

### 4. RAM is accessed

The resulting physical address is sent to the memory subsystem.

```text
CPU
 |
 v
Virtual Address
 |
 v
MMU
 |
 v
Page Tables
 |
 v
Physical Address
 |
 v
RAM
```

---

# Page Tables

Page tables are data structures that describe how virtual pages map to physical pages.

A simplistic page table might look like:

| Virtual Page | Physical Frame | Permissions  |
| ------------ | -------------- | ------------ |
| 0x100        | 0x800          | Read/Execute |
| 0x101        | 0x801          | Read/Write   |
| 0x102        | —              | Not mapped   |
| 0x103        | 0x950          | Read-only    |

The actual Linux page-table structures are considerably more sophisticated.

On modern x86-64 systems, address translation normally involves multiple levels of page tables.

Conceptually:

```text
Virtual Address
      |
      v
+-----------+
| Level 4   |
+-----------+
      |
      v
+-----------+
| Level 3   |
+-----------+
      |
      v
+-----------+
| Level 2   |
+-----------+
      |
      v
+-----------+
| Level 1   |
+-----------+
      |
      v
Physical Frame
```

Linux uses architecture-independent memory-management abstractions, while the exact page-table representation depends on the CPU architecture.

---

## The TLB

Walking page tables for every memory access would be extremely expensive.

The CPU therefore maintains a cache of recent virtual-to-physical translations called the **Translation Lookaside Buffer (TLB)**.

Instead of:

```text
Virtual address
      |
      v
Page-table walk
      |
      v
Physical address
```

a common case is:

```text
Virtual address
      |
      v
     TLB
      |
      | hit
      v
Physical address
```

If the translation is not in the TLB:

```text
Virtual address
      |
      v
     TLB
      |
    miss
      |
      v
Page-table walk
      |
      v
Physical address
      |
      v
TLB updated
```

This is why the TLB is critical to virtual-memory performance.

---

# Demand Paging

One of the most important consequences of virtual memory is that **mapping a virtual address does not necessarily mean that a physical RAM page is already present**.

Consider:

```c
malloc(1024 * 1024 * 1024);
```

Allocating 1 GiB of virtual memory does not necessarily mean Linux immediately reserves 1 GiB of physical RAM and fills it with zeros.

The kernel can establish virtual-memory metadata first and populate physical pages when they are actually needed.

This is called **demand paging**.

Conceptually:

```text
malloc()
   |
   v
Virtual address range established
   |
   |
   | no physical page yet
   v
Process accesses memory
   |
   v
Page fault
   |
   v
Kernel supplies/maps a physical page
   |
   v
Instruction continues
```

The term **page fault** can sound like an error, but many page faults are completely normal.

---

# Page Faults

Suppose the process accesses a virtual page that is not currently mapped to a usable physical page.

The CPU detects this during address translation.

Instead of completing the memory access, the CPU raises a **page-fault exception**.

The kernel then determines what should happen.

Possible cases include:

1. The page simply needs to be allocated.
2. The page exists in a file and needs to be loaded.
3. The page was swapped out.
4. The access violates permissions.
5. The address is invalid.

For example:

```text
Process accesses virtual page
             |
             v
        Page table
             |
       +-----+-----+
       |           |
    mapped       absent
       |           |
       v           v
    access      page fault
                   |
                   v
                 Kernel
                   |
          +--------+--------+
          |        |        |
       allocate   load    reject
```

A valid demand fault is handled by the kernel and execution resumes.

An invalid access can result in:

```text
SIGSEGV
```

---

# Physical Memory Is Not the Same as Virtual Memory

This distinction is extremely important.

Suppose:

```text
Virtual address:
0x00007f0000000000
```

The corresponding physical page might be:

```text
Physical address:
0x0000001234500000
```

There is no requirement that the numerical values resemble each other.

Virtual memory is an **addressing abstraction**.

Physical memory is the actual hardware storage.

```text
Virtual address space
        |
        | translation
        v
Physical address space
        |
        v
       RAM
```

---

# Process Isolation

Virtual memory is also one of the mechanisms behind process isolation.

Suppose:

```text
Process A:

virtual 0x400000
        |
        v
physical 0x100000


Process B:

virtual 0x400000
        |
        v
physical 0x900000
```

Both processes can use:

```text
0x400000
```

without referring to the same physical memory.

The kernel gives each process its own address-space configuration.

This means that a normal user-space process cannot simply say:

```text
"Give me physical RAM belonging to process B."
```

The MMU enforces the mappings established by the kernel.

---

# Memory Protection

Page-table entries also contain protection information.

A page can conceptually be:

```text
Readable
Writable
Executable
User-accessible
Kernel-only
```

For example:

```text
Code page
    R X

Data page
    R W

Read-only data
    R
```

This enables important security properties.

For example, a typical executable's code pages should not normally be writable.

Likewise, kernel memory is protected from ordinary user-space accesses.

This contributes to mechanisms such as **W^X** and **NX/DEP**, depending on architecture and configuration.

---

# Shared Memory

Virtual memory does not mean that every process has completely separate physical memory.

Linux can map the same physical page into multiple address spaces.

For example:

```text
Process A                  Process B
    |                          |
    | virtual page             | virtual page
    v                          v
+-------+                  +-------+
| page  |                  | page  |
+-------+                  +-------+
    \                          /
     \                        /
      +----------------------+
      | Physical RAM page    |
      +----------------------+
```

This is useful for:

* shared-memory IPC
* shared libraries
* memory-mapped files
* copy-on-write
* other forms of memory sharing

---

# Copy-on-Write

A particularly important example is `fork()`.

Suppose process A has a memory page:

```text
Process A
    |
    v
 physical page P
```

When `fork()` creates a child, Linux does not necessarily copy every page immediately.

Instead, parent and child can initially reference the same physical pages:

```text
Parent --------+
               |
               v
          Physical page P
               ^
               |
Child ---------+
```

The pages can be marked read-only.

If the child attempts to modify one:

```text
Child writes
     |
     v
Page fault
     |
     v
Kernel creates/copies page
     |
     v
Child gets private writable page
```

Now:

```text
Parent ------> Physical page P

Child -------> Physical page Q
```

This is **copy-on-write (COW)**.

It makes operations such as `fork()` substantially more efficient when the child initially shares most of the parent's memory.

---

# Memory-Mapped Files

Virtual memory can also connect a file directly to a process's address space.

For example:

```text
File on disk
     |
     | mmap()
     v
Virtual address range
     |
     v
Process accesses memory
     |
     v
Page fault
     |
     v
Kernel loads required file page
```

Instead of explicitly doing:

```c
read(fd, buffer, size);
```

a program can use `mmap()` and access the mapped region as memory.

The kernel manages the relationship between virtual pages and the file-backed storage.

This mechanism is heavily used by:

* shared libraries
* executable files
* databases
* memory-mapped datasets
* shared memory
* file caches

---

# Example

Consider:

```c
#include <stdlib.h>

int main(void)
{
    char *buffer = malloc(4096);

    buffer[0] = 'A';

    return 0;
}
```

A simplified sequence is:

```text
malloc(4096)
     |
     v
Virtual memory range available
     |
     |
buffer[0] = 'A'
     |
     v
CPU accesses virtual address
     |
     v
TLB / page-table lookup
     |
     v
Page isn't populated
     |
     v
Page fault
     |
     v
Linux allocates/obtains a physical page
     |
     v
Page-table mapping established
     |
     v
Instruction continues
     |
     v
'A' written to RAM
```

The important point is that **the virtual-memory system is involved even though the C program appears to manipulate an ordinary pointer**.

---

# Deep Dive

## Linux's `mm` subsystem

Linux's memory-management subsystem is generally referred to as **`mm`**.

At a high level, it manages:

```text
Process address spaces
        |
        +-- Virtual memory areas
        |
        +-- Page tables
        |
        +-- Physical pages
        |
        +-- Page cache
        |
        +-- Reclaim
        |
        +-- Swap
        |
        +-- Memory mapping
        |
        +-- NUMA
```

A process's virtual address space is represented by an `mm_struct`.

Within it, Linux tracks regions of virtual memory with **VMAs (Virtual Memory Areas)**.

A VMA describes a contiguous virtual-memory region with common properties.

For example:

```text
Process address space

0x00400000
+----------------------+
| executable code      |
+----------------------+

0x00600000
+----------------------+
| global data          |
+----------------------+

0x10000000
+----------------------+
| heap                 |
+----------------------+

       ...

0x7f0000000000
+----------------------+
| shared libraries     |
+----------------------+

       ...

0x7ffffffff000
+----------------------+
| stack                |
+----------------------+
```

Each region can have different permissions and backing.

---

## Page Cache

File-backed memory introduces another important concept: the **page cache**.

Linux can keep file contents in physical memory so that subsequent accesses don't need to repeatedly read from storage.

Conceptually:

```text
             File
              |
              v
         Page Cache
              |
              v
             RAM
              |
              v
       Process address
```

This means the same physical page can potentially serve multiple processes accessing the same file.

The page cache is therefore an important part of Linux's overall memory-management strategy.

---

## Anonymous Memory

Not all memory is backed by a file.

Examples include:

* heap allocations
* stacks
* anonymous `mmap()` regions

This is called **anonymous memory**.

Conceptually:

```text
Anonymous virtual page
        |
        v
Physical RAM
        |
        +---- potentially swap-backed
```

Anonymous memory has no ordinary filesystem file providing its contents.

---

## Swap

When physical memory becomes constrained, Linux can reclaim memory.

For anonymous memory, one possible mechanism is **swap**:

```text
RAM
 |
 | page becomes reclaimable
 v
Swap storage
 |
 | later accessed
 v
Page fault
 |
 v
Read page back into RAM
```

The important distinction is:

> Virtual memory is not synonymous with swap.

Virtual memory works even on systems with no swap at all.

Swap is only one mechanism used by the virtual-memory subsystem.

---

## Large Pages

The normal page size is commonly 4 KiB, but Linux and modern CPUs can also use larger pages.

For example, x86 systems can support:

```text
4 KiB
2 MiB
1 GiB
```

Larger pages reduce the number of page-table entries and can reduce TLB pressure.

For example:

```text
4 KiB pages:

1 GiB / 4 KiB
≈ 262,144 pages
```

versus:

```text
2 MiB pages:

1 GiB / 2 MiB
= 512 pages
```

This can significantly matter for large memory workloads.

The trade-off is that larger pages can increase memory waste and reduce flexibility in memory allocation.

---

## NUMA

On multi-socket or NUMA systems, physical memory is not necessarily equally close to every CPU.

A simplified topology might look like:

```text
CPU 0 ---- RAM 0
  |
  |
  +------ RAM 1

CPU 1 ---- RAM 1
  |
  |
  +------ RAM 0
```

Accessing local memory can be faster than accessing memory attached to another NUMA node.

Linux therefore has NUMA-aware memory-management mechanisms that influence where pages are allocated and migrated.

This becomes particularly important for high-performance servers.

---

# Trade-offs and Alternatives

### Advantages

* Strong process isolation.
* Flexible address spaces.
* Efficient memory sharing.
* Demand allocation.
* Memory-mapped files.
* Copy-on-write.
* Hardware-enforced protection.
* Ability to use swap and reclaim memory.

### Disadvantages

Virtual memory introduces overhead:

* Page-table memory consumption.
* TLB misses.
* Page-table walks.
* Page faults.
* Memory-management complexity.
* Potential swap latency.
* NUMA-related effects.
* Fragmentation and allocation complexity.

### When to Use It

For normal Linux applications, you generally **do not choose whether to use virtual memory**. It is fundamental to the operating system's process model.

What you *can* choose is how to use it:

* `malloc()` for normal dynamic memory.
* `mmap()` for explicit mappings.
* shared memory for IPC.
* huge pages for appropriate high-performance workloads.
* memory-mapped files for suitable I/O patterns.

### When Not to Use It

There is generally no ordinary user-space alternative to Linux virtual memory.

However, specialized environments such as some embedded systems, kernels, hypervisors, or real-time systems may deliberately use different memory-management configurations or avoid particular mechanisms such as swapping.

---

# Common Pitfalls

### "Virtual memory means using the disk as RAM."

Not necessarily.

Virtual memory primarily means **virtual address translation and memory isolation**.

Swap is a separate mechanism.

---

### "Every `malloc()` immediately consumes physical RAM."

Not necessarily.

Linux can lazily populate memory and physical pages may only be allocated when they are actually accessed.

---

### "A page fault means the program has crashed."

No.

A page fault is a CPU exception that tells the kernel that a memory access requires handling.

Many page faults are legitimate and expected.

An invalid page fault can eventually result in `SIGSEGV`.

---

### "Virtual addresses are physical addresses with an offset."

No.

The MMU performs a translation through page tables. There is generally no simple fixed offset between a process's virtual addresses and physical RAM.

---

### "Each process owns its own physical memory."

Not necessarily.

Processes have separate **virtual address spaces**, but physical pages can be shared.

Shared libraries and copy-on-write are common examples.

---

### "Swap is required for virtual memory."

No.

Linux can use virtual memory without swap.

---

# Related Concepts

* **Processes**
* **Threads**
* **Physical Memory**
* **Page Tables**
* **MMU**
* **TLB**
* **Page Faults**
* **Demand Paging**
* **Copy-on-Write**
* **Memory Mapping (`mmap`)**
* **Page Cache**
* **Swap**
* **Huge Pages**
* **NUMA**
* **Linux `mm` subsystem**
* **Memory Protection**
* **Kernel/User Space**
* **Address Space Layout Randomization (ASLR)**

