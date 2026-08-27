# Rust Smart Pointers

**Category:** Programming
**Subcategory:** Memory
**Tags:** Rust, smart pointers, Box, Rc, Arc, RefCell, ownership, interior mutability
**Type:** concept



## 1. Short Answer

In Rust, a **smart pointer** is a type that behaves somewhat like a pointer but also provides additional ownership, lifetime, memory-management, or access-control semantics.

The most important smart-pointer types are:

| Type         | Main purpose                                       |
| ------------ | -------------------------------------------------- |
| `Box<T>`     | Own a value on the heap                            |
| `Rc<T>`      | Shared ownership in single-threaded code           |
| `Arc<T>`     | Shared ownership across threads                    |
| `Weak<T>`    | Non-owning reference to `Rc`/`Arc` data            |
| `RefCell<T>` | Runtime-checked borrowing / interior mutability    |
| `Cell<T>`    | Interior mutability for small `Copy`-like values   |
| `Mutex<T>`   | Thread-safe interior mutability                    |
| `RwLock<T>`  | Multiple readers or one writer                     |
| `Cow<'a, T>` | Borrow when possible, clone when necessary         |
| `Pin<P>`     | Prevent a value from being moved through a pointer |

The key thing to understand is that these types solve **different problems**.

For example:

```rust
Box<T>     → heap ownership
Rc<T>      → shared ownership
Arc<T>     → thread-safe shared ownership
RefCell<T> → runtime borrow checking
Mutex<T>   → synchronized mutable access
Weak<T>    → non-owning reference
Pin<T>     → stable memory location
```

They can also be **combined**:

```rust
Arc<Mutex<T>>
Rc<RefCell<T>>
Arc<RwLock<T>>
Pin<Box<T>>
```

Understanding why these combinations exist is more important than memorizing the list.

---

# 2. Core Idea

Rust normally enforces ownership and borrowing at compile time:

```rust
let x = String::from("hello");

let y = x;
```

After the move:

```text
x ──X──> String
y ─────> String
```

Only `y` owns the value.

A smart pointer changes the way ownership or access works.

For example:

```rust
let x = Box::new(String::from("hello"));
```

Conceptually:

```text
Stack                    Heap

x
│
│ owns
▼
Box ────────────────> String
```

The `Box` itself is stored wherever the variable is stored, while the `String` object it owns is allocated on the heap.

Other smart pointers introduce other relationships:

```text
Rc<T>

       +------+
       |  T   |
       +------+
        ^    ^
        |    |
       Rc   Rc
```

Multiple `Rc`s can own the same value.

Or:

```text
Arc<Mutex<T>>

        Arc
         |
         v
      +-------+
      | Mutex |
      |   |   |
      |   T   |
      +-------+
```

This allows shared ownership combined with synchronized mutation.

---

# 3. How Smart Pointers Work

A normal reference:

```rust
&T
```

does not own the value.

A smart pointer may own the value and provide additional behavior.

The most useful distinction is:

```text
Reference
    |
    +-- borrows

Smart pointer
    |
    +-- may own
    +-- may share ownership
    +-- may control access
    +-- may manage allocation
    +-- may synchronize access
    +-- may control movement
```

Rust's smart pointers are ordinary Rust types implementing traits such as:

```rust
Deref
DerefMut
Drop
```

when appropriate.

This means a smart pointer can often be used syntactically like a reference.

---

# 4. `Box<T>`

## Purpose

`Box<T>` is the simplest owning smart pointer.

It puts a value on the heap.

```rust
let x = Box::new(42);
```

Conceptually:

```text
Stack                Heap

x
│
▼
Box ───────────────> 42
```

The `Box` owns the heap allocation.

When the `Box` is dropped, the value and allocation are released.

---

## Why use `Box<T>`?

### 1. Explicit heap allocation

```rust
let value = Box::new(100);
```

### 2. Recursive types

Rust needs types to have a statically known size.

This is impossible:

```rust
enum List {
    Cons(i32, List),
    Nil,
}
```

because `List` would contain another `List`, which contains another `List`, indefinitely.

`Box` solves this:

```rust
enum List {
    Cons(i32, Box<List>),
    Nil,
}
```

