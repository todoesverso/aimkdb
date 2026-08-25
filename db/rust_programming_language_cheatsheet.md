---

title: "Rust Programming Language Cheat Sheet"
category: "Programming"
subcategory: "Languages"
tags:

* "Rust"
* "Rust syntax"
* "ownership"
* "borrowing"
* "lifetimes"
* "traits"
* "generics"
* "Cargo"
  type: "reference"

---

# Rust Programming Language Cheat Sheet

## 1. Program Structure

```rust
fn main() {
    println!("Hello, world!");
}
```

Compile directly:

```bash
rustc main.rs
./main
```

Create a Cargo project:

```bash
cargo new my_project
cd my_project
cargo run
```

Common commands:

```bash
cargo build
cargo build --release
cargo run
cargo check
cargo test
cargo fmt
cargo clippy
cargo doc
```

---

# 2. Variables

Variables are immutable by default:

```rust
let x = 10;
```

Mutable variable:

```rust
let mut x = 10;
x = 20;
```

Explicit type:

```rust
let x: i32 = 10;
```

Constants:

```rust
const MAX_SIZE: usize = 1024;
```

Static:

```rust
static VERSION: &str = "1.0";
```

Shadowing:

```rust
let x = 10;
let x = x + 1;
let x = "hello";
```

Shadowing creates a new binding; it is different from mutating a variable.

---

# 3. Basic Types

### Integers

```rust
i8
i16
i32
i64
i128
isize

u8
u16
u32
u64
u128
usize
```

Examples:

```rust
let a: i32 = -10;
let b: u64 = 100;
let index: usize = 0;
```

### Floating point

```rust
f32
f64
```

```rust
let pi: f64 = 3.14159;
```

### Boolean

```rust
let enabled: bool = true;
```

### Character

```rust
let c: char = 'A';
```

A Rust `char` represents a Unicode scalar value and is **not** equivalent to a one-byte C `char`.

### Unit

```rust
let x: () = ();
```

`()` represents the unit type and is commonly used for functions that return no meaningful value.

---

# 4. Tuples

```rust
let point: (i32, i32) = (10, 20);
```

Access:

```rust
point.0
point.1
```

Destructuring:

```rust
let (x, y) = point;
```

Nested tuple:

```rust
let value = (1, "hello", true);
```

---

# 5. Arrays

Fixed-size arrays:

```rust
let numbers: [i32; 4] = [1, 2, 3, 4];
```

Repeated value:

```rust
let zeros = [0; 10];
```

Access:

```rust
numbers[0]
```

Length:

```rust
numbers.len()
```

Arrays have their size encoded in their type:

```text
[i32; 4]
   |
   +-- element type
   +-- number of elements
```

---

# 6. Slices

A slice represents a dynamically sized view into a contiguous sequence.

```rust
let numbers = [1, 2, 3, 4];

let slice: &[i32] = &numbers[1..3];
```

```text
array:  [1, 2, 3, 4]
           ^     ^
           |-----|
             slice
```

Mutable slice:

```rust
let mut numbers = [1, 2, 3, 4];

let slice = &mut numbers[1..3];
slice[0] = 20;
```

Common function parameter:

```rust
fn sum(values: &[i32]) -> i32 {
    values.iter().sum()
}
```

This accepts both arrays and `Vec<T>` slices.

---

# 7. Strings

Rust has two primary string types.

### `String`

Owned, growable UTF-8 string:

```rust
let mut s = String::from("hello");

s.push('!');
s.push_str(" world");
```

### `&str`

Borrowed string slice:

```rust
let s: &str = "hello";
```

Conceptually:

```text
String
  |
  +-- owns UTF-8 data
  +-- heap allocation
  +-- growable

&str
  |
  +-- borrowed view
  +-- does not own the data
```

Conversion:

```rust
let s = String::from("hello");
let slice: &str = &s;
```

---

# 8. Functions

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

The last expression is returned implicitly.

Explicit return:

```rust
fn add(a: i32, b: i32) -> i32 {
    return a + b;
}
```

No return value:

```rust
fn log_message(message: &str) {
    println!("{message}");
}
```

Generic function:

```rust
fn identity<T>(value: T) -> T {
    value
}
```

---

# 9. Expressions vs Statements

Rust is heavily expression-oriented.

```rust
let x = if condition {
    10
} else {
    20
};
```

A block evaluates to its final expression:

```rust
let result = {
    let a = 10;
    let b = 20;

    a + b
};
```

Semicolon changes the meaning:

```rust
{
    10
}
```

evaluates to `10`, while:

```rust
{
    10;
}
```

evaluates to `()`.

---

# 10. Control Flow

### `if`

```rust
if x > 10 {
    println!("large");
} else if x > 0 {
    println!("positive");
} else {
    println!("non-positive");
}
```

### `loop`

```rust
loop {
    work();

    if done {
        break;
    }
}
```

Return a value:

```rust
let result = loop {
    break 42;
};
```

### `while`

```rust
while condition {
    work();
}
```

### `for`

```rust
for i in 0..10 {
    println!("{i}");
}
```

Inclusive range:

```rust
for i in 0..=10 {
    println!("{i}");
}
```

---

# 11. Pattern Matching

`match` is one of Rust's central language features.

```rust
match value {
    0 => println!("zero"),
    1 => println!("one"),
    _ => println!("other"),
}
```

Return a value:

```rust
let result = match value {
    0 => "zero",
    1 => "one",
    _ => "other",
};
```

Multiple patterns:

```rust
match value {
    1 | 2 | 3 => println!("small"),
    _ => println!("other"),
}
```

Range:

```rust
match value {
    1..=10 => println!("1-10"),
    _ => println!("other"),
}
```

Guards:

```rust
match value {
    x if x > 10 => println!("large"),
    _ => println!("small"),
}
```

---

# 12. `if let`

Useful when only one pattern matters:

```rust
if let Some(value) = optional {
    println!("{value}");
}
```

Equivalent conceptually to a partial `match`.

---

# 13. Ownership

Ownership is the central mechanism used by Rust to manage memory without requiring a garbage collector.

Every value has an owner.

```rust
let s = String::from("hello");
```

When `s` goes out of scope, its `String` is dropped.

```rust
{
    let s = String::from("hello");

    // use s
}

// s is dropped here
```

The basic ownership rules are:

1. Every value has an owner.
2. There is one owner at a time.
3. When the owner goes out of scope, the value is dropped.

---

# 14. Move Semantics

This moves ownership:

```rust
let s1 = String::from("hello");
let s2 = s1;
```

After the move:

```rust
// println!("{s1}"); // error
println!("{s2}");
```

Conceptually:

```text
Before:

s1 -----> String data


After:

s1       String data <----- s2
 |             ^
 invalid       |
```

Rust prevents accidental double-free behavior.

---

# 15. `Copy`

Some small types implement `Copy`.

```rust
let x = 10;
let y = x;

println!("{x}");
println!("{y}");
```

`i32` is copied rather than moved.

Common `Copy` types include:

* integers
* floating-point values
* `bool`
* `char`
* tuples containing only `Copy` types
* references, subject to their type

A type can opt into `Copy` when its semantics permit it.

---

# 16. Borrowing

Instead of transferring ownership, borrow a value:

```rust
fn length(s: &String) -> usize {
    s.len()
}
```

Call:

```rust
let s = String::from("hello");

let n = length(&s);

println!("{s}");
```

Usually prefer `&str`:

```rust
fn length(s: &str) -> usize {
    s.len()
}
```

---

# 17. Mutable Borrowing

```rust
fn append_world(s: &mut String) {
    s.push_str(" world");
}

let mut s = String::from("hello");

append_world(&mut s);
```

Rust enforces borrowing rules at compile time.

At a high level:

```text
Either:

many immutable borrows

OR:

one mutable borrow

but not both simultaneously
```

This prevents many data races and invalid memory accesses.

---

# 18. Ownership Cheat Sheet

```text
T
 |
 +-- owns the value

&T
 |
 +-- shared borrow

&mut T
 |
 +-- exclusive mutable borrow
```

Typical function choices:

```rust
fn read(value: &T)
fn modify(value: &mut T)
fn consume(value: T)
```

A useful design question is:

> Does this function need to own the value, modify it, or merely inspect it?

---

# 19. Lifetimes

Lifetimes describe how long references are valid.

Example:

```rust
fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() > b.len() {
        a
    } else {
        b
    }
}
```

The lifetime `'a` expresses the relationship between the input references and the returned reference.

Important:

> Lifetimes do not extend an object's lifetime. They describe relationships between references.

Most lifetimes are inferred automatically.

---

