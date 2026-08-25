---

title: "C Programming Language Cheat Sheet"
category: "Programming"
subcategory: "Languages"
tags:

* "C"
* "C programming"
* "C23"
* "syntax"
* "pointers"
* "memory"
* "standard library"
  type: "reference"

---

# C Programming Language Cheat Sheet

## 1. Program Structure

```c
#include <stdio.h>

int main(void)
{
    printf("Hello, world!\n");
    return 0;
}
```

Common compilation:

```bash
gcc -std=c23 -Wall -Wextra -O2 main.c -o main
```

---

## 2. Basic Types

| Type             |           Typical size | Example               |
| ---------------- | ---------------------: | --------------------- |
| `char`           |                 1 byte | `'A'`                 |
| `short`          |              ≥ 2 bytes | `short x = 10;`       |
| `int`            |              ≥ 2 bytes | `int x = 10;`         |
| `long`           |              ≥ 4 bytes | `long x = 10L;`       |
| `long long`      |              ≥ 8 bytes | `long long x = 10LL;` |
| `float`          |     ≥ 6 decimal digits | `3.14f`               |
| `double`         |    ≥ 10 decimal digits | `3.14`                |
| `_Bool` / `bool` | implementation-defined | `true`                |
| `void`           |               no value | `void f(void)`        |

For portable exact-width integers:

```c
#include <stdint.h>

int8_t
uint8_t
int16_t
uint16_t
int32_t
uint32_t
int64_t
uint64_t
```

---

## 3. Variables and Constants

```c
int x = 10;
double pi = 3.14159;
char c = 'A';

const int max = 100;
```

Multiple declarations:

```c
int x = 1, y = 2, z = 3;
```

Type inference with C23:

```c
auto x = 42;
```

In C23, `auto` can be used for type inference, but it is **not** the same as C++'s `auto` semantics in all respects.

---

## 4. Operators

### Arithmetic

```c
a + b
a - b
a * b
a / b
a % b
```

### Comparison

```c
a == b
a != b
a < b
a <= b
a > b
a >= b
```

### Logical

```c
a && b
a || b
!a
```

### Bitwise

```c
a & b
a | b
a ^ b
~a
a << n
a >> n
```

### Assignment

```c
x = 10;
x += 5;
x -= 5;
x *= 5;
x /= 5;
x %= 5;
x &= mask;
x |= mask;
x ^= mask;
x <<= 1;
x >>= 1;
```

### Increment/decrement

```c
i++;
++i;

i--;
--i;
```

---

## 5. Control Flow

### `if`

```c
if (x > 10) {
    printf("large\n");
} else if (x > 0) {
    printf("positive\n");
} else {
    printf("non-positive\n");
}
```

### `switch`

```c
switch (command) {
case 1:
    foo();
    break;

case 2:
    bar();
    break;

default:
    baz();
    break;
}
```

### `while`

```c
while (condition) {
    work();
}
```

### `do ... while`

```c
do {
    work();
} while (condition);
```

### `for`

```c
for (int i = 0; i < 10; i++) {
    printf("%d\n", i);
}
```

### `break` / `continue`

```c
for (...) {
    if (error)
        break;

    if (skip)
        continue;
}
```

---

## 6. Functions

Declaration:

```c
int add(int a, int b);
```

Definition:

```c
int add(int a, int b)
{
    return a + b;
}
```

No parameters:

```c
void foo(void)
{
}
```

Returning nothing:

```c
void log_message(const char *message)
{
    printf("%s\n", message);
}
```

C passes arguments **by value**.

To modify an object in the caller, pass a pointer:

```c
void increment(int *x)
{
    (*x)++;
}

int n = 10;
increment(&n);
```

---

# 7. Arrays

```c
int numbers[5] = {1, 2, 3, 4, 5};
```

Access:

```c
numbers[0]
numbers[4]
```

Size:

```c
sizeof numbers
```

Number of elements:

```c
sizeof numbers / sizeof numbers[0]
```

Multidimensional arrays:

