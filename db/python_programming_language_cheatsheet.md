# Python Programming Language Cheat Sheet

**Category:** Programming
**Subcategory:** Languages
**Tags:** Python, syntax, standard library, OOP, typing, async, data structures
**Type:** reference

## 1. Program Structure

```python
def main():
    print("Hello, world!")


if __name__ == "__main__":
    main()
```

Run:

```bash
python main.py
```

Check version:

```bash
python --version
```

Interactive interpreter:

```bash
python
```

---

# 2. Variables

Python variables are names bound to objects.

```python
x = 10
name = "Alice"
enabled = True
```

Multiple assignment:

```python
x, y = 10, 20
```

Swap:

```python
x, y = y, x
```

Type annotation:

```python
count: int = 10
name: str = "Alice"
```

Python is dynamically typed:

```python
x = 10
x = "hello"
```

The **object** has a type; the variable is a name referring to that object.

---

# 3. Basic Types

```text
int
float
complex
bool
str
bytes
None
list
tuple
set
dict
```

Examples:

```python
x = 42
pi = 3.14159
z = 1 + 2j

enabled = True
name = "Alice"

data = b"hello"
nothing = None
```

Check type:

```python
type(x)
```

Check whether an object has a type:

```python
isinstance(x, int)
```

---

# 4. Numbers

### Integers

```python
x = 42
negative = -10
large = 10_000_000
```

Python integers have arbitrary precision.

### Floating point

```python
x = 3.14
```

### Arithmetic

```python
a + b
a - b
a * b
a / b       # floating-point division
a // b      # floor division
a % b       # remainder
a ** b      # exponentiation
```

Example:

```python
10 / 3     # 3.333...
10 // 3    # 3
10 % 3     # 1
10 ** 2    # 100
```

---

# 5. Boolean Logic

```python
True
False
```

Operators:

```python
a and b
a or b
not a
```

Comparisons:

```python
a == b
a != b
a < b
a <= b
a > b
a >= b
```

Identity:

```python
a is b
a is not b
```

Membership:

```python
x in collection
x not in collection
```

Prefer:

```python
if value is None:
    ...
```

rather than:

```python
if value == None:
    ...
```

---

# 6. Strings

```python
name = "Alice"
message = 'hello'
```

Multiline:

```python
text = """
line one
line two
"""
```

Indexing:

```python
text[0]
text[-1]
```

Slicing:

```python
text[1:5]
text[:5]
text[5:]
text[::-1]
```

Useful methods:

```python
text.lower()
text.upper()
text.strip()
text.split()
text.replace("old", "new")
text.startswith("hello")
text.endswith(".py")
```

Length:

```python
len(text)
```

---

# 7. f-Strings

Preferred modern string formatting:

```python
name = "Alice"
age = 30

message = f"{name} is {age} years old"
```

Expressions:

```python
f"result = {x + y}"
```

Formatting:

```python
f"{value:.2f}"
f"{value:10}"
f"{value:>10}"
f"{value:08d}"
```

---

# 8. Lists

```python
numbers = [1, 2, 3, 4]
```

Access:

```python
numbers[0]
numbers[-1]
```

Slice:

```python
numbers[1:3]
```

Modify:

```python
numbers.append(5)
numbers.extend([6, 7])
numbers.insert(0, 0)
numbers.remove(3)
value = numbers.pop()
```

Other methods:

```python
numbers.sort()
numbers.reverse()
numbers.clear()
numbers.count(2)
numbers.index(2)
```

Copy:

```python
copy = numbers.copy()
```

---

# 9. Tuples

Immutable sequences:

```python
point = (10, 20)
```

Parentheses are optional in many contexts:

```python
point = 10, 20
```

Single-element tuple:

```python
x = (10,)
```

Unpacking:

```python
x, y = point
```

Useful for returning multiple values:

```python
def get_point():
    return 10, 20
```

---

# 10. Sets

```python
numbers = {1, 2, 3}
```

Empty set:

```python
numbers = set()
```

Add/remove:

```python
numbers.add(4)
numbers.remove(2)
numbers.discard(10)
```

Set operations:

```python
a | b       # union
a & b       # intersection
a - b       # difference
a ^ b       # symmetric difference
```

Membership is typically very fast:

```python
if value in numbers:
    ...
```

---

# 11. Dictionaries

Key/value mapping:

```python
user = {
    "name": "Alice",
    "age": 30,
}
```

Access:

```python
user["name"]
```

Safer lookup:

```python
user.get("email")
user.get("email", "unknown")
```

Modify:

```python
user["age"] = 31
user["email"] = "alice@example.com"
```

Delete:

```python
del user["age"]
```

Useful methods:

```python
user.keys()
user.values()
user.items()
user.get(...)
user.pop(...)
user.update(...)
```

Iteration:

```python
for key, value in user.items():
    print(key, value)
```

---

# 12. Comprehensions

### List comprehension

```python
squares = [x * x for x in range(10)]
```

With condition:

```python
evens = [x for x in numbers if x % 2 == 0]
```

### Set comprehension

```python
squares = {x * x for x in range(10)}
```

### Dictionary comprehension

```python
squares = {
    x: x * x
    for x in range(10)
}
```

### Generator expression

```python
squares = (x * x for x in range(10))
```

Important distinction:

```text
[...]     → creates collection immediately
(...)     → generator expression, produces lazily
```

---

# 13. Control Flow

### `if`

```python
if x > 10:
    print("large")
elif x > 0:
    print("positive")
else:
    print("non-positive")
```

Python uses indentation to define blocks.

### Conditional expression

```python
result = "yes" if condition else "no"
```

---

# 14. `for`

```python
for item in items:
    print(item)
```

Range:

```python
for i in ran[118;1:3uge(10):
    print(i)
```

Start/stop:

```python
for i in range(1, 10):
    ...
```

Step:

```python
for i in range(0, 10, 2):
    ...
```

Enumerate:

```python
for index, value in enumerate(items):
    print(index, value)
```

Dictionary:

```python
for key, value in data.items():
    ...
```

---

# 15. `while`

```python
while condition:
    work()
```

Break:

```python
while True:
    value = get_value()

    if value is None:
        break
```

Continue:

```python
for item in items:
    if should_skip(item):
        continue

    process(item)
```

Python also supports loop `else`:

```python
for item in items:
    if item == target:
        break
else:
    print("not found")
```

The `else` executes when the loop terminates normally without `break`.

---

# 16. Functions

```python
def add(a, b):
    return a + b
```

Type annotations:

```python
def add(a: int, b: int) -> int:
    return a + b
```

Default argument:

```python
def greet(name: str = "World"):
    print(f"Hello {name}")
```

Keyword arguments:

```python
greet(name="Alice")
```

---

# 17. `*args` and `**kwargs`

Variable positional arguments:

```python
def sum_all(*args):
    return sum(args)
```

Variable keyword arguments:

```python
def configure(**kwargs):
    print(kwargs)
```

Both:

```python
def function(*args, **kwargs):
    ...
```

Unpacking:

```python
values = [1, 2, 3]

print(*values)
```

Dictionary unpacking:

```python
options = {
    "host": "localhost",
    "port": 8080,
}

connect(**options)
```

---

# 18. Positional-Only and Keyword-Only Parameters

Positional-only:

```python
def func(x, y, /):
    ...
```

`x` and `y` must be positional.

Keyword-only:

```python
def func(x, *, debug=False):
    ...
```

Usage:

```python
func(10, debug=True)
```

Both:

```python
def func(x, /, y, *, debug=False):
    ...
```

---

# 19. Lambda

Small anonymous function:

```python
square = lambda x: x * x
```

Common with sorting:

```python
users.sort(key=lambda user: user["name"])
```

Prefer a normal `def` when the function is complex.

---

# 20. Scope

Python uses lexical scoping.

Common scopes:

```text
LEGB

Local
Enclosing
Global
Built-in
```

Global:

```python
x = 10

def foo():
    print(x)
```

Modify global:

```python
x = 10

def foo():
    global x
    x += 1
```

Nonlocal:

```python
def outer():
    x = 10

    def inner():
        nonlocal x
        x += 1

    inner()
```

Avoid excessive use of `global`.

---

# 21. Exceptions

```python
try:
    value = int(text)
except ValueError:
    print("invalid number")
```

Multiple exceptions:

```python
try:
    ...
except (ValueError, TypeError):
    ...
```

Access exception:

```python
try:
    ...
except ValueError as exc:
    print(exc)
```

`else`:

```python
try:
    value = int(text)
except ValueError:
    print("invalid")
else:
    print("success")
```

`finally`:

```python
try:
    ...
finally:
    cleanup()
```