Now the compiler knows that `Box<List>` has a fixed size.

---

## 3. Trait objects

`Box` is commonly used for dynamically dispatched trait objects:

```rust
trait Animal {
    fn speak(&self);
}

struct Dog;

impl Animal for Dog {
    fn speak(&self) {
        println!("woof");
    }
}

let animal: Box<dyn Animal> = Box::new(Dog);
animal.speak();
```

Conceptually:

```text
Box<dyn Animal>
       |
       +----> Dog object
       |
       +----> vtable information
```

The exact representation is implementation-dependent, but a trait object reference is generally a **fat pointer** containing a data pointer plus metadata such as a vtable pointer.

---

# 5. `Rc<T>`

`Rc<T>` means **Reference Counted**.

It provides **shared ownership**.

```rust
use std::rc::Rc;

let a = Rc::new(String::from("hello"));
let b = Rc::clone(&a);
```

Now:

```text
        +---------+
        | "hello" |
        | count=2 |
        +---------+
          ^     ^
          |     |
         Rc    Rc
          a     b
```

Both `a` and `b` own the same allocation.

When the last `Rc` disappears, the value is dropped.

---

## Why `Rc` exists

Normal ownership allows one owner:

```text
owner
  |
  v
value
```

`Rc` allows:

```text
owner  owner
   \    /
    \  /
    value
```

This is useful for data structures such as:

* graphs
* trees with shared nodes
* DAGs
* shared immutable configuration

---

## `Rc::clone`

Use:

```rust
let b = Rc::clone(&a);
```

rather than thinking of it as cloning the underlying value.

This:

```rust
Rc::clone(&a)
```

normally increments the reference count.

It does **not** clone the `T`.

So:

```rust
let a = Rc::new(String::from("hello"));
let b = Rc::clone(&a);
```

does not create two `String`s.

It creates two owners of one `String`.

---

# 6. `Rc<T>` Is Not Thread-Safe

`Rc<T>` is intended for single-threaded use.

This is important:

```text
Rc<T>
  |
  +-- shared ownership
  |
  +-- NOT thread-safe
```

If you need shared ownership between threads, use:

```rust
Arc<T>
```

instead.

---

# 7. `Arc<T>`

`Arc<T>` means **Atomically Reference Counted**.

It is essentially the thread-safe counterpart of `Rc`.

```rust
use std::sync::Arc;

let a = Arc::new(String::from("hello"));
let b = Arc::clone(&a);
```

Conceptually:

```text
          +---------+
          | "hello" |
          | count=2 |
          +---------+
             ^   ^
             |   |
            Arc Arc
```

The reference count is maintained using atomic operations.

That makes shared ownership possible across threads.

---

## `Rc` vs `Arc`

|                  | `Rc<T>`         | `Arc<T>`        |
| ---------------- | --------------- | --------------- |
| Shared ownership | Yes             | Yes             |
| Thread-safe      | No              | Yes             |
| Reference count  | Non-atomic      | Atomic          |
| Performance      | Lower overhead  | Higher overhead |
| Typical use      | Single-threaded | Multithreaded   |

Use `Rc` unless you actually need cross-thread ownership.

Use `Arc` when ownership crosses thread boundaries.

---

# 8. `Weak<T>`

`Weak<T>` is a **non-owning reference** associated with `Rc<T>` or `Arc<T>`.

This is especially important for avoiding reference cycles.

Consider:

```text
A → B
↑   |
└───┘
```

If both relationships use `Rc`:

```text
A: Rc<B>
B: Rc<A>
```

the reference counts never reach zero.

The objects leak.

---

## `Weak` breaks the cycle

Instead:

```text
A ──Rc──> B
B ──Weak─> A
```

The weak reference does not keep the object alive.

Example:

```rust
use std::rc::{Rc, Weak};

struct Node {
    parent: Weak<Node>,
    children: Vec<Rc<Node>>,
}
```

This is a very common pattern for trees.

```text
        Parent
        /    \
      Rc      Rc
      /        \
   Child      Child
      ^
      |
    Weak
```

Children own the parent relationship conceptually only through a weak link, preventing the ownership cycle.

---

# 9. `RefCell<T>`

