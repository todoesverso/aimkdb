# Stack vs Heap in C and Rust - Linux and ELF Memory Layout

**Category:** Operating Systems
**Subcategory:** Memory
**Tags:** C, Rust, stack, heap, virtual memory, ELF, process, mmap, malloc, brk, Box, Vec, segments, sections, ASLR, page tables
**Type:** concept

> **In short:** The **stack** and **heap** are not ELF sections. An ELF executable describes things such as **code, read-only data, initialized data, and uninitialized data**. When Linux executes the ELF, it creates a **process virtual address space** and adds runtime regions such as the **stack, heap, shared libraries, and memory mappings**.

This distinction is important:

```text
ELF file on disk
       │
       │ execve()
       ▼
Linux process
       │
       ▼
virtual address space
       │
       ├── ELF code/data
       ├── heap
       ├── stack
       ├── shared libraries
       ├── mmap regions
       └── kernel-controlled regions
```

---

# 1. Start With the Three Different Concepts

It helps to separate three things that are often mixed together.

### ELF

Describes the executable file:

```text
┌─────────────────────┐
│ ELF header          │
├─────────────────────┤
│ program headers     │
├─────────────────────┤
│ sections            │
│                     │
│ .text               │
│ .rodata             │
│ .data               │
│ .bss                │
│ ...                 │
└─────────────────────┘
```

### Linux process

When Linux executes the ELF:

```text
┌─────────────────────┐
│ virtual address     │
│ space               │
│                     │
│ code                │
│ data                │
│ heap                │
│ libraries           │
│ mmap regions        │
│ stack               │
└─────────────────────┘
```

### Physical memory

The virtual addresses are mapped through page tables:

```text
CPU virtual address
        │
        ▼
   page tables
        │
        ▼
physical RAM
```

So:

> **ELF describes the executable. Linux constructs the process address space. The MMU translates virtual addresses to physical addresses.**

---

# 2. A Typical Linux Process Address Space

On a 64-bit Linux system, a simplified process might look like:

```text
HIGH ADDRESSES

0x7fffffffffff
┌──────────────────────────────┐
│ Process stack                │
│                              │
│ ↓ grows downward             │
├──────────────────────────────┤
│                              │
│ mmap() regions               │
│ shared libraries             │
│ shared objects               │
│ thread stacks                │
│                              │
├──────────────────────────────┤
│                              │
│              ...             │
│                              │
├──────────────────────────────┤
│ Heap                         │
│ ↑ traditionally grows up     │
├──────────────────────────────┤
│ .bss                         │
├──────────────────────────────┤
│ .data                        │
├──────────────────────────────┤
│ .rodata                      │
├──────────────────────────────┤
│ .text                        │
├──────────────────────────────┤
│ ELF executable               │
└──────────────────────────────┘

LOW ADDRESSES
```

This is **conceptual**, not a fixed Linux layout.

Modern Linux uses:

* ASLR
* PIE
* shared libraries
* `mmap`
* dynamically sized stacks
* different mappings depending on the program

So the actual addresses change between executions.

---

# 3. Let's Build a C Program

Consider:

```c
#include <stdio.h>
#include <stdlib.h>

int global_initialized = 42;
int global_uninitialized;

const char message[] = "hello";

void foo(void)
{
    int local = 123;

    int *heap = malloc(sizeof(int));
    *heap = 456;

    printf("local   = %p\n", (void *)&local);
    printf("heap    = %p\n", (void *)heap);
    printf("global  = %p\n", (void *)&global_initialized);
    printf("bss     = %p\n", (void *)&global_uninitialized);
    printf("message = %p\n", (void *)message);

    free(heap);
}

int main(void)
{
    foo();
}
```

There are several different kinds of memory here.

```text
global_initialized
        │
        ▼
     .data

global_uninitialized
        │
        ▼
      .bss

message
        │
        ▼
     .rodata

foo()
        │
        ▼
      .text

local
        │
        ▼
      stack

malloc()
        │
        ▼
       heap
```