Raise:

```python
raise ValueError("invalid value")
```

---

# 22. Custom Exceptions

```python
class ConfigurationError(Exception):
    pass
```

Raise:

```python
raise ConfigurationError("missing configuration")
```

Catch:

```python
try:
    load_config()
except ConfigurationError as exc:
    print(exc)
```

Exception hierarchy:

```text
BaseException
    |
    +-- Exception
          |
          +-- ValueError
          +-- TypeError
          +-- RuntimeError
          +-- OSError
          +-- ...
```

Usually derive application exceptions from `Exception`, not `BaseException`.

---

# 23. Classes

```python
class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def greet(self):
        return f"Hello {self.name}"
```

Create:

```python
user = User("Alice", 30)
```

Access:

```python
user.name
user.greet()
```

---

# 24. Class and Static Methods

Class method:

```python
class User:
    @classmethod
    def anonymous(cls):
        return cls("anonymous", 0)
```

Static method:

```python
class Math:
    @staticmethod
    def add(a, b):
        return a + b
```

Difference:

```text
instance method
    self

classmethod
    cls

staticmethod
    neither
```

---

# 25. Properties

```python
class User:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
```

Use:

```python
user.name
user.name = "Bob"
```

Properties allow method-backed attributes.

---

# 26. Dataclasses

For data-oriented classes:

```python
from dataclasses import dataclass


@dataclass
class User:
    name: str
    age: int
```

Create:

```python
user = User("Alice", 30)
```

Useful options:

```python
@dataclass(frozen=True)
class Point:
    x: float
    y: float
```

Other options include:

```text
frozen
order
slots
kw_only
repr
eq
```

---

# 27. Inheritance

```python
class Animal:
    def speak(self):
        print("...")


class Dog(Animal):
    def speak(self):
        print("woof")
```

Use:

```python
dog = Dog()
dog.speak()
```

Call parent implementation:

```python
class Dog(Animal):
    def speak(self):
        super().speak()
        print("woof")
```

Python supports multiple inheritance:

```python
class C(A, B):
    ...
```

Method resolution order:

```python
C.mro()
```

---

# 28. Abstract Base Classes

```python
from abc import ABC, abstractmethod


class Storage(ABC):

    @abstractmethod
    def save(self, data):
        pass
```

A subclass must implement the abstract method before it can normally be instantiated.

---

# 29. Duck Typing

Python often focuses on behavior rather than concrete types.

Instead of:

```python
if isinstance(obj, SomeClass):
    ...
```

you can often simply do:

```python
obj.save()
```

The idea:

> If an object supports the required operation, use it.

This philosophy is strongly connected to Python's dynamic nature and protocols.

---

# 30. Type Hints

Basic:

```python
def add(a: int, b: int) -> int:
    return a + b
```

Optional:

```python
def find_user(id: int) -> User | None:
    ...
```

Collections:

```python
list[int]
dict[str, int]
tuple[int, str]
set[str]
```

Union:

```python
str | int
```

Type alias:

```python
type UserID = int
```

Modern Python type syntax depends on the Python version being targeted.

---

# 31. Generics

```python
from typing import TypeVar

T = TypeVar("T")


def identity(value: T) -> T:
    return value
```

Modern syntax can express generic classes/functions more directly in newer Python versions.

---

# 32. Protocols

Structural typing:

```python
from typing import Protocol


class Drawable(Protocol):
    def draw(self) -> None:
        ...
```

A class can satisfy the protocol by implementing the required interface without explicitly inheriting from it.

This is the static-typing equivalent of Python's duck-typing philosophy.

---

# 33. Iterators

An iterator implements:

```python
__iter__()
__next__()
```

Example:

```python
numbers = iter([1, 2, 3])

next(numbers)
next(numbers)
```

When exhausted:

```text
StopIteration
```

`for` loops use the iterator protocol internally.

---

# 34. Generators

Generator:

```python
def numbers():
    yield 1
    yield 2
    yield 3
```

Use:

```python
for n in numbers():
    print(n)
```

Generator expression:

```python
squares = (x * x for x in range(10))
```

Generators are lazy and useful for processing large streams of data.

---

# 35. Context Managers

Common:

```python
with open("file.txt") as f:
    data = f.read()
```

The context manager protocol uses:

```python
__enter__()
__exit__()
```

Custom context manager:

```python
class Resource:
    def __enter__(self):
        print("acquire")
        return self

    def __exit__(self, exc_type, exc, tb):
        print("release")
```

The `with` statement ensures cleanup even when exceptions occur.

---

# 36. Files

Read:

```python
with open("data.txt", "r") as f:
    text = f.read()
```

Read lines:

```python
with open("data.txt") as f:
    for line in f:
        print(line.strip())
```

Write:

```python
with open("data.txt", "w") as f:
    f.write("hello\n")
```

Append:

```python
with open("data.txt", "a") as f:
    f.write("more\n")
```

Binary:

```python
with open("image.png", "rb") as f:
    data = f.read()
```

---

# 37. `pathlib`

Prefer `pathlib` for modern filesystem code:

```python
from pathlib import Path

path = Path("data/file.txt")
```

Useful operations:

```python
path.exists()
path.is_file()
path.is_dir()
path.name
path.stem
path.suffix
path.parent
```

Read:

```python
text = path.read_text()
```

Write:

```python
path.write_text("hello")
```

Directory:

```python
for file in Path("data").glob("*.json"):
    print(file)
```

---

# 38. JSON

```python
import json
```

Serialize:

```python
data = {
    "name": "Alice",
    "age": 30,
}

text = json.dumps(data)
```

Deserialize:

```python
data = json.loads(text)
```

File:

```python
with open("data.json") as f:
    data = json.load(f)
```

Write:

```python
with open("data.json", "w") as f:
    json.dump(data, f, indent=2)
```

---

# 39. Regular Expressions

```python
import re
```

Search:

```python
match = re.search(r"\d+", text)
```

Match:

```python
re.match(r"^hello", text)
```

Find all:

```python
re.findall(r"\d+", text)
```

Replace:

```python
re.sub(r"\s+", " ", text)
```

Raw strings are useful for regex patterns:

```python
r"\d+\.\d+"
```

---

# 40. Environment Variables

```python
import os

value = os.getenv("DATABASE_URL")
```

With default:

```python
value = os.getenv("PORT", "8080")
```

Set in shell:

```bash
export PORT=8080
```

For modern filesystem/environment code, `os` and `pathlib` are commonly used together.

---

# 41. Command-Line Arguments

Simple:

```python
import sys

print(sys.argv)
```

For real CLI applications, prefer `argparse`:

```python
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--port",
    type=int,
    default=8080,
)

args = parser.parse_args()

print(args.port)
```

---

# 42. Logging

```python
import logging

logging.basicConfig(level=logging.INFO)

logging.debug("debug")
logging.info("started")
logging.warning("warning")
logging.error("error")
```

Typical application:

```python
logger = logging.getLogger(__name__)

logger.info("Processing %s", filename)
```

Prefer logging over `print()` for long-running applications and libraries.

---

# 43. Modules

`math_utils.py`:

```python
def add(a, b):
    return a + b
```

Import:

```python
import math_utils

math_utils.add(1, 2)
```

Or:

```python
from math_utils import add
```

Alias:

```python
import math as m
```

Avoid:

```python
from module import *
```

---

# 44. Packages

Typical project:

```text
my_project/
├── pyproject.toml
├── README.md
└── src/
    └── my_project/
        ├── __init__.py
        ├── main.py
        └── utils.py
```

Import:

```python
from my_project.utils import helper
```

Modern Python packaging is generally configured through `pyproject.toml`.

---

# 45. Virtual Environments

Create:

```bash
python -m venv .venv
```

Activate on Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

Install:

```bash
python -m pip install requests
```

Freeze dependencies:

```bash
python -m pip freeze
```

Deactivate:

```bash
deactivate
```

---

# 46. `pyproject.toml`

Modern Python projects commonly use:

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "requests",
]
```

`pyproject.toml` is the standard configuration entry point for modern Python packaging and tooling.

---

# 47. Async Programming

Python's standard async framework is `asyncio`.

```python
import asyncio


async def main():
    print("hello")
    await asyncio.sleep(1)
    print("world")


asyncio.run(main())
```

Async function:

```python
async def fetch():
    ...
```

Await:

```python
result = await fetch()
```

Concurrent tasks:

```python
tasks = [
    asyncio.create_task(fetch_a()),
    asyncio.create_task(fetch_b()),
]