```c
int matrix[3][4];
matrix[1][2] = 42;
```

Arrays are contiguous:

```text
int numbers[4]

+-----+-----+-----+-----+
|  10 |  20 |  30 |  40 |
+-----+-----+-----+-----+
```

---

# 8. Pointers

A pointer stores an address.

```c
int x = 42;
int *p = &x;
```

Dereference:

```c
printf("%d\n", *p);
```

Modify through pointer:

```c
*p = 100;
```

Conceptually:

```text
x
+------+
|  42  |
+------+
   ^
   |
   |
+------+
|  p   |
+------+
```

`&` obtains an address:

```c
&x
```

`*` dereferences a pointer:

```c
*p
```

---

## 9. Pointer Arithmetic

For:

```c
int numbers[5];
int *p = numbers;
```

Then:

```c
p + 1
```

points to the next `int`, not merely the next byte.

```c
*(p + 2)
```

is equivalent to:

```c
numbers[2]
```

Pointer subtraction:

```c
ptrdiff_t distance = p2 - p1;
```

Pointer arithmetic is only defined within the same array object, subject to the standard's rules.

---

# 10. Strings

C strings are arrays of characters terminated by `'\0'`.

```c
char name[] = "Alice";
```

Memory:

```text
'A' 'l' 'i' 'c' 'e' '\0'
```

String literal:

```c
const char *name = "Alice";
```

Useful functions:

```c
strlen(s)
strcmp(a, b)
strncmp(a, b, n)
strcpy(dst, src)
strncpy(dst, src, n)
strcat(dst, src)
strchr(s, c)
strstr(s, substring)
```

Include:

```c
#include <string.h>
```

Be careful with functions that do not know the destination buffer's size.

---

# 11. Dynamic Memory

Include:

```c
#include <stdlib.h>
```

Allocate:

```c
int *p = malloc(10 * sizeof *p);
```

Initialize to zero:

```c
int *p = calloc(10, sizeof *p);
```

Resize:

```c
p = realloc(p, 20 * sizeof *p);
```

Release:

```c
free(p);
p = NULL;
```

Typical pattern:

```c
int *numbers = malloc(n * sizeof *numbers);

if (numbers == NULL) {
    /* allocation failed */
    return 1;
}

/* use numbers */

free(numbers);
```

Important:

> Every successful allocation should have a clearly defined owner responsible for eventually calling `free()`.

---

# 12. `struct`

Define a structure:

```c
struct Point {
    int x;
    int y;
};
```

Create:

```c
struct Point p = {
    .x = 10,
    .y = 20
};
```

Access:

```c
p.x
p.y
```

Pointer to structure:

```c
struct Point *p = &point;

p->x
p->y
```

Equivalent:

```c
(*p).x
```

---

# 13. `typedef`

```c
typedef struct {
    int x;
    int y;
} Point;
```

Now:

```c
Point p = {
    .x = 10,
    .y = 20
};
```

Common pattern:

```c
typedef struct {
    char *name;
    int age;
} Person;
```

---

# 14. `enum`

```c
enum Color {
    RED,
    GREEN,
    BLUE
};
```

Use:

```c
enum Color color = GREEN;
```

Explicit values:

```c
enum Status {
    STATUS_OK = 0,
    STATUS_ERROR = 1,
    STATUS_BUSY = 2
};
```

---

# 15. `union`

A union stores different members in the same memory location.

```c
union Value {
    int i;
    float f;
    char c;
};
```

Only one member should generally be treated as the active representation according to the applicable C rules.

Useful for:

* tagged unions
* low-level representations
* memory-efficient variants
* hardware interfaces

---

# 16. `const`

```c
const int x = 10;
```

Pointer to constant data:

```c
const int *p;
```

You cannot modify the pointed-to `int` through `p`.

Constant pointer:

```c
int *const p = &x;
```

The pointer itself cannot be changed.

Both:

```c
const int *const p = ...;
```

Neither the pointer nor the pointed-to object can be modified through `p`.

---

# 17. Storage Classes and Qualifiers

