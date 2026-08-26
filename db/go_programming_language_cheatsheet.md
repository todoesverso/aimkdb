# Go Programming Language Cheat Sheet

**Category:** Programming
**Subcategory:** Languages
**Tags:** Go, Golang, concurrency, goroutines, channels, syntax, standard library
**Type:** reference

Minimal Go program:

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, world!")
}
```

Run:

```bash
go run main.go
```

Build:

```bash
go build
```

Format:

```bash
gofmt -w .
```

Initialize a module:

```bash
go mod init example.com/myapp
```

Download/update dependencies:

```bash
go mod tidy
```

---

# 2. Variables

Explicit type:

```go
var x int = 10
```

Type inference:

```go
var x = 10
```

Short declaration:

```go
x := 10
```

Multiple variables:

```go
x, y := 10, 20
```

Zero values:

```go
var i int       // 0
var f float64   // 0
var b bool      // false
var s string    // ""
var p *int      // nil
```

Go's zero-value philosophy is important:

> Variables are automatically initialized to a useful zero value.

---

# 3. Constants

```go
const Pi = 3.14159
```

Multiple:

```go
const (
    MaxConnections = 100
    Version        = "1.0"
)
```

Constants can be untyped:

```go
const x = 10
```

and acquire a type when needed.

---

# 4. Basic Types

```text
bool

string

int
int8
int16
int32
int64

uint
uint8
uint16
uint32
uint64
uintptr

float32
float64

complex64
complex128

byte      // alias for uint8
rune      // alias for int32
```

Architecture-dependent:

```go
int
uint
```

Use `int` for normal integer calculations unless a specific width is required.

---

# 5. Type Conversion

Go does not perform implicit numeric conversions.

```go
var x int = 10
var y float64 = float64(x)
```

String/byte:

```go
data := []byte("hello")
text := string(data)
```

Rune:

```go
r := rune('A')
```

---

# 6. Operators

### Arithmetic

```go
a + b
a - b
a * b
a / b
a % b
```

### Comparison

```go
a == b
a != b
a < b
a <= b
a > b
a >= b
```

### Logical

```go
a && b
a || b
!a
```

### Bitwise

```go
a & b
a | b
a ^ b
a << n
a >> n
```

### Assignment

```go
x = 10
x += 1
x -= 1
x *= 2
x /= 2
x %= 2
```

Increment/decrement:

```go
x++
x--
```

Unlike C/C++, `++` and `--` are statements, not expressions.

---

# 7. Strings

```go
name := "Alice"
```

Concatenation:

```go
message := "Hello " + name
```

Length:

```go
len(message)
```

Indexing gives a byte:

```go
b := message[0]
```

Unicode-aware iteration:

```go
for _, r := range message {
    fmt.Println(r)
}
```

Raw string:

```go
path := `C:\Users\Alice`
```

Useful package:

```go
import "strings"

strings.ToUpper(s)
strings.ToLower(s)
strings.TrimSpace(s)
strings.Split(s, ",")
strings.Join(parts, ",")
strings.Contains(s, "hello")
strings.HasPrefix(s, "http")
strings.ReplaceAll(s, "old", "new")
```

Important:

> A Go `string` is an immutable sequence of bytes, not necessarily a sequence of Unicode characters.

---

# 8. Arrays

Fixed-size:

```go
var numbers [5]int
```

Literal:

```go
numbers := [3]int{10, 20, 30}
```

Length is part of the type:

```text
[3]int
[4]int
```

are different types.

Access:

```go
numbers[0]
```

---

# 9. Slices

Slices are Go's primary dynamic sequence type.

```go
numbers := []int{1, 2, 3}
```

Append:

```go
numbers = append(numbers, 4)
```

Multiple:

```go
numbers = append(numbers, 5, 6, 7)
```

Length:

```go
len(numbers)
```

Capacity:

```go
cap(numbers)
```

Slice:

```go
numbers[1:3]
numbers[:3]
numbers[2:]
numbers[:]
```

Create:

```go
numbers := make([]int, 10)
```

With capacity:

```go
numbers := make([]int, 0, 100)
```

---

# 10. Slice Internals

A slice is conceptually:

```text
slice
  |
  +-- pointer ──────> backing array
  +-- length
  +-- capacity