results = await asyncio.gather(*tasks)
```

Important:

> `asyncio` provides concurrency for cooperative asynchronous tasks; it does not automatically make CPU-bound Python code execute in parallel.

---

# 48. Threads

```python
from threading import Thread


def worker():
    print("working")


thread = Thread(target=worker)
thread.start()
thread.join()
```

Useful for:

* blocking I/O
* background tasks
* integrating blocking APIs

The CPython GIL historically limits parallel execution of Python bytecode in standard builds, although newer Python versions provide optional free-threaded builds.

---

# 49. Multiprocessing

For CPU-bound parallel work:

```python
from multiprocessing import Process


def worker():
    print("working")


p = Process(target=worker)
p.start()
p.join()
```

Pool:

```python
from multiprocessing import Pool

with Pool() as pool:
    results = pool.map(work, items)
```

Processes have separate memory spaces and therefore different communication costs and semantics from threads.

---

# 50. `queue`

Thread-safe queue:

```python
from queue import Queue

q = Queue()

q.put("hello")

value = q.get()
q.task_done()
```

Useful for producer/consumer architectures.

For async code:

```python
asyncio.Queue
```

---

# 51. Decorators

Decorator:

```python
def log_calls(func):
    def wrapper(*args, **kwargs):
        print("calling")
        result = func(*args, **kwargs)
        print("done")
        return result

    return wrapper
```

Use:

```python
@log_calls
def add(a, b):
    return a + b
```

Conceptually:

```python
add = log_calls(add)
```

For production decorators, use:

```python
from functools import wraps
```

---

# 52. Useful Built-ins

```python
len(x)
type(x)
isinstance(x, T)
id(x)

abs(x)
round(x)
min(x)
max(x)
sum(x)

sorted(x)
reversed(x)

enumerate(x)
zip(a, b)
range(n)

map(fn, x)
filter(fn, x)

any(x)
all(x)

open(...)
print(...)
input(...)
```

---

# 53. `zip`

Combine iterables:

```python
names = ["Alice", "Bob"]
ages = [30, 40]

for name, age in zip(names, ages):
    print(name, age)
```

Create dictionary:

```python
data = dict(zip(names, ages))
```

---

# 54. `enumerate`

Instead of:

```python
for i in range(len(items)):
    print(i, items[i])
```

prefer:

```python
for i, item in enumerate(items):
    print(i, item)
```

Starting index:

```python
for i, item in enumerate(items, start=1):
    print(i, item)
```

---

# 55. Sorting

```python
numbers.sort()
```

Returns `None` and modifies the list.

Non-mutating:

```python
sorted_numbers = sorted(numbers)
```

Key:

```python
users.sort(key=lambda user: user.age)
```

Reverse:

```python
numbers.sort(reverse=True)
```

Multiple criteria:

```python
users.sort(key=lambda u: (u.country, u.name))
```

---

# 56. Copying

Assignment does not copy an object:

```python
a = [1, 2, 3]
b = a
```

Now:

```text
a ──┐
    ├──> list
b ──┘
```

Shallow copy:

```python
b = a.copy()
```

or:

```python
b = list(a)
```

Deep copy:

```python
import copy

b = copy.deepcopy(a)
```

Be aware that shallow copies only copy the outer container.

---

# 57. Equality vs Identity

Equality:

```python
a == b
```

Identity:

```python
a is b
```

Use `is` primarily for identity checks such as:

```python
if value is None:
    ...
```

Do not use:

```python
if x is 10:
    ...
```

to test numerical equality.

---

# 58. Truthiness

These commonly evaluate as false:

```text
False
None
0
0.0
""
[]
()
{}
set()
```

Therefore:

```python
if items:
    process(items)
```

is often preferable to:

```python
if len(items) > 0:
    process(items)
```

---

# 59. Assignment Expressions

The "walrus" operator:

```python
if (match := pattern.search(text)):
    print(match.group())
```

It assigns and evaluates an expression simultaneously.

Use sparingly; readability comes first.

---

# 60. Structural Pattern Matching

Python supports `match` / `case`:

```python
match command:
    case "start":
        start()
    case "stop":
        stop()
    case _:
        print("unknown command")
```

With destructuring:

```python
match point:
    case (0, 0):
        print("origin")

    case (x, y):
        print(x, y)