---

# 4. The ELF File

Compile it:

```bash
gcc -g -O0 -o example example.c
```

Now inspect the ELF:

```bash
file example
```

You might see something like:

```text
example: ELF 64-bit LSB pie executable, x86-64
```

Now:

```bash
readelf -h example
```

This displays the ELF header.

You can also inspect sections:

```bash
readelf -S example
```

You will see sections such as:

```text
.text
.rodata
.data
.bss
.symtab
.strtab
.debug_info
...
```

---

# 5. ELF `.text`

The `.text` section contains executable machine code.

For example:

```c
void foo(void)
{
    ...
}
```

The compiler generates machine instructions.

Conceptually:

```text
ELF

.text
┌─────────────────────────┐
│ main() machine code     │
│ foo() machine code      │
│ other functions         │
└─────────────────────────┘
```

Linux maps this into the process as executable memory.

Typically the corresponding mapping has permissions similar to:

```text
r-xp
```

meaning:

```text
r = readable
w = writable
x = executable
p = private
```

---

# 6. ELF `.rodata`

Read-only constants commonly go into `.rodata`.

For:

```c
const char message[] = "hello";
```

the string data can be placed there.

Conceptually:

```text
.rodata

┌─────────────────────┐
│ "hello\0"           │
│ other constants     │
└─────────────────────┘
```

It is normally mapped read-only.

This is one reason attempting:

```c
message[0] = 'H';
```

is not valid if the object is actually placed in read-only storage.

---

# 7. ELF `.data`

Initialized writable global/static variables generally go into `.data`.

For:

```c
int global_initialized = 42;
```

we have:

```text
.data

┌─────────────────────┐
│ global_initialized  │
│          42         │
└─────────────────────┘
```

Linux maps the corresponding memory as writable.

Typically:

```text
rw-p
```

---

# 8. ELF `.bss`

Now:

```c
int global_uninitialized;
```

This is different.

It needs storage, but its initial value is zero.

It normally goes into `.bss`.

```text
.bss

┌─────────────────────────┐
│ global_uninitialized    │
│                         │
│ initially zero          │
└─────────────────────────┘
```

The interesting part is that `.bss` doesn't need to store all those zero bytes in the executable file.

Instead, ELF records the required memory size.

Linux provides zero-filled memory when loading the program.

Therefore:

```text
.data

file:
[42]


.bss

file:
[essentially no stored zero bytes]

runtime:
[00 00 00 00]
```

---

# 9. ELF Sections vs ELF Segments

This is a very important distinction.

ELF has **sections**:

```text
.text
.rodata
.data
.bss
.symtab
.debug_info
...
```

But the Linux loader primarily cares about **program headers / segments**.

Inspect them with:

```bash
readelf -l example
```

You may see:

```text
Program Headers:

Type     Offset   VirtAddr
LOAD     ...
LOAD     ...
LOAD     ...
LOAD     ...

Section to Segment mapping:
...
```

The `PT_LOAD` segments tell Linux which portions of the ELF need to be mapped into memory.

---

# 10. Why Segments Matter

Suppose the ELF has:

```text
.text
.rodata
.data
.bss
```

Linux doesn't necessarily create one virtual-memory mapping for every section.

Instead, sections are grouped into loadable segments according to their required permissions.

Conceptually:

```text
ELF sections:

.text
.rodata
.data
.bss

        │
        ▼

ELF LOAD segments:

┌──────────────────────┐
│ .text                │
│ .rodata              │
└──────────────────────┘
          │
          │ r-x / r--
          ▼

┌──────────────────────┐
│ .data                │
│ .bss                 │
└──────────────────────┘
          │
          │ rw-
          ▼
```

This is why **sections and memory mappings are not the same thing**.

---

# 11. The ELF-to-Process Transformation

The entire process can be visualized as:

```text
               ELF FILE

        ┌──────────────────┐
        │ ELF header       │
        ├──────────────────┤
        │ program headers  │
        ├──────────────────┤
        │ .text            │
        │ .rodata          │
        │ .data            │
        │ .bss             │
        └──────────────────┘
                 │
                 │ execve()
                 ▼
        ┌──────────────────┐
        │ Linux ELF loader │
        └──────────────────┘
                 │
                 ▼
        PROCESS ADDRESS SPACE

        ┌──────────────────┐
        │ stack            │
        ├──────────────────┤
        │ mmap/shared libs │
        ├──────────────────┤
        │ heap             │
        ├──────────────────┤
        │ .bss             │
        │ .data            │
        │ .rodata          │
        │ .text            │
        └──────────────────┘
```

---

# 12. Where Does the Heap Come From?

This is where the distinction becomes interesting.

The heap is **not normally an ELF section**.

The ELF contains things like:

```text
.text
.rodata
.data
.bss
```

but not:

```text
.heap
```

The traditional process heap begins around the end of the program's data/BSS area.

Conceptually:

```text
ELF-loaded data
       │
       ▼
    .bss end
       │
       ▼
     heap
       │
       │ grows
       ▼
```

Linux historically provides the `brk` system call for manipulating the end of the process's data segment.

You can observe it indirectly with:

```bash
strace ./example
```

Although modern allocators don't necessarily use `brk()` for every allocation.

---

# 13. `malloc()` Is Not a System Call

This is another important point.

When you write:

```c
malloc(100);
```

your program normally calls a **userspace allocator**.

Conceptually:

```text
your code
   │
   ▼
malloc()
   │
   ▼
C allocator
   │
   ├── reuse existing memory
   │
   ├── brk()
   │
   └── mmap()
```

The allocator decides how to obtain memory from the kernel.

Therefore:

> **`malloc()` is a library/allocator operation, not simply a direct "allocate 100 bytes from Linux" system call.**

---

# 14. `mmap()` and the Heap

Modern allocators can obtain memory from Linux using `mmap()`.

For example:

```text
malloc()
   │
   ▼
allocator
   │
   ▼
mmap()
   │
   ▼
new virtual memory mapping
```

Large allocations are often handled differently from small allocations.

The exact behavior depends on the allocator.

On a typical Linux system using glibc, the allocator may use both:

```text
brk()
mmap()
```

---

# 15. Looking at the Actual Process

Linux gives us a wonderful way to see this.

Run:

```bash
cat /proc/self/maps
```

You'll get output resembling:

```text
55a1...-55a2... r--p ... /program
55a2...-55a3... r-xp ... /program
55a3...-55a4... r--p ... /program
55a4...-55a5... rw-p ... /program
55a5...-55a6... rw-p ... [heap]

7f...-7f... r-xp ... /lib/x86_64-linux-gnu/libc.so.6
...

7fff...-8000... rw-p ... [stack]
```

The exact addresses vary because of ASLR.

---

# 16. Understanding `/proc/PID/maps`

A line looks roughly like:

```text
address-start-address-end permissions offset device inode pathname
```

For example:

```text
55a20000-55a21000 r-xp 00001000 ... /program
```

The permissions:

```text
r-xp
```

mean:

```text
r = readable
w = writable
x = executable
p = private
s = shared
```

Special mappings may have names:

```text
[heap]
[stack]
[vvar]
[vdso]
[vsyscall]
```

---

# 17. The Actual Process Layout

A typical modern Linux process might therefore look more like:

```text
HIGH ADDRESS
────────────────────────────────────

7fff... ┌──────────────────────────┐
        │          stack           │
        │                          │
        │       ↓ grows down       │
        └──────────────────────────┘

        ┌──────────────────────────┐
        │ thread stacks            │
        ├──────────────────────────┤
        │ shared libraries         │
        ├──────────────────────────┤
        │ dynamic mmap allocations │
        ├──────────────────────────┤
        │ anonymous mappings       │
        └──────────────────────────┘

        ... unused address space ...

55xx... ┌──────────────────────────┐
        │           heap           │
        │       ↑ grows up         │
        ├──────────────────────────┤
        │ .bss                     │
        ├──────────────────────────┤
        │ .data                    │
        ├──────────────────────────┤
        │ .rodata                  │
        ├──────────────────────────┤
        │ .text                    │
        └──────────────────────────┘

LOW ADDRESS
```