`RefCell<T>` provides **interior mutability**.

Normally Rust checks borrowing at compile time:

```rust
let mut x = 10;

let a = &x;
let b = &mut x; // compile-time error
```

`RefCell` moves some of these borrowing checks to runtime.

```rust
use std::cell::RefCell;

let x = RefCell::new(10);

*x.borrow_mut() += 1;
```

The important distinction is:

```text
Normal reference
    ↓
borrow rules checked at compile time

RefCell<T>
    ↓
borrow rules checked at runtime
```

---

## Runtime checking

This is legal:

```rust
let x = RefCell::new(10);

let a = x.borrow();
println!("{a}");
```

But attempting conflicting borrows causes a runtime panic:

```rust
let x = RefCell::new(10);

let a = x.borrow();
let b = x.borrow_mut(); // panic
```

So `RefCell` doesn't remove Rust's borrowing rules.

It **defers their enforcement until runtime**.

---

# 10. `Rc<RefCell<T>>`

This is one of the most important combinations.

`Rc<T>` provides:

```text
shared ownership
```

`RefCell<T>` provides:

```text
mutable access despite shared ownership
```

Together:

```rust
Rc<RefCell<T>>
```

mean approximately:

> Multiple owners can access the same value, and mutation is checked at runtime.

Conceptually:

```text
       Rc       Rc
        \       /
         \     /
        RefCell
           |
           v
           T
```

This is common in single-threaded graph/data-structure implementations.

For example:

```rust
use std::cell::RefCell;
use std::rc::Rc;

let x = Rc::new(RefCell::new(10));

let a = Rc::clone(&x);
let b = Rc::clone(&x);

*a.borrow_mut() += 1;

println!("{}", b.borrow());
```

Both `a` and `b` refer to the same mutable value.

---

# 11. `Cell<T>`

`Cell<T>` is another interior-mutability type.

It is useful when the value can be copied or moved in and out without requiring references to the interior.

Example:

```rust
use std::cell::Cell;

let x = Cell::new(10);

x.set(20);

println!("{}", x.get());
```

The distinction is approximately:

```text
Cell<T>
    |
    +-- get/set values
    +-- no borrowing of interior

RefCell<T>
    |
    +-- borrow()
    +-- borrow_mut()
    +-- runtime borrow checking
```

`Cell` is particularly useful for small `Copy` values such as:

```rust
Cell<bool>
Cell<u32>
Cell<usize>
Cell<Option<T>>
```

when the required operations fit its API.

---

# 12. `Mutex<T>`

`Mutex<T>` provides synchronized mutable access across threads.

```rust
use std::sync::Mutex;

let x = Mutex::new(10);

{
    let mut value = x.lock().unwrap();
    *value += 1;
}
```

Conceptually:

```text
       Thread A
           |
           v
        +-------+
        | Mutex |
        |   T   |
        +-------+
           ^
           |
       Thread B
```

Only one thread can hold the mutex guard at a time.

The guard typically releases the lock when it is dropped.

---

# 13. `Arc<Mutex<T>>`

This is the multithreaded counterpart to:

```text
Rc<RefCell<T>>
```

The roles are:

```text
Rc       → shared ownership
RefCell  → runtime mutable access
```

versus:

```text
Arc      → thread-safe shared ownership
Mutex    → synchronized mutable access
```

Therefore:

```rust
Arc<Mutex<T>>
```

is a very common pattern.

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let counter = Arc::new(Mutex::new(0));

let c = Arc::clone(&counter);

let handle = thread::spawn(move || {
    let mut value = c.lock().unwrap();
    *value += 1;
});

handle.join().unwrap();
```

Conceptually:

```text
              Arc
           /       \
       Thread A   Thread B
           \       /
            \     /
            Mutex
              |
              T
```

---

# 14. `RwLock<T>`

`RwLock<T>` provides two kinds of access:

```text
many readers
OR
one writer
```

Example:

```rust
use std::sync::RwLock;

let value = RwLock::new(42);

let reader1 = value.read().unwrap();
let reader2 = value.read().unwrap();