```

It is more powerful than a traditional switch statement.

---

# 61. Protocol / Special Methods

Python objects can customize language operations through special methods:

```python
__init__
__str__
__repr__
__len__
__iter__
__next__
__getitem__
__setitem__
__contains__
__call__
__enter__
__exit__
__eq__
__lt__
__hash__
```

Example:

```python
class User:
    def __str__(self):
        return self.name
```

Then:

```python
print(user)
```

uses `__str__()`.

---

# 62. Resource Management

A strong Python pattern is:

```python
with resource:
    use(resource)
```

Examples:

```python
with open(...) as f:
    ...

with database.connect() as conn:
    ...

with lock:
    shared_state += 1
```

The general principle is:

> Acquire the resource, use it, and deterministically release it.

---

# 63. Common Standard Library Modules

| Module            | Purpose                    |
| ----------------- | -------------------------- |
| `pathlib`         | Filesystem paths           |
| `os`              | OS interfaces              |
| `sys`             | Python runtime             |
| `subprocess`      | External processes         |
| `shutil`          | File operations            |
| `json`            | JSON                       |
| `re`              | Regular expressions        |
| `datetime`        | Dates and times            |
| `time`            | Time-related operations    |
| `math`            | Mathematics                |
| `statistics`      | Statistics                 |
| `random`          | Random numbers             |
| `logging`         | Logging                    |
| `argparse`        | CLI arguments              |
| `dataclasses`     | Data classes               |
| `collections`     | Specialized containers     |
| `itertools`       | Iterator utilities         |
| `functools`       | Functional utilities       |
| `typing`          | Type hints                 |
| `asyncio`         | Async I/O                  |
| `threading`       | Threads                    |
| `multiprocessing` | Processes                  |
| `sqlite3`         | SQLite                     |
| `socket`          | Networking                 |
| `http`            | HTTP-related functionality |
| `unittest`        | Testing                    |

---

# 64. Performance Mental Model

Python code often follows:

```text
Python source
     |
     v
Python bytecode
     |
     v
Python interpreter/runtime
     |
     v
CPU
```

For performance-critical code, consider:

* better algorithms
* built-in operations
* iterators/generators
* avoiding unnecessary allocations
* batching work
* multiprocessing
* native extensions
* C/C++/Rust extensions
* specialized libraries

Before optimizing:

```text
measure
  ↓
identify bottleneck
  ↓
optimize
  ↓
measure again
```

Use profiling rather than guessing.

---

# 65. Common Python Pitfalls

### Mutable default arguments

Avoid:

```python
def add_item(item, items=[]):
    items.append(item)
    return items
```

Prefer:

```python
def add_item(item, items=None):
    if items is None:
        items = []

    items.append(item)
    return items
```

### Late binding in closures

Be careful with:

```python
functions = [
    lambda: i
    for i in range(3)
]
```

All functions refer to the same final `i`.

### Modifying a collection while iterating

Avoid:

```python
for item in items:
    if should_remove(item):
        items.remove(item)
```

Prefer creating a filtered collection:

```python
items = [
    item
    for item in items
    if not should_remove(item)
]
```

### Catching everything

Avoid:

```python
try:
    ...
except Exception:
    pass
```

unless you have a deliberate reason and appropriate logging/error handling.

---

# 66. Python Mental Model

The most important concepts fit together like this:

```text
                    Python
                       |
        +--------------+--------------+
        |                             |
     Objects                       Runtime
        |                             |
   +----+----+                 +------+------+
   |         |                 |             |
 types    references        interpreter   libraries
   |
   +-- int
   +-- str
   +-- list
   +-- dict
   +-- class
   +-- function
```

And for program structure:

```text
Python program
      |
      +-- expressions
      +-- statements
      +-- functions
      +-- classes
      +-- modules
      +-- packages
      |
      +-- exceptions
      +-- iterators
      +-- generators
      +-- context managers
      +-- async tasks
```

The central idea is:

> **Python is a dynamically typed, object-oriented, high-level language built around objects, references, protocols, and a powerful runtime, with syntax designed to make common operations concise and readable.**

## Related Concepts

* Python Object Model
* Names and References
* Mutability and Immutability
* Functions
* Closures
* Decorators
* Iterators
* Generators
* Context Managers
* Exceptions
* Classes and OOP
* Dataclasses
* Type Hints
* Protocols
* Modules and Packages
* `asyncio`
* Threads
* Multiprocessing
* Python GIL
* CPython
* Python Bytecode
* Python Performance
* Packaging and `pyproject.toml`