Again, this is a conceptual layout rather than a fixed address map.

---

# 18. What Happens When Linux Starts the Program?

When you execute:

```bash
./example
```

the shell eventually performs something equivalent to:

```c
execve("./example", argv, envp);
```

Linux then:

1. Reads the ELF header.
2. Validates the executable.
3. Reads the program headers.
4. Creates a new virtual address space.
5. Maps `PT_LOAD` segments.
6. Sets appropriate page permissions.
7. Maps the dynamic linker if required.
8. Creates the initial stack.
9. Places `argv`, `envp`, and auxiliary information on the stack.
10. Transfers control to the ELF entry point.

Conceptually:

```text
execve()
   │
   ▼
ELF loader
   │
   ├── map executable
   │
   ├── map dynamic linker
   │
   ├── create stack
   │
   ├── setup argv/envp
   │
   └── jump to entry point
             │
             ▼
           _start
             │
             ▼
           main()
```

---

# 19. `_start` vs `main()`

A very important detail:

Linux does **not** directly call:

```c
main();
```

The ELF entry point is usually something like:

```text
_start
```

For a dynamically linked C program, startup code eventually invokes the C runtime, which calls `main()`.

Conceptually:

```text
Linux
  │
  ▼
ELF entry point
  │
  ▼
_start
  │
  ▼
C runtime initialization
  │
  ▼
main()
```

You can inspect the entry point:

```bash
readelf -h example
```

Look for:

```text
Entry point address:
```

---

# 20. The Initial Stack Is More Than Local Variables

When Linux starts your program, the initial stack contains important process startup information.

Conceptually:

```text
STACK

┌──────────────────────┐
│ argc                 │
├──────────────────────┤
│ argv[]               │
├──────────────────────┤
│ NULL                 │
├──────────────────────┤
│ envp[]               │
├──────────────────────┤
│ NULL                 │
├──────────────────────┤
│ auxiliary vector     │
├──────────────────────┤
│ strings              │
└──────────────────────┘
```

This is how startup code gets information such as:

```text
argument count
arguments
environment
kernel-provided auxiliary information
```

---

# 21. What Is Actually in a Stack Frame?

Consider:

```c
int add(int a, int b)
{
    int result = a + b;

    return result;
}
```

You might imagine:

```text
STACK FRAME

┌─────────────────────┐
│ return address      │
├─────────────────────┤
│ saved registers     │
├─────────────────────┤
│ a                   │
├─────────────────────┤
│ b                   │
├─────────────────────┤
│ result              │
└─────────────────────┘
```

But on x86-64 Linux, this is not necessarily the actual layout.

The System V AMD64 ABI passes the first integer arguments in registers such as:

```text
RDI
RSI
RDX
RCX
R8
R9
```

So `a` and `b` may never be stored on the stack at all.

The compiler may generate something closer to:

```text
RDI = a
RSI = b

RAX = RDI + RSI
```

and return.

This is why you should distinguish:

> **source-level stack concepts**

from:

> **actual machine-level storage.**

---

# 22. Stack Frames Are a Compiler/ABI Concept

The stack is closely connected to the calling convention.

A function call may involve:

```text
caller
  │
  ├── place arguments in registers/stack
  │
  ├── CALL instruction
  │
  ▼
callee
  │
  ├── establish stack frame if needed
  │
  ├── execute
  │
  └── RET
```

The exact details depend on:

* CPU architecture
* ABI
* compiler
* optimization level

For Linux x86-64, the dominant ABI is the **System V AMD64 ABI**.

---

# 23. C: Inspecting the Memory

You can make the layout visible yourself.

Example:

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int global_data = 42;
int global_bss;

const char constant[] = "hello";