# 20. Structs

```rust
struct Point {
    x: f64,
    y: f64,
}
```

Create:

```rust
let p = Point {
    x: 10.0,
    y: 20.0,
};
```

Access:

```rust
println!("{}", p.x);
```

Mutable:

```rust
let mut p = Point { x: 0.0, y: 0.0 };

p.x = 10.0;
```

---

# 21. Methods

```rust
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }
}
```

Call:

```rust
let r = Rectangle {
    width: 10,
    height: 20,
};

println!("{}", r.area());
```

Receiver forms:

```rust
&self
&mut self
self
```

They correspond roughly to:

```text
&self       borrow immutably
&mut self   borrow mutably
self        consume ownership
```

---

# 22. Associated Functions

An associated function has no `self` receiver.

```rust
impl Rectangle {
    fn square(size: u32) -> Self {
        Self {
            width: size,
            height: size,
        }
    }
}
```

Call:

```rust
let r = Rectangle::square(10);
```

---

# 23. Enums

```rust
enum Direction {
    North,
    South,
    East,
    West,
}
```

With associated data:

```rust
enum Message {
    Quit,
    Text(String),
    Move { x: i32, y: i32 },
}
```

Pattern matching:

```rust
match message {
    Message::Quit => println!("quit"),

    Message::Text(text) => {
        println!("{text}");
    }

    Message::Move { x, y } => {
        println!("{x}, {y}");
    }
}
```

Enums are much more powerful than C-style enumerations because variants can carry data.

---

# 24. `Option<T>`

Rust does not use `NULL` for ordinary optional values.

Instead:

```rust
enum Option<T> {
    Some(T),
    None,
}
```

Example:

```rust
fn find_user(id: u64) -> Option<User> {
    // ...
}
```

Use:

```rust
match find_user(42) {
    Some(user) => println!("{}", user.name),
    None => println!("not found"),
}
```

Convenient methods:

```rust
value.is_some()
value.is_none()
value.unwrap()
value.unwrap_or(default)
value.map(...)
value.and_then(...)
```

Avoid `unwrap()` when failure is a normal possibility.

---

# 25. `Result<T, E>`

Errors are commonly represented with:

```rust
Result<T, E>
```

Conceptually:

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

Example:

```rust
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err("division by zero".into())
    } else {
        Ok(a / b)
    }
}
```

Handle it:

```rust
match divide(10.0, 2.0) {
    Ok(value) => println!("{value}"),
    Err(error) => println!("error: {error}"),
}
```

---

# 26. The `?` Operator

Instead of:

```rust
let value = match operation() {
    Ok(value) => value,
    Err(error) => return Err(error),
};
```

use:

```rust
let value = operation()?;
```

Example:

```rust
fn load_config() -> Result<Config, Error> {
    let text = std::fs::read_to_string("config.toml")?;
    let config = parse_config(&text)?;

    Ok(config)
}
```

The `?` operator propagates compatible errors.

---

# 27. Generics

```rust
fn identity<T>(value: T) -> T {
    value
}
```

Struct:

```rust
struct Pair<T> {
    first: T,
    second: T,
}
```

Usage:

```rust
let pair = Pair {
    first: 10,
    second: 20,
};
```

Multiple generic types:

```rust
struct Pair<T, U> {
    first: T,
    second: U,
}
```

---

# 28. Traits

Traits define shared behavior.

```rust
trait Drawable {
    fn draw(&self);
}
```

Implement:

```rust
struct Circle;

impl Drawable for Circle {
    fn draw(&self) {
        println!("circle");
    }
}
```

A trait is roughly comparable to an interface, but Rust's trait system is more expressive.

---

# 29. Trait Bounds

```rust
fn print_value<T: std::fmt::Display>(value: T) {
    println!("{value}");
}
```

Equivalent `where` syntax:

```rust
fn print_value<T>(value: T)
where
    T: std::fmt::Display,
{
    println!("{value}");
}
```

Multiple bounds:

```rust
fn process<T>(value: T)
where
    T: Clone + Send + Sync,
{
    // ...
}
```

---

# 30. Trait Objects

Dynamic dispatch:

```rust
fn draw_all(items: &[Box<dyn Drawable>]) {
    for item in items {
        item.draw();
    }
}
```

`dyn Trait` means the concrete type is erased behind a trait-object interface.

Conceptually:

```text
Generic T
    |
    +-- static dispatch
    +-- monomorphization

dyn Trait
    |
    +-- dynamic dispatch
    +-- vtable
```

---

# 31. Closures

```rust
let add = |a, b| a + b;

let result = add(2, 3);
```

Capture variables:

```rust
let x = 10;

let add_x = |n| n + x;
```

Mutable capture:

```rust
let mut count = 0;

let mut increment = || {
    count += 1;
};
```

Move capture:

```rust
let s = String::from("hello");

let f = move || {
    println!("{s}");
};
```

---

# 32. Iterators

```rust
let numbers = vec![1, 2, 3, 4, 5];

let doubled: Vec<_> = numbers
    .iter()
    .map(|x| x * 2)
    .collect();
```

Common operations:

```rust
.iter()
.iter_mut()
.into_iter()

.map(...)
.filter(...)
.filter_map(...)
.flat_map(...)
.fold(...)
.reduce(...)
.zip(...)
.enumerate(...)
.take(...)
.skip(...)
.collect()
```

Example:

```rust
let sum: i32 = numbers
    .iter()
    .filter(|x| **x > 2)
    .map(|x| x * 2)
    .sum();
```

Iterators are generally **lazy** until consumed.

---

# 33. `Vec<T>`

Growable contiguous array:

```rust
let mut numbers = Vec::new();

numbers.push(10);
numbers.push(20);
numbers.push(30);
```

Or:

```rust
let numbers = vec![1, 2, 3, 4];
```

Access:

```rust
numbers[0]
```

Bounds-checked access returning `Option`:

```rust
numbers.get(0)
```

Useful methods:

```rust
push()
pop()
insert()
remove()
len()
capacity()
clear()
sort()
iter()
```

---

# 34. Collections

### `Vec<T>`

Contiguous growable array.

```rust
Vec<T>
```

### `HashMap<K, V>`

```rust
use std::collections::HashMap;

let mut map = HashMap::new();

map.insert("one", 1);
map.insert("two", 2);
```

Lookup:

```rust
map.get("one")
```

### `HashSet<T>`

```rust
use std::collections::HashSet;

let mut set = HashSet::new();

set.insert("rust");
```

Other common collections:

```text
VecDeque
LinkedList
BTreeMap
BTreeSet
BinaryHeap
```

---

# 35. Modules

```rust
mod network {
    pub fn connect() {
        println!("connecting");
    }
}
```

Use:

```rust
network::connect();
```

Visibility is private by default.

```rust
pub fn public_function() {}
```

---

# 36. `use`

Import names:

```rust
use std::collections::HashMap;
```

Multiple imports:

```rust
use std::collections::{HashMap, HashSet};
```

Alias:

```rust
use std::collections::HashMap as Map;
```

Glob imports:

```rust
use std::collections::*;
```

Generally avoid glob imports except where they make sense.

---

# 37. Crates and Cargo

A Cargo project commonly looks like:

```text
my_project/
├── Cargo.toml
└── src/
    └── main.rs
```

Library:

```text
src/
└── lib.rs
```

`Cargo.toml`:

```toml
[package]
name = "my_project"
version = "0.1.0"
edition = "2024"

[dependencies]
```

Add a dependency:

```bash
cargo add serde
```

Build:

```bash
cargo build
```

Release:

```bash
cargo build --release
```

---

# 38. Ownership and Smart Pointers

### `Box<T>`

Heap allocation:

```rust
let x = Box::new(42);
```

Useful for recursive types and explicit heap ownership.

### `Rc<T>`

Reference counting for single-threaded shared ownership:

```rust
use std::rc::Rc;

let x = Rc::new(String::from("hello"));
let y = Rc::clone(&x);
```

### `Arc<T>`

Atomic reference counting for thread-safe shared ownership:

```rust
use std::sync::Arc;

let x = Arc::new(42);
let y = Arc::clone(&x);
```

---

# 39. Interior Mutability

`Cell<T>`:

```rust
use std::cell::Cell;

let value = Cell::new(10);

value.set(20);
```

`RefCell<T>`:

```rust
use std::cell::RefCell;

let value = RefCell::new(10);

*value.borrow_mut() += 1;
```

`RefCell` moves certain borrowing checks from compile time to runtime.

For multi-threaded code, common equivalents include:

```text
Mutex<T>
RwLock<T>
Atomic*
```

---

# 40. Concurrency