Common keywords:

```c
const
static
extern
_Thread_local
volatile
restrict
```

### `static`

At file scope:

```c
static int counter;
```

The identifier has internal linkage.

Inside a function:

```c
void foo(void)
{
    static int count = 0;
    count++;
}
```

`count` retains its value between function calls.

### `extern`

Declares an object/function defined elsewhere:

```c
extern int global_counter;
```

### `restrict`

Used to communicate pointer aliasing assumptions:

```c
void copy(size_t n,
          int *restrict dst,
          const int *restrict src);
```

When used correctly, this can enable optimization.

### `volatile`

Tells the implementation that accesses to the object have observable effects that must not simply be optimized away.

It is commonly relevant to:

* memory-mapped I/O
* certain signal-handler interactions
* hardware registers

**`volatile` is not a threading synchronization primitive.**

---

# 18. Preprocessor

Include headers:

```c
#include <stdio.h>
#include "myheader.h"
```

Macros:

```c
#define MAX_SIZE 1024
```

Function-like macro:

```c
#define SQUARE(x) ((x) * (x))
```

Conditional compilation:

```c
#ifdef DEBUG
    printf("debug\n");
#endif
```

Header guard:

```c
#ifndef MY_HEADER_H
#define MY_HEADER_H

/* declarations */

#endif
```

Modern projects may use `#pragma once`, although it is not part of the ISO C standard.

---

# 19. Header Files

`foo.h`:

```c
#ifndef FOO_H
#define FOO_H

int add(int a, int b);

#endif
```

`foo.c`:

```c
#include "foo.h"

int add(int a, int b)
{
    return a + b;
}
```

`main.c`:

```c
#include <stdio.h>
#include "foo.h"

int main(void)
{
    printf("%d\n", add(2, 3));
}
```

Compile:

```bash
gcc -std=c23 -Wall -Wextra main.c foo.c -o program
```

---

# 20. Input / Output

```c
#include <stdio.h>
```

Output:

```c
printf("value = %d\n", x);
puts("hello");
putchar('A');
```

Input:

```c
scanf("%d", &x);
```

Character input:

```c
int c = getchar();
```

File operations:

```c
FILE *f = fopen("data.txt", "r");

if (f == NULL) {
    /* error */
}

fclose(f);
```

Read:

```c
fgets(buffer, sizeof buffer, f);
```

Write:

```c
fprintf(f, "value=%d\n", x);
```

---

# 21. `printf` Format Specifiers

| Type            | Format |
| --------------- | ------ |
| `int`           | `%d`   |
| `unsigned int`  | `%u`   |
| `long`          | `%ld`  |
| `unsigned long` | `%lu`  |
| `long long`     | `%lld` |
| `float`         | `%f`   |
| `double`        | `%f`   |
| `char`          | `%c`   |
| string          | `%s`   |
| pointer         | `%p`   |
| hexadecimal     | `%x`   |
| octal           | `%o`   |
| `size_t`        | `%zu`  |
| `ptrdiff_t`     | `%td`  |

For a pointer:

```c
printf("%p\n", (void *)ptr);
```

For fixed-width integers, use `<inttypes.h>` macros such as:

```c
printf("%" PRId64 "\n", value);
```

---

# 22. File Descriptors and POSIX I/O

On POSIX systems, low-level I/O uses file descriptors.

```c
#include <unistd.h>

ssize_t n = read(fd, buffer, sizeof buffer);
ssize_t written = write(fd, buffer, size);

close(fd);
```

Common descriptors:

```text
0 = stdin
1 = stdout
2 = stderr
```

This is different from the ISO C `FILE *` API.

```text
ISO C                  POSIX

FILE *                  int fd
  |                       |
  v                       v
fopen/fread/fwrite      open/read/write
```

---

# 23. Error Handling

Many C APIs communicate errors through return values.

```c
FILE *f = fopen("file.txt", "r");

if (f == NULL) {
    perror("fopen");
    return 1;
}
```

For system calls and POSIX APIs, `errno` is commonly used:

```c
#include <errno.h>
#include <stdio.h>

if (something_failed) {
    perror("operation");
}
```

For general application APIs, explicit error-return conventions are often preferable to relying exclusively on global error state.

---

# 24. Function Pointers

A function pointer stores the address of a function.

```c
int add(int a, int b)
{
    return a + b;
}

int (*operation)(int, int) = add;

int result = operation(2, 3);
```

Useful for:

* callbacks
* dispatch tables
* state machines
* plugin interfaces
* generic algorithms

Example:

```c
void apply(int *array,
           size_t n,
           void (*fn)(int *))
{
    for (size_t i = 0; i < n; i++)
        fn(&array[i]);
}
```

---

# 25. Variadic Functions

Functions can accept a variable number of arguments.

```c
#include <stdarg.h>

int sum(int count, ...)
{
    va_list args;
    va_start(args, count);

    int result = 0;

    for (int i = 0; i < count; i++)
        result += va_arg(args, int);

    va_end(args);

    return result;
}
```

Usage:

```c
sum(3, 10, 20, 30);
```

`printf()` itself is a variadic function.

---

# 26. Bit Manipulation

Set bit:

```c
x |= (1u << n);
```

Clear bit:

```c
x &= ~(1u << n);
```

Toggle bit:

```c
x ^= (1u << n);
```

Test bit:

```c
if (x & (1u << n)) {
    /* set */
}
```

Extract bits:

```c
unsigned value = (x >> shift) & mask;
```

These operations are particularly common in systems programming.

---

# 27. Memory Layout

A typical process looks approximately like:

```text
High addresses
+-----------------------+
| Stack                 |
|         ↓             |
+-----------------------+
|                       |
|     mmap / libraries  |
|                       |
+-----------------------+
|         ↑             |
| Heap                  |
+-----------------------+
| BSS                   |
+-----------------------+
| Data                  |
+-----------------------+
| Read-only data        |
+-----------------------+
| Code / text           |
+-----------------------+
Low addresses
```

This is a conceptual layout; the exact arrangement depends on the platform, executable format, linker, kernel, ASLR, and other factors.

---

# 28. Undefined Behavior

One of the most important concepts in C is **undefined behavior (UB)**.

Examples include:

```c
int a[3];

a[5] = 10;        // UB
```

Using an object after freeing it:

```c
int *p = malloc(sizeof *p);
free(p);

*p = 10;          // UB
```

Signed integer overflow:

```c
int x = INT_MAX;
x++;              // UB
```

Dereferencing an invalid pointer:

```c
int *p = NULL;
*p = 42;          // UB
```

Undefined behavior means the C standard imposes **no requirements** on what happens.

It does not simply mean:

> "The program will probably crash."

A compiler may exploit the assumption that valid C programs do not perform undefined operations.

---

# 29. Common Pointer Mistakes

### Uninitialized pointer

```c
int *p;
*p = 10;    // UB
```

### Dangling pointer

```c
int *p = malloc(sizeof *p);
free(p);

*p = 10;    // UB
```

### Memory leak

```c
int *p = malloc(sizeof *p);

/* forgot free(p) */
```

### Returning address of a local variable

```c
int *foo(void)
{
    int x = 10;
    return &x;      // dangling pointer
}
```

### Buffer overflow

```c
char buffer[8];

strcpy(buffer, "This is too long");
```

---

# 30. Useful Standard Library Headers

| Header          | Purpose                                 |
| --------------- | --------------------------------------- |
| `<stdio.h>`     | I/O                                     |
| `<stdlib.h>`    | allocation, conversion, process control |
| `<string.h>`    | strings and memory                      |
| `<stdint.h>`    | fixed-width integers                    |
| `<inttypes.h>`  | integer formatting                      |
| `<stdbool.h>`   | boolean support                         |
| `<stddef.h>`    | `size_t`, `ptrdiff_t`, `NULL`, etc.     |
| `<stdint.h>`    | integer types                           |
| `<limits.h>`    | integer limits                          |
| `<float.h>`     | floating-point limits                   |
| `<math.h>`      | mathematics                             |
| `<ctype.h>`     | character classification                |
| `<time.h>`      | time                                    |
| `<assert.h>`    | assertions                              |
| `<errno.h>`     | error reporting                         |
| `<stdarg.h>`    | variadic arguments                      |
| `<signal.h>`    | signals                                 |
| `<threads.h>`   | C11 threads                             |
| `<stdatomic.h>` | C11 atomics                             |