void function(void)
{
    int local = 123;

    int *heap = malloc(sizeof(int));
    *heap = 456;

    printf("function : %p\n", (void *)function);
    printf("constant : %p\n", (void *)constant);
    printf("data     : %p\n", (void *)&global_data);
    printf("bss      : %p\n", (void *)&global_bss);
    printf("heap     : %p\n", (void *)heap);
    printf("stack    : %p\n", (void *)&local);

    free(heap);
}

int main(void)
{
    function();
}
```

You should see addresses with a rough ordering like:

```text
function : 0x55...
constant : 0x55...
data     : 0x55...
bss      : 0x55...
heap     : 0x55...
stack    : 0x7fff...
```

The exact values depend on the system and ASLR.

---

# 24. Disable ASLR for Experiments

For educational experiments, predictable addresses can be useful.

You can temporarily disable ASLR for a process with:

```bash
setarch "$(uname -m)" -R ./example
```

Or inspect the system setting:

```bash
cat /proc/sys/kernel/randomize_va_space
```

Typical values include:

```text
0 = disabled
1 = conservative
2 = full
```

Don't disable ASLR globally just for experimentation unless you understand the security implications.

---

# 25. Inspect the ELF Sections

Run:

```bash
readelf -S example
```

You'll see something conceptually like:

```text
[Nr] Name       Type
     .text      PROGBITS
     .rodata    PROGBITS
     .data      PROGBITS
     .bss       NOBITS
```

Notice:

```text
.bss → NOBITS
```

That's a beautiful ELF detail.

The section exists conceptually in the process, but its zero-filled contents don't have to occupy space in the executable file.

---

# 26. Inspect ELF Program Headers

Run:

```bash
readelf -l example
```

Look for:

```text
LOAD
LOAD
LOAD
LOAD
```

The important entries are `PT_LOAD` segments.

Conceptually:

```text
ELF

             Program Headers
                   │
       ┌───────────┴───────────┐
       │                       │
       ▼                       ▼

   LOAD segment             LOAD segment
   executable               writable

   .text                     .data
   .rodata                   .bss
```

These tell the Linux loader what needs to be mapped into memory.

---

# 27. Sections Are Mostly a Linker Concept

This is an extremely useful mental model:

```text
Sections
    ↓
linker / ELF organization

Segments
    ↓
loader / runtime memory mapping
```

For example:

```text
.text
.rodata
.data
.bss
```

are sections.

Whereas:

```text
PT_LOAD
PT_INTERP
PT_DYNAMIC
PT_PHDR
PT_GNU_STACK
PT_GNU_RELRO
```

are program headers/segments or related entries.

The kernel's ELF loader is primarily interested in the program headers.

---

# 28. `PT_GNU_STACK`

Modern Linux ELF files commonly contain:

```text
GNU_STACK
```

You can see it with:

```bash
readelf -l example
```

It communicates stack-related properties, particularly whether the program expects an executable stack.

Ideally:

```text
GNU_STACK
RW
```

rather than:

```text
RWE
```

because an executable stack is generally unnecessary and undesirable.

This connects ELF metadata directly to the permissions of the runtime stack.

---

# 29. `PT_GNU_RELRO`

You may also see:

```text
GNU_RELRO
```

This is related to **RELRO**, a hardening mechanism.

Some dynamically linked data is writable during relocation, then made read-only after startup.

Conceptually:

```text
startup

RELRO
  │
  │ writable
  ▼
relocations applied
  │
  ▼
mprotect()
  │
  ▼
read-only
```

This is another example of ELF metadata influencing runtime memory protection.

---

# 30. Shared Libraries

A dynamically linked program isn't just your ELF.

For example:

```c
printf("hello\n");
```

usually involves glibc.

Linux maps shared libraries into the process:

```text
PROCESS