```

Therefore:

```go
a := []int{1, 2, 3}
b := a[:2]

b[0] = 100
```

also changes the underlying array visible through `a`.

Copy:

```go
b := make([]int, len(a))
copy(b, a)
```

---

# 11. Maps

Create:

```go
users := map[string]int{
    "alice": 30,
    "bob":   40,
}
```

Access:

```go
age := users["alice"]
```

Check existence:

```go
age, ok := users["alice"]

if ok {
    fmt.Println(age)
}
```

Delete:

```go
delete(users, "alice")
```

Create with `make`:

```go
users := make(map[string]int)
```

Assign:

```go
users["alice"] = 30
```

Maps are reference-like runtime structures and must be initialized before assigning to them.

---

# 12. `if`

```go
if x > 10 {
    fmt.Println("large")
} else if x > 0 {
    fmt.Println("positive")
} else {
    fmt.Println("non-positive")
}
```

Initialization in `if`:

```go
if value, err := getValue(); err != nil {
    fmt.Println(err)
} else {
    fmt.Println(value)
}
```

The variables declared in the initialization are scoped to the `if` statement.

---

# 13. `for`

Go has one looping construct: `for`.

Traditional:

```go
for i := 0; i < 10; i++ {
    fmt.Println(i)
}
```

While-style:

```go
for x < 10 {
    x++
}
```

Infinite:

```go
for {
    work()
}
```

Break:

```go
for {
    if done {
        break
    }
}
```

Continue:

```go
for i := 0; i < 10; i++ {
    if i%2 == 0 {
        continue
    }

    fmt.Println(i)
}
```

---

# 14. `range`

Slice:

```go
for i, value := range numbers {
    fmt.Println(i, value)
}
```

Value only:

```go
for _, value := range numbers {
    fmt.Println(value)
}
```

Index only:

```go
for i := range numbers {
    fmt.Println(i)
}
```

Map:

```go
for key, value := range users {
    fmt.Println(key, value)
}
```

String:

```go
for i, r := range text {
    fmt.Println(i, r)
}
```

For strings, `range` decodes UTF-8 into runes.

---

# 15. Functions

Basic:

```go
func add(a int, b int) int {
    return a + b
}
```

Equivalent parameter declaration:

```go
func add(a, b int) int {
    return a + b
}
```

Multiple returns:

```go
func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }

    return a / b, nil
}
```

---

# 16. Named Return Values

```go
func divide(a, b int) (result int, err error) {
    if b == 0 {
        err = errors.New("division by zero")
        return
    }

    result = a /[118;1:3u b
    return
}
```

Named returns are useful in some cases but should not be overused.

---

# 17. Variadic Functions

```go
func sum(values ...int) int {
    total := 0

    for _, value := range values {
        total += value
    }

    return total
}
```

Call:

```go
sum(1, 2, 3, 4)
```

Slice expansion:

```go
values := []int{1, 2, 3}

sum(values...)
```

---

# 18. Functions as Values

```go
add := func(a, b int) int {
    return a + b
}

result := add(10, 20)
```

Function type:

```go
type BinaryOp func(int, int) int
```

Higher-order function:

```go
func apply(op BinaryOp, a, b int) int {
    return op(a, b)
}
```

---

# 19. Closures

```go
func counter() func() int {
    n := 0

    return func() int {
        n++
        return n
    }
}
```

Usage:

```go
next := counter()

fmt.Println(next()) // 1
fmt.Println(next()) // 2
fmt.Println(next()) // 3
```

The returned function captures `n`.

---

# 20. Structs

```go
type User struct {
    Name string
    Age  int
}
```

Create:

```go
user := User{
    Name: "Alice",
    Age:  30,
}
```

Access:

```go
fmt.Println(user.Name)
```

Anonymous initialization:

```go
user := User{"Alice", 30}
```

Prefer named fields for maintainability.

---

# 21. Methods

```go
type User struct {
    Name string
}

func (u User) Greet() string {
    return "Hello " + u.Name
}
```

Call:

```go
user.Greet()
```

Pointer receiver:

```go
func (u *User) Rename(name string) {
    u.Name = name
}
```

---

# 22. Value vs Pointer Receivers

Value receiver:

```go
func (u User) Name() string {
    return u.Name
}
```

Pointer receiver:

```go
func (u *User) Rename(name string) {
    u.Name = name
}
```

Use a pointer receiver when:

* the method modifies the object
* copying the struct is undesirable
* the type is large
* you want a consistent method set

---

# 23. Pointers

```go
x := 10

p := &x
```

Dereference:

```go
fmt.Println(*p)
```

Modify:

```go
*p = 20
```

Pointer:

```go
var p *int
```

Zero value:

```go
p == nil
```

Unlike C, Go intentionally removes pointer arithmetic.

---

# 24. `new` vs `make`

`new` allocates zeroed storage and returns a pointer:

```go
p := new(int)
```

`make` initializes runtime data structures:

```go
slice := make([]int, 10)
m := make(map[string]int)
ch := make(chan int)
```

Rule of thumb:

```text
new(T)       → *T
make(...)    → slice/map/channel
```

---

# 25. Interfaces

Interface:

```go
type Speaker interface {
    Speak() string
}
```

Implementation is implicit:

```go
type Dog struct{}

func (Dog) Speak() string {
    return "woof"
}
```

No explicit:

```text
implements Speaker
```

is required.

Use:

```go
var s Speaker = Dog{}

fmt.Println(s.Speak())
```

This is one of Go's most important design features.

---

# 26. Interface Composition

```go
type Reader interface {
    Read([]byte) (int, error)
}

type Writer interface {
    Write([]byte) (int, error)
}

type ReadWriter interface {
    Reader
    Writer
}
```

Interfaces are commonly kept small.

A famous Go design principle:

> Prefer small interfaces.

---

# 27. Empty Interface / `any`

```go
var value any

value = 10
value = "hello"
value = User{}
```

`any` is an alias for:

```go
interface{}
```

However, avoid using `any` everywhere. Prefer precise types and interfaces.

---

# 28. Type Assertions

```go
value, ok := x.(string)

if ok {
    fmt.Println(value)
}
```

Without checking:

```go
value := x.(string)
```

This panics if the dynamic value isn't a string.

---

# 29. Type Switch

```go
switch value := x.(type) {
case int:
    fmt.Println("int:", value)

case string:
    fmt.Println("string:", value)

default:
    fmt.Println("unknown")
}
```

Useful when handling multiple concrete types stored behind an interface.

---

# 30. `switch`

```go
switch command {
case "start":
    start()

case "stop":
    stop()

case "restart":
    restart()

default:
    fmt.Println("unknown command")
}
```

No implicit fallthrough.

Multiple cases:

```go
switch day {
case "Saturday", "Sunday":
    fmt.Println("weekend")
}
```

Expression-less switch:

```go
switch {
case x < 0:
    ...
case x == 0:
    ...
default:
    ...
}
```

---

# 31. Errors

Go normally represents expected failures with `error`.

```go
func load() error {
    ...
}
```

Create:

```go
err := errors.New("something went wrong")
```

Return:

```go
return fmt.Errorf("loading config: %w", err)
```

Check:

```go
if err != nil {
    return err
}
```

This pattern is fundamental to Go.

---

# 32. Error Wrapping

```go
return fmt.Errorf("open configuration: %w", err)
```

Check underlying error:

```go
if errors.Is(err, os.ErrNotExist) {
    ...
}
```

Extract a specific error type:

```go
var pathErr *os.PathError

if errors.As(err, &pathErr) {
    ...
}
```

---

# 33. `panic` and `recover`

Panic:

```go
panic("unexpected state")
```

Recover:

```go
defer func() {
    if r := recover(); r != nil {
        fmt.Println("recovered:", r)
    }
}()
```

Use panics for truly exceptional programming/runtime conditions, not ordinary expected errors.

---

# 34. `defer`

```go
func readFile() error {
    f, err := os.Open("data.txt")
    if err != nil {
        return err
    }

    defer f.Close()

    ...
}
```

Deferred calls execute when the surrounding function returns.

Multiple:

```go
defer cleanup1()
defer cleanup2()
```

Execution is LIFO:

```text
cleanup2
cleanup1
```

---

# 35. Goroutines

Start concurrent execution:

```go
go doWork()
```

Example:

```go
go func() {
    fmt.Println("background work")
}()
```

A goroutine is a lightweight concurrent execution unit managed by the Go runtime.

---

# 36. Channels

Create:

```go
ch := make(chan int)
```

Send:

```go
ch <- 42
```

Receive:

```go
value := <-ch
```

Close:

```go
close(ch)
```

Typical pattern:

```go
go func() {
    ch <- 42
}()

value := <-ch
```

Channels are commonly used to communicate between goroutines.

---

# 37. Buffered Channels

Unbuffered:

```go
ch := make(chan int)
```

Buffered:

```go
ch := make(chan int, 10)
```

The buffer allows sends to proceed until the channel is full.

---

# 38. Channel Direction

Send-only:

```go
chan<- int
```

Receive-only:

```go
<-chan int
```

Example:

```go
func producer(out chan<- int) {
    out <- 42
}
```

```go
func consumer(in <-chan int) {
    value := <-in
    fmt.Println(value)
}
```

Directional channels make APIs safer and self-documenting.

---

# 39. `select`

Wait on multiple channel operations:

```go
select {
case value := <-ch:
    fmt.Println(value)

case <-done:
    return
}
```

Timeout:

```go
select {
case value := <-ch:
    fmt.Println(value)

case <-time.After(time.Second):
    fmt.Println("timeout")
}
```

`select` is central to Go's concurrent programming model.

---

# 40. Closing Channels

Producer:

```go
func producer(ch chan<- int) {
    defer close(ch)

    for i := 0; i < 10; i++ {
        ch <- i
    }
}
```

Consumer:

```go
for value := range ch {
    fmt.Println(value)
}
```

Important rule:

> Usually the sender/producer closes a channel, not the receiver.

Receiving from a closed channel returns its zero value. To detect closure:

```go
value, ok := <-ch

if !ok {
    // closed
}
```

---

# 41. `sync.WaitGroup`

Wait for goroutines:

```go
var wg sync.WaitGroup

wg.Add(2)

go func() {
    defer wg.Done()
    work()
}()

go func() {
    defer wg.Done()
    work()
}()

wg.Wait()
```

Modern Go code may also use `errgroup`-style structured concurrency patterns when error propagation matters.

---

# 42. Mutexes

Protect shared state:

```go
var mu sync.Mutex
var counter int

mu.Lock()
counter++
mu.Unlock()
```

Better:

```go
mu.Lock()
defer mu.Unlock()

counter++
```

Read/write mutex:

```go
var mu sync.RWMutex

mu.RLock()
value := data
mu.RUnlock()
```

---

# 43. Atomic Operations

For simple atomic state:

```go
var counter atomic.Int64

counter.Add(1)

value := counter.Load()
```

Atomics can avoid a mutex for suitable operations but require careful reasoning about synchronization.

---

# 44. Context

`context.Context` is used to propagate:

* cancellation
* deadlines
* request-scoped values

Example:

```go
ctx, cancel := context.WithTimeout(
    context.Background(),
    time.Second,
)
defer cancel()
```

Check cancellation:

```go
select {
case <-ctx.Done():
    return ctx.Err()

default:
}
```

Typical function signature:

```go
func fetch(ctx context.Context) error {
    ...
}
```

Convention:

> `context.Context` is normally the first parameter.

---

# 45. Packages

Directory:

```text
myapp/
├── go.mod
├── main.go
└── internal/
    └── config/
        └── config.go
```

Package declaration:

```go
package config
```

Import:

```go
import "example.com/myapp/internal/config"
```

Use:

```go
config.Load()
```

---

# 46. Exported vs Unexported

Uppercase identifier:

```go
func LoadConfig() {}
```

Exported.

Lowercase:

```go
func loadConfig() {}
```

Unexported.

Same for types and fields:

```go
type User struct {
    Name string
    age  int
}
```

`Name` is exported; `age` is not.

Go's visibility system is intentionally simple:

```text
Uppercase → exported
lowercase → package-private
```

---

# 47. Imports

Single:

```go
import "fmt"
```

Multiple:

```go
import (
    "fmt"
    "os"
    "strings"
)
```

Alias:

```go
import j "encoding/json"
```

Blank import:

```go
import _ "some/package"
```

Usually used for packages whose initialization side effects are intentional.

---

# 48. Modules

Initialize:

```bash
go mod init example.com/project
```

Add dependency:

```bash
go get example.com/library
```

Remove unused dependencies:

```bash
go mod tidy
```

Build all packages:

```bash
go build ./...
```

Test all packages:

```bash
go test ./...
```

---

# 49. Testing

File:

```text
math_test.go
```

Test:

```go
func TestAdd(t *testing.T) {
    result := Add(2, 3)

    if result != 5 {
        t.Fatalf("expected 5, got %d", result)
    }
}
```

Run:

```bash
go test ./...
```

Verbose:

```bash
go test -v ./...
```

---

# 50. Table-Driven Tests

A very common Go pattern:

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name string
        a    int
        b    int
        want int
    }{
        {"positive", 2, 3, 5},
        {"zero", 0, 3, 3},
        {"negative", -2, 3, 1},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)

            if got != tt.want {
                t.Fatalf("got %d, want %d", got, tt.want)
            }
        })
    }
}
```

---

# 51. Benchmarks

```go
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(10, 20)
    }
}
```

Run:

```bash
go test -bench=.
```

Memory benchmark:

```bash
go test -bench=. -benchmem
```

---

# 52. Fuzzing

Go has built-in fuzz testing:

```go
func FuzzParse(f *testing.F) {
    f.Add("hello")

    f.Fuzz(func(t *testing.T, input string) {
        Parse(input)
    })
}
```

Run:

```bash
go test -fuzz=FuzzParse
```

Useful for parsers, protocol implementations, input validation, and other code with large input spaces.

---

# 53. HTTP Server

Minimal server:

```go
http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintln(w, "Hello")
})

http.ListenAndServe(":8080", nil)
```

Modern handler:

```go
func hello(w http.ResponseWriter, r *http.Request) {
    w.Write([]byte("hello"))
}
```

Server:

```go
server := &http.Server{
    Addr:    ":8080",
    Handler: mux,
}

server.ListenAndServe()
```

---

# 54. HTTP Client

```go
resp, err := http.Get("https://example.com")
if err != nil {
    return err
}
defer resp.Body.Close()
```

Read body:

```go
body, err := io.ReadAll(resp.Body)
if err != nil {
    return err
}
```

For production clients, explicitly configure timeouts and reuse an `http.Client`.

---

# 55. JSON

Struct:

```go
type User struct {
    Name string `json:"name"`
    Age  int    `json:"age"`
}
```

Marshal:

```go
data, err := json.Marshal(user)
```

Unmarshal:

```go
var user User

err := json.Unmarshal(data, &user)
```

Pretty JSON:

```go
data, err := json.MarshalIndent(user, "", "  ")
```

---

# 56. Files

Read:

```go
data, err := os.ReadFile("data.txt")
```

Write:

```go
err := os.WriteFile(
    "data.txt",
    []byte("hello"),
    0644,
)
```

Open:

```go
f, err := os.Open("data.txt")
if err != nil {
    return err
}
defer f.Close()
```

Create:

```go
f, err := os.Create("data.txt")
```

---

# 57. Paths

```go
import "path/filepath"
```

Join:

```go
path := filepath.Join("data", "users", "alice.json")
```

Base:

```go
filepath.Base(path)
```

Directory:

```go
filepath.Dir(path)
```

Extension:

```go
filepath.Ext(path)
```

---

# 58. Command Execution

```go
cmd := exec.Command("ls", "-la")

output, err := cmd.Output()
```

With arguments:

```go
cmd := exec.Command(
    "ffmpeg",
    "-i", "input.mp4",
    "output.mp4",
)
```

For long-running processes or interactive I/O, configure:

```go
cmd.Stdin
cmd.Stdout
cmd.Stderr
```

---

# 59. Environment Variables

```go
value := os.Getenv("DATABASE_URL")
```

Check existence:

```go
value, ok := os.LookupEnv("DATABASE_URL")
```

Set:

```go
os.Setenv("MODE", "production")
```

---

# 60. CLI Arguments

```go
import "os"

args := os.Args
```

Example:

```go
fmt.Println(os.Args[1:])
```

For structured CLI flags:

```go
import "flag"

port := flag.Int("port", 8080, "server port")

flag.Parse()

fmt.Println(*port)
```

---

# 61. Logging

Basic:

```go
log.Println("starting server")
```

Formatted:

```go
log.Printf("port=%d", port)
```

Fatal:

```go
log.Fatal(err)
```

Structured logging:

```go
logger := slog.New(
    slog.NewTextHandler(os.Stdout, nil),
)

logger.Info(
    "server started",
    "port", 8080,
)
```

For modern Go applications, `log/slog` is the standard structured logging option.

---

# 62. Time

```go
now := time.Now()
```

Duration:

```go
time.Second
time.Millisecond
time.Minute
time.Hour
```

Sleep:

```go
time.Sleep(time.Second)
```

Deadline:

```go
deadline := time.Now().Add(5 * time.Second)
```

Ticker:

```go
ticker := time.NewTicker(time.Second)
defer ticker.Stop()

for range ticker.C {
    work()
}
```

---

# 63. SQL

Database package:

```go
import "database/sql"
```

Open:

```go
db, err := sql.Open("driver", "connection")
```

Query:

```go
rows, err := db.Query(
    "SELECT id, name FROM users",
)
```

Parameterized query:

```go
row := db.QueryRow(
    "SELECT name FROM users WHERE id = ?",
    id,
)
```

Always parameterize external values instead of constructing SQL strings manually.

---

# 64. Generics

Go supports generic functions:

```go
func Max[T constraints.Ordered](a, b T) T {
    if a > b {
        return a
    }

    return b
}
```

A modern example using a standard constraint:

```go
func Map[T any, R any](
    values []T,
    fn func(T) R,
) []R {
    result := make([]R, len(values))

    for i, value := range values {
        result[i] = fn(value)
    }

    return result
}
```

Generics are useful when the same algorithm genuinely applies across multiple types.

---

# 65. Generic Types

```go
type Stack[T any] struct {
    values []T
}

func (s *Stack[T]) Push(value T) {
    s.values = append(s.values, value)
}

func (s *Stack[T]) Pop() T {
    value := s.values[len(s.values)-1]
    s.values = s.values[:len(s.values)-1]

    return value
}
```

Use:

```go
stack := Stack[int]{}
stack.Push(10)
stack.Push(20)
```

---

# 66. `any` vs Generics vs Interfaces

Think of them differently:

```text
interface
    → common behavior

generic
    → same algorithm for different types

any
    → deliberately accept arbitrary values
```

Example interface:

```go
type Reader interface {
    Read([]byte) (int, error)
}
```

Generic:

```go
func First[T any](items []T) T {
    return items[0]
}
```

`any`:

```go
func Debug(value any) {
    fmt.Printf("%#v\n", value)
}
```

---

# 67. Memory and Escape Analysis

Go manages memory automatically with garbage collection.

A variable may "escape" from stack allocation to heap allocation when necessary.

Inspect compiler decisions:

```bash
go build -gcflags="-m" .
```

Typical mental model:

```text
Go code
   |
   v
compiler
   |
   +-- stack allocations
   |
   +-- heap allocations
             |
             v
        garbage collector
```

You generally should not manually manage memory.

---

# 68. Garbage Collection

Go uses a concurrent garbage collector.

You generally control performance by:

* reducing unnecessary allocations
* reusing buffers
* choosing appropriate data structures
* avoiding needless conversions
* profiling before optimizing

Useful tools:

```bash
go test -bench=. -benchmem
go tool pprof
```

---

# 69. Race Detector

One of the most valuable Go tools:

```bash
go test -race ./...
```

Also:

```bash
go run -race .
```

It detects many data races involving concurrent memory accesses.

Typical workflow:

```text
write concurrent code
        ↓
go test -race ./...
        ↓
fix races
        ↓
benchmark/profile
```

---

# 70. Profiling

CPU profile:

```bash
go test -cpuprofile=cpu.out
```

Memory profile:

```bash
go test -memprofile=mem.out
```

Analyze:

```bash
go tool pprof cpu.out
```

For HTTP services, Go also provides `net/http/pprof`.

---

# 71. Go Toolchain

Useful commands:

```bash
go run .
go build .
go test ./...
go fmt ./...
go vet ./...
go mod tidy
go list ./...
go doc package
go env
go version
```

A common quality check:

```bash
gofmt -w .
go vet ./...
go test ./...
go test -race ./...
```

---

# 72. `go vet`

Static analysis:

```bash
go vet ./...
```

It detects certain suspicious constructs and common mistakes.

For larger projects, combine it with additional static-analysis tools such as `staticcheck`.

---

# 73. Naming Conventions

Go favors short, descriptive names:

```go
i
err
ctx
req
resp
cfg
```

Exported:

```go
type HTTPServer struct {}
```

Unexported:

```go
type serverConfig struct {}
```

Acronyms are normally capitalized consistently:

```text
HTTP
URL
API
ID
JSON
```

rather than:

```text
Http
Url
Api
Id
Json
```

---

# 74. Go Formatting

Go has an intentionally standardized formatter:

```bash
gofmt -w .
```

Most Go projects do not debate formatting style.

The philosophy is essentially:

> Let the tool decide the formatting.

This is one reason Go codebases tend to have very consistent formatting.

---

# 75. Common Project Layout

A simple application:

```text
myapp/
├── go.mod
├── go.sum
├── main.go
├── config.go
├── server.go
└── user.go
```

Larger project:

```text
myapp/
├── go.mod
├── cmd/
│   └── myapp/
│       └── main.go
├── internal/
│   ├── config/
│   ├── server/
│   └── database/
├── pkg/
└── api/
```

Do not introduce elaborate directory structures without a reason.

---

# 76. Common Go Idioms

### Handle errors immediately

```go
value, err := operation()
if err != nil {
    return err
}
```

### Defer cleanup

```go
f, err := os.Open(path)
if err != nil {
    return err
}
defer f.Close()
```

### Prefer early returns

Instead of deeply nested code:

```go
if err != nil {
    return err
}
```

### Keep interfaces small

```go
type Reader interface {
    Read([]byte) (int, error)
}
```

### Pass context explicitly

```go
func Process(ctx context.Context, data []byte) error {
    ...
}
```

### Make the zero value useful

Design types so:

```go
var x T
```

is usable whenever practical.

---

# 77. Go Concurrency Mental Model

The core pieces:

```text
                    Go Concurrency
                          |
          +---------------+---------------+
          |               |               |
      Goroutines       Channels        Shared State
          |               |               |
          |          communication       |
          |               |          +----+----+
          |               |          |         |
          |             select      Mutex    Atomic
          |                          |
          +-------------+------------+
                        |
                    sync / context
```

A good Go concurrency design often looks like:

```text
goroutine
    |
    +---- channel ----> goroutine
    |
    +---- context ----> cancellation
    |
    +---- waitgroup --> lifecycle
```

But channels are not mandatory. Mutexes and atomics are often the simpler solution for shared state.

---

# 78. Go's Core Design Philosophy

Several ideas explain much of the language:

```text
simplicity
    ↓
small language
    ↓
explicit behavior
    ↓
composition
    ↓
concurrency
    ↓
tooling
```

Particularly important:

* explicit error handling
* implicit interface implementation
* composition over inheritance
* goroutines
* channels
* simple syntax
* garbage collection
* static typing
* fast compilation
* standardized tooling

---

# 79. Go vs C / Rust / Python — Quick Mental Map

| Concept                    | C                    | Go                  | Rust                       | Python                    |
| -------------------------- | -------------------- | ------------------- | -------------------------- | ------------------------- |
| Memory management          | Manual               | GC                  | Ownership/RAII             | GC/refcount               |
| Static typing              | Yes                  | Yes                 | Yes                        | No                        |
| Generics                   | Limited              | Yes                 | Yes                        | Runtime typing            |
| Interfaces                 | No native equivalent | Yes                 | Traits                     | Protocols/duck typing     |
| Exceptions                 | No                   | No                  | No                         | Yes                       |
| Error values               | Common               | Idiomatic           | Idiomatic                  | Less central              |
| Concurrency                | Threads/processes    | Goroutines/channels | Threads/async              | Threads/async/processes   |
| Pointer arithmetic         | Yes                  | No                  | No safe pointer arithmetic | No                        |
| GC                         | No                   | Yes                 | No tracing GC              | Yes                       |
| Compilation                | Native               | Native              | Native                     | Bytecode/interpreter      |
| Main concurrency primitive | OS threads           | Goroutines          | Threads/async              | asyncio/threads/processes |

---

# 80. The Go Mental Model

The most useful way to organize Go in your head is:

```text
                         GO
                          |
       +------------------+------------------+
       |                  |                  |
    Types              Functions         Packages
       |                  |                  |
  +----+----+        +----+----+        +----+----+
  |         |        |         |        |         |
struct   interface  methods  closures  modules  imports
  |
  +-- pointers
  +-- slices
  +-- maps
  +-- arrays

       +------------------+
       |
   Concurrency
       |
   +---+----+-------+
   |        |       |
goroutine channel  select
            |
         context
```

And the central Go philosophy can be summarized as:

> **Keep the language and abstractions simple, make behavior explicit, compose small pieces, and use concurrency as a first-class part of system design.**

## High-Value Topics to Learn Next

For a strong Go foundation, the most important topics after basic syntax are:

1. **Pointers and value semantics**
2. **Slices and their backing arrays**
3. **Interfaces and implicit implementation**
4. **Error handling and error wrapping**
5. **Goroutines**
6. **Channels and `select`**
7. **Context cancellation**
8. **Mutexes and race conditions**
9. **Memory allocation and escape analysis**
10. **Generics**
11. **HTTP/network programming**
12. **Testing and benchmarking**
13. **Profiling with pprof**
14. **Go modules and package design**
15. **Go's runtime and garbage collector**