println!("{reader1}");
println!("{reader2}");
```

Multiple readers can coexist.

But a writer requires exclusive access:

```rust
let mut writer = value.write().unwrap();
*writer += 1;
```

Conceptually:

```text
             RwLock
            /      \
       read       write
       /  \          |
      R1  R2         W
```

---

# 15. `Arc<RwLock<T>>`

This is useful when data is shared across threads and reads are much more common than writes.

```rust
Arc<RwLock<T>>
```

means:

```text
Arc
 ↓
shared ownership between threads

RwLock
 ↓
synchronized read/write access

T
 ↓
actual data
```

For example:

```text
                 Arc
              /       \
          Thread A   Thread B
              \       /
               RwLock
              /     \
          readers   writer
```

---

# 16. `Cow<T>`

`Cow` means **Clone on Write**.

It is different from `Rc`/`Arc`.

`Cow` is useful when you want to:

> Borrow data when possible, but create an owned copy only if modification becomes necessary.

Example:

```rust
use std::borrow::Cow;

fn normalize(input: &str) -> Cow<'_, str> {
    if input.is_ascii() {
        Cow::Borrowed(input)
    } else {
        Cow::Owned(input.to_lowercase())
    }
}
```

Conceptually:

```text
                 Cow
                /   \
        Borrowed     Owned
           |           |
      existing data   clone
```

This is particularly useful for avoiding unnecessary allocations.

---

# 17. `Pin<P>`

`Pin` is one of the more advanced pointer abstractions.

It is used when an object must not be moved in memory through a particular pointer.

Commonly:

```rust
Pin<Box<T>>
```

appears in asynchronous Rust.

The key idea is:

```text
Normal Box<T>

Box ─────> T

T may be moved out/around according to ownership rules.


Pin<Box<T>>

Pin
 |
 v
Box ─────> T

The pointee is guaranteed not to be moved
through the Pin API once pinned.
```

This becomes important for types whose internal state contains self-references or for compiler-generated `Future` state machines that may rely on stable addresses.

`Pin` does **not** mean:

> "This memory can never move under any circumstances."

Its guarantee is more precise: safe code using the pinning API cannot move a pinned `T` out through the pinned pointer unless `T: Unpin` or an appropriate operation is used.

---

# 18. `Deref` and Smart Pointers

Many smart pointers implement `Deref`.

For example:

```rust
let x = Box::new(String::from("hello"));

println!("{}", x.len());
```

You might expect:

```rust
x.len()
```

to require explicitly dereferencing:

```rust
(*x).len()
```

Rust's **deref coercion** and method resolution make the former possible.

Conceptually:

```text
Box<String>
     |
   Deref
     |
     v
  String
```

This is why smart pointers can often behave like references.

---

# 19. `DerefMut`

Mutable smart pointers can additionally implement `DerefMut`.

For example:

```rust
let mut x = Box::new(String::from("hello"));

x.push_str(" world");
```

The compiler can obtain mutable access to the underlying `String` through `DerefMut`.

Conceptually:

```text
&mut Box<T>
      |
  DerefMut
      |
      v
   &mut T
```

---

# 20. `Drop`

Owning smart pointers commonly implement `Drop`.

For example, when:

```rust
{
    let x = Box::new(String::from("hello"));
}
```

`x` goes out of scope.

Rust automatically drops:

```text
Box
 ↓
String
 ↓
heap allocation
```

`Rc` adds reference counting:

```text
Rc count = 3

     ↓ drop

Rc count = 2

     ↓ drop

Rc count = 1

     ↓ drop

Rc count = 0
     ↓
destroy T
```

This is why understanding `Drop` is important when studying smart pointers.

---

# 21. Smart Pointer Combinations

The most useful combinations are:

| Type                     | Meaning                               |
| ------------------------ | ------------------------------------- |
| `Box<T>`                 | Owned heap allocation                 |
| `Rc<T>`                  | Shared ownership, single-threaded     |
| `Arc<T>`                 | Shared ownership, multithreaded       |
| `Rc<RefCell<T>>`         | Shared mutable data, single-threaded  |
| `Arc<Mutex<T>>`          | Shared mutable data, multithreaded    |
| `Arc<RwLock<T>>`         | Shared read/write data, multithreaded |
| `Rc<RefCell<Option<T>>>` | Shared mutable optional state         |
| `Weak<T>`                | Non-owning relationship               |
| `Pin<Box<T>>`            | Heap allocation + pinning             |

A useful way to decode these types is from the outside inward.

For:

```rust
Arc<Mutex<Vec<u8>>>
```

read it as:

```text
Arc
 ↓