┌──────────────────────────┐
│ stack                    │
├──────────────────────────┤
│ libc.so                  │
├──────────────────────────┤
│ dynamic linker           │
├──────────────────────────┤
│ other shared libraries   │
├──────────────────────────┤
│ heap                     │
├──────────────────────────┤
│ executable               │
└──────────────────────────┘
```

You can inspect them with:

```bash
ldd ./example
```

and see their mappings with:

```bash
cat /proc/$(pidof example)/maps
```

For a short-lived process, use:

```bash
cat /proc/self/maps
```

inside the program or pause it with `sleep()`.

---

# 31. Rust Does the Same Thing

Rust isn't fundamentally different at the Linux process level.

Compile:

```bash
rustc main.rs
```

and inspect:

```bash
file main
readelf -h main
readelf -S main
readelf -l main
```

You'll still have concepts corresponding to:

```text
.text
.rodata
.data
.bss
```

and Linux will still create:

```text
code mappings
data mappings
heap
stack
shared libraries
mmap regions
```

Rust's memory-safety model doesn't require a different Linux virtual-memory architecture.

---

# 32. Rust Heap Example

```rust
fn main() {
    let x = Box::new(42);

    println!("{}", x);
}
```

Conceptually:

```text
Linux Process

STACK
┌─────────────────────┐
│ x / Box             │
│ pointer             │─────────┐
└─────────────────────┘         │
                                ▼
                             HEAP
                         ┌──────────┐
                         │   42     │
                         └──────────┘
```

When `x` goes out of scope:

```text
Box
 │
 ▼
Drop
 │
 ▼
allocator
 │
 ▼
memory returned
```

Rust's allocator ultimately obtains memory through OS mechanisms such as `mmap` and/or `brk`, depending on the allocator and allocation.

---

# 33. Rust `Vec`

Consider:

```rust
fn main() {
    let numbers = vec![10, 20, 30, 40];

    println!("{}", numbers[2]);
}
```

Conceptually:

```text
STACK

numbers
┌──────────────────────┐
│ ptr ─────────────────┼──────┐
│ len = 4              │      │
│ capacity = 4         │      │
└──────────────────────┘      │
                              ▼
                           HEAP
                      ┌────────────────┐
                      │ 10 20 30 40    │
                      └────────────────┘
```

The `Vec` itself is a small value.

Its dynamically sized buffer is the heap allocation.

---

# 34. A Complete Mental Model

Put everything together:

```text
                         LINUX PROCESS
┌────────────────────────────────────────────────────┐
│                                                    │
│                         STACK                      │
│                                                    │
│    function frames                                 │
│    local state                                     │
│    argv/envp/startup data                          │
│                                                    │
│                     ↓ grows down                   │
├────────────────────────────────────────────────────┤
│                                                    │
│                    mmap regions                    │
│                                                    │
│    shared libraries                                │
│    thread stacks                                   │
│    anonymous mappings                               │
│    large allocator allocations                     │
│    files mapped with mmap                          │
│                                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│                       HEAP                         │
│                                                    │
│    malloc() allocations                            │
│    allocator metadata                              │
│                                                    │
│                     ↑ grows up                     │
├────────────────────────────────────────────────────┤
│ .bss                                               │
│                                                    │
│ zero-initialized global/static data                │
├────────────────────────────────────────────────────┤
│ .data                                              │
│                                                    │
│ initialized writable global/static data            │
├────────────────────────────────────────────────────┤
│ .rodata                                            │
│                                                    │
│ read-only constants                                │
├────────────────────────────────────────────────────┤
│ .text                                              │
│                                                    │
│ executable machine code                            │
└────────────────────────────────────────────────────┘
```

But remember:

```text
ELF sections
      ≠
Linux memory regions
```

The executable's sections are organized into loadable segments, and Linux creates additional runtime mappings that don't exist as ELF sections.

---

# 35. The Whole Chain

The most useful way to understand this topic is as a chain:

```text
C / Rust source code
        │
        ▼
compiler
        │
        ▼