---

# 31. C Memory Model — Quick View

Think about objects rather than merely bytes.

```text
Object
 |
 +-- type
 +-- value
 +-- lifetime
 +-- storage duration
 +-- alignment
 +-- effective type
```

Important concepts include:

* object lifetime
* alignment
* pointer validity
* aliasing
* sequencing
* data races
* atomic operations
* undefined behavior

For concurrent C programs, the **C memory model** matters independently of what a particular CPU happens to do.

---

# 32. C Compilation Pipeline

A simplified pipeline:

```text
source.c
   |
   v
Preprocessor
   |
   v
expanded source
   |
   v
Compiler
   |
   v
assembly
   |
   v
Assembler
   |
   v
object file
   |
   v
Linker
   |
   v
executable
```

Typical commands:

```bash
gcc -std=c23 -E main.c       # preprocessing
gcc -std=c23 -S main.c       # assembly
gcc -std=c23 -c main.c       # object file
gcc -std=c23 main.c -o main  # compile + link
```

---

# 33. Useful Compiler Flags

For GCC:

```bash
-std=c23
-Wall
-Wextra
-Wpedantic
-Wconversion
-Wshadow
-Werror
-g
-O0
-O2
-O3
-fsanitize=address
-fsanitize=undefined
```

A useful development command:

```bash
gcc -std=c23 \
    -Wall -Wextra -Wpedantic \
    -g \
    -fsanitize=address,undefined \
    main.c -o main
```

Sanitizers are especially useful for finding memory errors and undefined behavior during testing.

---

# 34. C23 Minimal Reference

Modern C should generally be written against a specific language version when portability matters.

For C23:

```bash
gcc -std=c23
```

The language version matters because features and library facilities differ between:

```text
C90
C99
C11
C17
C23
```

Do not assume that a compiler's default language mode is the same as the C version you intend to target.

---

# 35. Quick Syntax Reference

```c
// variable
int x = 10;

// constant
const int x = 10;

// pointer
int *p = &x;

// array
int a[10];

// string
char s[] = "hello";

// struct
struct Point p;

// typedef
typedef unsigned long ulong;

// enum
enum State { IDLE, RUNNING, STOPPED };

// function
int add(int a, int b);

// function pointer
int (*fn)(int, int);

// dynamic allocation
int *p = malloc(n * sizeof *p);

// release
free(p);

// conditional
if (condition) { }

// loop
for (int i = 0; i < n; i++) { }

// switch
switch (x) {
case 1:
    break;
default:
    break;
}
```

---

# 36. Essential Mental Model

If you remember only a few things about C, remember these:

```text
C program
   |
   +-- values
   |
   +-- objects
   |     |
   |     +-- type
   |     +-- lifetime
   |     +-- storage
   |
   +-- pointers
   |     |
   |     +-- addresses
   |     +-- indirection
   |
   +-- arrays
   |
   +-- functions
   |
   +-- structs
   |
   +-- manual resource management
   |
   +-- explicit control over memory
```

And especially:

> **C gives you direct control over memory and machine-level resources, but that control comes with responsibility for lifetime, bounds, ownership, aliasing, and concurrency correctness.**

## Related Concepts

* C Type System
* Pointers and Pointer Arithmetic
* C Memory Model
* Undefined Behavior
* Dynamic Memory Allocation
* Structs and Unions
* Function Pointers
* C Preprocessor
* C Compilation Model
* Linkers and Object Files
* POSIX APIs
* System Calls
* C Concurrency
* C Atomics
* Memory Management
* Data Structures in C