shared ownership across threads

Mutex
 ↓
exclusive synchronized access

Vec<u8>
 ↓
actual data
```

---

# 22. Choosing the Right Smart Pointer

A practical decision tree:

```text
Do I need heap allocation?
        |
       yes
        |
        v
      Box<T>
        |
        +-- Need shared ownership?
                |
               yes
                |
        +-------+-------+
        |               |
    Single-threaded   Multi-threaded
        |               |
       Rc              Arc
        |               |
        |          Need mutation?
        |               |
        |          +----+----+
        |          |         |
        |         yes        no
        |          |         |
        |       Mutex/      Arc<T>
        |       RwLock
        |
   Need mutation?
        |
       yes
        |
    RefCell<T>
```

For single-threaded shared mutable data:

```text
Rc<RefCell<T>>
```

For multithreaded shared mutable data:

```text
Arc<Mutex<T>>
```

For mostly-read multithreaded data:

```text
Arc<RwLock<T>>
```

---

# 23. Deep Dive: Ownership vs Mutability

One of the most important conceptual distinctions is that these are **separate dimensions**.

Consider:

```text
Ownership
│
├── unique
│     └── Box<T>
│
└── shared
      ├── Rc<T>
      └── Arc<T>


Mutability
│
├── ordinary borrowing
├── RefCell<T>
├── Cell<T>
├── Mutex<T>
└── RwLock<T>
```

This is why composition is so powerful.

For example:

```rust
Arc<Mutex<T>>
```

combines:

```text
shared ownership
        +
thread-safe mutation
```

while:

```rust
Rc<RefCell<T>>
```

combines:

```text
shared ownership
        +
single-threaded interior mutability
```

---

# 24. Why `Rc<RefCell<T>>` Is Not `Arc<Mutex<T>>`

They look similar:

```text
Rc<RefCell<T>>
Arc<Mutex<T>>
```

but their guarantees are different.

### `Rc<RefCell<T>>`

```text
single-threaded
      +
shared ownership
      +
runtime borrow checking
```

### `Arc<Mutex<T>>`

```text
multi-threaded
      +
atomic shared ownership
      +
synchronization
```

You cannot simply replace one with the other without considering the concurrency model.

---

# 25. Reference Counting and Cycles

Reference counting has an important weakness.

Consider:

```text
A ──Rc──> B
^         |
|         |
└─────────┘
```

Reference counts never reach zero.

Therefore:

```text
Rc
```

and:

```text
Arc
```

can leak memory through cycles.

This is why:

```text
Rc<T>  + Weak<T>
Arc<T> + Weak<T>
```

are designed to work together.

A typical ownership graph is:

```text
Parent
  |
 Rc
  v
Child
  |
Weak
  |
  +----> Parent