machine code + ELF
        │
        ├── sections
        │     ├── .text
        │     ├── .rodata
        │     ├── .data
        │     └── .bss
        │
        └── program headers
              └── PT_LOAD
                       │
                       ▼
                  Linux loader
                       │
                       ▼
               virtual address space
                       │
          ┌────────────┼─────────────┐
          ▼            ▼             ▼
        code         heap          stack
          │            │             │
          ▼            ▼             ▼
      ELF mappings   allocator    call frames
                       │
                  ┌────┴────┐
                  ▼         ▼
                brk()     mmap()
                  │         │
                  └────┬────┘
                       ▼
                  Linux VM
                       │
                       ▼
                  page tables
                       │
                       ▼
                  physical RAM
```

That's the connection between **C/Rust memory**, **ELF**, and **Linux virtual memory**.

---

# 36. The Most Important Distinctions

There are several concepts that are easy to accidentally conflate:

### Stack

A runtime memory region used heavily for function-call state.

```text
function calls
     ↓
stack frames
```

### Heap

Dynamically managed memory.

```text
malloc / allocator
       ↓
dynamic objects
```

### ELF sections

Linker/executable organization.

```text
.text
.rodata
.data
.bss
```

### ELF segments

Information used by the loader to construct process mappings.

```text
PT_LOAD
PT_INTERP
PT_DYNAMIC
...
```

### Virtual memory

The address space visible to the process.

```text
virtual address
       ↓
page table
       ↓
physical address
```

These are **different layers**.

---

# 37. A Practical Experiment

If you want to see this yourself on Linux, compile the following:

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int data = 42;
int bss;

const char rodata[] = "hello";

void code(void)
{
}

int main(void)
{
    int stack = 123;
    int *heap = malloc(sizeof(int));

    *heap = 456;

    printf("code   : %p\n", (void *)code);
    printf("rodata : %p\n", (void *)rodata);
    printf("data   : %p\n", (void *)&data);
    printf("bss    : %p\n", (void *)&bss);
    printf("heap   : %p\n", (void *)heap);
    printf("stack  : %p\n", (void *)&stack);

    printf("\nPID: %d\n", getpid());

    getchar();

    free(heap);
}
```

Compile:

```bash
gcc -g -O0 -o memory memory.c
```

Run:

```bash
./memory
```

While it is waiting at `getchar()`, inspect it from another terminal:

```bash
cat /proc/<PID>/maps
```

Then:

```bash
readelf -S memory
```

and:

```bash
readelf -l memory
```

Finally:

```bash
objdump -h memory
```

You can now correlate:

```text
C variable
    ↓
ELF section
    ↓
ELF LOAD segment
    ↓
Linux virtual-memory mapping
    ↓
actual virtual address
```

That experiment is one of the best ways to make the stack/heap/ELF relationship concrete.

---

# 38. Final Mental Model

Don't memorize:

> "Stack is high memory and heap is low memory."

That's an oversimplification.

Instead remember:

```text
                  ELF FILE
                     │
             program headers
                     │
                     ▼
               Linux loader
                     │
                     ▼
             VIRTUAL ADDRESS SPACE
                     │
       ┌─────────────┼──────────────┐
       │             │              │
       ▼             ▼              ▼
     CODE           HEAP          STACK
       │             │              │
       │             │              │
     ELF          allocator      functions
    segments       │              │
                   │              │
              malloc/Box      local state
                   │
              brk/mmap
                   │
                   ▼
              Linux VM
                   │
                   ▼
              page tables
                   │
                   ▼
               physical RAM
```

And the key C/Rust difference is:

```text
C

pointer ──► allocation
              │
              ▼
        programmer must
        manage lifetime


Rust

Box/Vec/String ──► allocation
                       │
                       ▼
                 ownership system
                       │
                       ▼
                     Drop
                       │
                       ▼
                  deallocation
```

So **stack vs heap** is only one layer of the story. Once you connect it to **ELF segments → Linux virtual address mappings → `malloc`/`mmap`/`brk` → page tables → physical memory**, you get the actual systems-level picture of where your C and Rust programs live in a Linux process.