Spawn a thread:

```rust
use std::thread;

let handle = thread::spawn(|| {
    println!("hello from thread");
});

handle.join().unwrap();
```

Channels:

```rust
use std::sync::mpsc;
use std::thread;

let (tx, rx) = mpsc::channel();

thread::spawn(move || {
    tx.send(42).unwrap();
});

let value = rx.recv().unwrap();
```

Shared state:

```rust
use std::sync::{Arc, Mutex};

let counter = Arc::new(Mutex::new(0));
```

---

# 41. `Send` and `Sync`

Two important concurrency traits:

```text
Send
Sync
```

### `Send`

A type can be transferred between threads.

### `Sync`

A type can be safely referenced from multiple threads.

Conceptually:

```text
T: Send
    ↓
ownership of T can move across threads

T: Sync
    ↓
&T can be shared across threads
```

These traits are fundamental to Rust's compile-time concurrency safety.

---

# 42. Async Rust

An async function:

```rust
async fn fetch_data() -> Result<String, Error> {
    // ...
}
```

Call:

```rust
let result = fetch_data().await?;
```

An async function returns a future.

```text
async fn
   |
   v
Future
   |
   v
executor
   |
   v
poll()
```

Rust's standard library provides the language primitives for async, but an async runtime such as Tokio or async-std is typically used to execute asynchronous tasks.

---

# 43. Macros

Declarative macro:

```rust
macro_rules! hello {
    () => {
        println!("hello");
    };
}
```

Invoke:

```rust
hello!();
```

Common built-in macros:

```rust
println!()
print!()
format!()
vec!()
panic!()
assert!()
dbg!()
todo!()
unimplemented!()
```

Derive macros:

```rust
#[derive(Debug, Clone, PartialEq)]
struct User {
    name: String,
}
```

---

# 44. Attributes

Attributes provide metadata to the compiler or tools.

```rust
#[derive(Debug)]
struct User {
    name: String,
}
```

Conditional compilation:

```rust
#[cfg(target_os = "linux")]
fn platform_specific() {
}
```

Tests:

```rust
#[test]
fn addition_works() {
    assert_eq!(2 + 2, 4);
}
```

---

# 45. Error Handling

Rust generally prefers:

```text
Recoverable error
        |
        v
Result<T, E>

Optional value
        |
        v
Option<T>

Unrecoverable programmer/system invariant failure
        |
        v
panic!
```

Avoid using `panic!` as normal application-level error handling.

---

# 46. Testing

```rust
#[cfg(test)]
mod tests {
    #[test]
    fn addition_works() {
        assert_eq!(2 + 2, 4);
    }
}
```

Run:

```bash
cargo test
```

Assertions:

```rust
assert!(condition);
assert_eq!(left, right);
assert_ne!(left, right);
```

---

# 47. Formatting and Linting

Format:

```bash
cargo fmt
```

Check formatting:

```bash
cargo fmt --check
```

Lint:

```bash
cargo clippy
```

Compile without producing binaries:

```bash
cargo check
```

A useful development loop is:

```text
cargo fmt
     ↓
cargo check
     ↓
cargo clippy
     ↓
cargo test
```

---

# 48. Common Rust Keywords

```text
as
async
await
break
const
continue
crate
dyn
else
enum
extern
false
fn
for
if
impl
in
let
loop
match
mod
move
mut
pub
ref
return
Self
self
static
struct
super
trait
true
type
unsafe
use
where
while
```

Additional syntax and contextual keywords exist depending on Rust edition and language version.

---

# 49. Unsafe Rust

Rust allows explicitly opting out of some compile-time safety guarantees:

```rust
unsafe {
    // unsafe operations
}
```

Examples include:

* raw pointer dereferencing
* calling unsafe functions
* accessing mutable statics in applicable contexts
* implementing certain unsafe traits

Example:

```rust
let value = 42;
let ptr = &value as *const i32;

unsafe {
    println!("{}", *ptr);
}
```

Important:

> `unsafe` does not mean "the compiler stops checking everything."

It means certain operations that require additional programmer guarantees are permitted.

---

# 50. Raw Pointers

```rust
let value = 42;

let p: *const i32 = &value;
let mut value = 42;
let p: *mut i32 = &mut value;
```

Dereference requires an unsafe context:

```rust
unsafe {
    *p = 100;
}
```

Raw pointers are primarily useful for:

* FFI
* hardware interfaces
* custom allocators
* low-level systems programming
* interoperability with C

---

# 51. FFI

Calling C functions:

```rust
unsafe extern "C" {
    fn puts(s: *const std::ffi::c_char) -> i32;
}
```

FFI crosses the safety boundary between Rust and another language.

When interacting with C, Rust cannot automatically verify the foreign function's contracts.

Therefore FFI code often forms a small `unsafe` boundary surrounded by safe Rust abstractions.

---

# 52. Common Ownership Patterns

### Borrow when you only need to read

```rust
fn process(data: &[u8]) {
}
```

### Mutably borrow when you need to modify

```rust
fn process(data: &mut [u8]) {
}
```

### Take ownership when the function needs to keep it

```rust
fn store(data: Vec<u8>) {
}
```

### Return ownership

```rust
fn create_data() -> Vec<u8> {
    vec![1, 2, 3]
}
```

### Shared ownership

```rust
Arc<T>
```

### Shared mutable ownership

Often:

```rust
Arc<Mutex<T>>
```

---

# 53. Common Pitfalls

### Fighting the borrow checker

The borrow checker is often telling you that your ownership model is unclear.

Instead of trying to circumvent it immediately, reconsider:

* Who owns this value?
* Who needs to mutate it?
* How long must the reference live?
* Can the function borrow instead of own?
* Can the data structure be redesigned?

### Cloning everything

```rust
let copy = value.clone();
```

`clone()` is sometimes appropriate, but using it everywhere merely to satisfy ownership errors can hide an inefficient design.

### Using `unwrap()` everywhere

```rust
value.unwrap()
```

Fine when failure is truly impossible or deliberately treated as fatal, but usually inappropriate for ordinary error handling.

### Confusing `String` and `&str`

```text
String = owned UTF-8 string
&str   = borrowed string slice
```

### Overusing `Rc<RefCell<T>>`

This can reproduce runtime-managed shared mutable state inside a language designed to make ownership explicit.

Use it when the ownership model actually requires it, not merely because it makes the borrow checker disappear.

---

# 54. Rust vs. C — Mental Model

| Concept             | C                               | Rust                            |
| ------------------- | ------------------------------- | ------------------------------- |
| Memory management   | Manual                          | Ownership + RAII-like `Drop`    |
| Null pointer        | Common                          | `Option<T>`                     |
| Error handling      | Return codes / `errno`          | `Result<T, E>`                  |
| Generic programming | Macros / `void *` / conventions | Generics + traits               |
| Interfaces          | Function pointers / conventions | Traits                          |
| Strings             | `char *` + `'\0'`               | `String`, `&str`                |
| Array bounds        | Usually unchecked               | Checked indexing                |
| Memory safety       | Programmer responsibility       | Compiler-enforced for safe Rust |
| Concurrency safety  | Programmer responsibility       | Type system + ownership         |
| Unsafe operations   | Normal                          | Explicit `unsafe`               |
| Build system        | Compiler/linker/tools           | Cargo                           |

---

# 55. Essential Mental Model

The most important Rust concepts can be reduced to:

```text
                Rust
                  |
       +----------+----------+
       |                     |
    Ownership             Types
       |                     |
   +---+---+           +-----+-----+
   |       |           |           |
Borrowing Lifetimes  Traits      Enums
   |                   |
   |                   +-- Generics
   |
   +-- &T
   +-- &mut T
   +-- T
```

And for systems programming:

```text
Safe Rust
    |
    +-- ownership
    +-- borrowing
    +-- lifetimes
    +-- types
    +-- traits
    +-- concurrency
    |
    v
Unsafe boundary
    |
    +-- raw pointers
    +-- FFI
    +-- hardware
    +-- low-level invariants
```

The central idea is:

> **Rust uses ownership, borrowing, lifetimes, and a powerful type system to make memory safety and thread safety enforceable at compile time, while still allowing explicit low-level control when necessary.**

## Related Concepts

* Ownership
* Borrowing
* Lifetimes
* Rust Type System
* Traits
* Generics
* Pattern Matching
* `Option<T>`
* `Result<T, E>`
* Iterators
* Closures
* Smart Pointers
* `Send` and `Sync`
* Rust Concurrency
* Async Rust
* Unsafe Rust
* Rust FFI
* Cargo
* Rust Compilation Model
* Zero-Cost Abstractions