```

---

# 26. Smart Pointers and Concurrency

It is tempting to think:

```text
Arc<T>
```

means:

> "T is thread-safe."

It does not.

`Arc<T>` makes **shared ownership** thread-safe.

It does not automatically make `T` safe to mutate concurrently.

For example:

```rust
Arc<Vec<i32>>
```

is useful for sharing immutable data.

But:

```rust
Arc<RefCell<Vec<i32>>>
```

is not a valid general solution for sharing mutable data between threads because `RefCell` is not a thread synchronization primitive.

Instead, use something such as:

```rust
Arc<Mutex<Vec<i32>>>
```

or:

```rust
Arc<RwLock<Vec<i32>>>
```

depending on the access pattern.

---

# 27. Smart Pointers and `Send` / `Sync`

Rust's concurrency safety is strongly connected to two marker traits:

```rust
Send
Sync
```

Very roughly:

### `Send`

A type can be transferred to another thread.

### `Sync`

A type can safely be shared through references between threads.

This explains why:

```text
Rc<T>
```

cannot generally cross thread boundaries.

`Arc<T>` is designed to support this when `T` itself satisfies the required thread-safety constraints.

This is one of the places where Rust's type system prevents an entire class of concurrency bugs.

---

# 28. Smart Pointer vs Reference

A useful comparison:

|                     | `&T`            | `Box<T>`       | `Rc<T>` | `Arc<T>`                  |
| ------------------- | --------------- | -------------- | ------- | ------------------------- |
| Owns value          | No              | Yes            | Yes     | Yes                       |
| Heap allocation     | Not necessarily | Yes            | Yes     | Yes                       |
| Shared ownership    | No              | No             | Yes     | Yes                       |
| Thread-safe sharing | N/A             | Depends on `T` | No      | Yes, with `T` constraints |
| Reference counted   | No              | No             | Yes     | Yes                       |

References are generally preferable when simple borrowing is sufficient.

Smart pointers should be introduced because your ownership model requires them, not simply because they are available.

---

# 29. Performance Considerations

Different smart pointers have different costs.

### `Box<T>`

Generally very cheap:

```text
one heap allocation
one owning pointer
```

### `Rc<T>`

Adds reference-count bookkeeping.

Cloning an `Rc` changes the count.

### `Arc<T>`

Uses atomic operations for reference counting.

This can be more expensive than `Rc`.

### `RefCell<T>`

Adds runtime borrow-state checking.

### `Mutex<T>`

Can involve:

* atomic operations
* contention
* blocking
* scheduler interaction

### `RwLock<T>`

Can be advantageous for read-heavy workloads but has its own synchronization overhead and fairness/contension behavior depending on the implementation.

The important lesson is:

> Don't choose a smart pointer based only on convenience. Choose it based on the ownership and concurrency semantics you actually need.

---

# 30. Common Pitfalls

### `Rc::clone()` clones the object

No.

```rust
Rc::clone(&x)
```

normally clones the **owner handle**, not the underlying `T`.

### `Arc<T>` makes everything thread-safe

No.

`Arc` provides thread-safe reference counting. The contained type still needs appropriate `Send`/`Sync` properties.

### `RefCell<T>` eliminates borrowing rules

No.

It enforces borrowing rules at runtime instead of compile time.

### `Rc<RefCell<T>>` is always bad

No.

It is extremely useful for certain single-threaded data structures.

It should not be used merely to fight the borrow checker when a simpler ownership model exists.

### `Mutex<T>` means the data is immutable

No.

It provides synchronized mutable access.

### `Weak<T>` gives normal access

Not directly.

You normally call:

```rust
weak.upgrade()
```

which returns:

```rust
Option<Rc<T>>
```

or:

```rust
Option<Arc<T>>
```

because the object may already have been destroyed.

### `Box<T>` is required for every heap allocation

No.

Many Rust types allocate internally:

```text
String
Vec<T>
HashMap<K,V>
```

You don't normally wrap these in `Box` just because they contain heap allocations.

---

# 31. Practical Cheat Sheet

```text
I need...

Heap allocation
    → Box<T>

Shared ownership, one thread
    → Rc<T>

Shared ownership, multiple threads
    → Arc<T>

Mutable data behind shared ownership, one thread
    → Rc<RefCell<T>>

Mutable data shared between threads
    → Arc<Mutex<T>>

Read-heavy shared data between threads
    → Arc<RwLock<T>>

A non-owning link
    → Weak<T>

Borrow-or-clone optimization
    → Cow<'a, T>

A stable address / pinning
    → Pin<P>
```

And the most important combinations:

```text
Rc<RefCell<T>>
    = shared + mutable + single-threaded

Arc<Mutex<T>>
    = shared + mutable + multi-threaded

Arc<RwLock<T>>
    = shared + read/write synchronization

Pin<Box<T>>
    = heap allocation + pinning
```

---

# 32. Related Concepts

* Ownership
* Borrowing
* Lifetimes
* `Deref`
* `DerefMut`
* `Drop`
* Interior mutability
* `Send`
* `Sync`
* Heap allocation
* Stack allocation
* Reference counting
* Atomic operations
* Mutexes
* Read-write locks
* Concurrency
* Trait objects
* Dynamic dispatch
* `Pin`
* `Unpin`
* Async Rust
* Recursive data structures
* Memory management
