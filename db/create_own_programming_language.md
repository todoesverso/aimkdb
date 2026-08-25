# Creating Your Own Programming Language in C

**Category:** Programming Languages
**Subcategory:** Language Implementation / Compilers / Interpreters
**Tags:** C, compiler, interpreter, lexer, parser, AST, programming language design

The easiest way to learn how programming languages work is to build a **small interpreted language first**.

We'll build a working language called **MiniLang** with:

```text
let x = 10;
let y = 20;
print x + y * 2;
```

It will support:

* integer literals
* variables
* variable assignment
* `+`, `-`, `*`, `/`
* parentheses
* `print`
* `let`
* multiple statements

We'll implement the whole thing in **C**, without external libraries.

---

# 1. What We're Building

The architecture will be:

```text
                 MiniLang source
                       │
                       ▼
                    LEXER
                       │
                       ▼
                    TOKENS
                       │
                       ▼
                    PARSER
                       │
                       ▼
                      AST
                       │
                       ▼
                  INTERPRETER
                       │
                       ▼
                     OUTPUT
```

For example:

```text
let x = 10 + 20 * 3;
```

becomes approximately:

```text
             =
           /   \
          x     +
               / \
             10   *
                 / \
                20  3
```

Then the interpreter evaluates that tree.

---

# 2. Why Start With an Interpreter?

There are three common approaches.

### Interpreter

```text
source
  ↓
tokens
  ↓
AST
  ↓
execute
```

### Compiler

```text
source
  ↓
tokens
  ↓
AST
  ↓
IR
  ↓
machine code
  ↓
executable
```

### Transpiler

```text
MiniLang
   ↓
parser
   ↓
C code
   ↓
C compiler
   ↓
executable
```

For learning language implementation, an interpreter is the simplest starting point.

Once it works, you can replace the interpreter with a compiler.

---

# 3. Our Language

We'll call it:

```text
MiniLang
```

A program looks like:

```text
let x = 10;
let y = 20;

print x;
print x + y;
print x * y + 5;
```

Output:

```text
10
30
205
```

We need these tokens:

```text
NUMBER
IDENTIFIER

LET
PRINT

+
-
*
/
=
(
)
;
```

---

# 4. Complete Working Implementation

Put the following into:

```text
minilang.c
```

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

/* ============================================================
 * LEXER
 * ============================================================ */

typedef enum {
    TOKEN_EOF,

    TOKEN_NUMBER,
    TOKEN_IDENTIFIER,

    TOKEN_LET,
    TOKEN_PRINT,

    TOKEN_PLUS,
    TOKEN_MINUS,
    TOKEN_STAR,
    TOKEN_SLASH,

    TOKEN_EQUAL,

    TOKEN_LPAREN,
    TOKEN_RPAREN,

    TOKEN_SEMICOLON
} TokenType;

typedef struct {
    TokenType type;
    char *text;
    long value;
} Token;

typedef struct {
    const char *source;
    size_t position;
} Lexer;

static char *copy_string(const char *start, size_t length)
{
    char *result = malloc(length + 1);

    if (!result) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    memcpy(result, start, length);
    result[length] = '\0';

    return result;
}

static void lexer_init(Lexer *lexer, const char *source)
{
    lexer->source = source;
    lexer->position = 0;
}

static char lexer_peek(Lexer *lexer)
{
    return lexer->source[lexer->position];
}

static char lexer_advance(Lexer *lexer)
{
    return lexer->source[lexer->position++];
}

static void skip_whitespace(Lexer *lexer)
{
    while (isspace((unsigned char)lexer_peek(lexer))) {
        lexer_advance(lexer);
    }
}

static Token make_token(TokenType type)
{
    Token token = {
        .type = type,
        .text = NULL,
        .value = 0
    };

    return token;
}

static Token lexer_next(Lexer *lexer)
{
    skip_whitespace(lexer);

    char c = lexer_peek(lexer);

    if (c == '\0') {
        return make_token(TOKEN_EOF);
    }

    /* Number */
    if (isdigit((unsigned char)c)) {
        const char *start = lexer->source + lexer->position;

        long value = 0;

        while (isdigit((unsigned char)lexer_peek(lexer))) {
            value = value * 10 + (lexer_advance(lexer) - '0');
        }

        size_t length =
            (size_t)(lexer->source + lexer->position - start);

        Token token = make_token(TOKEN_NUMBER);

        token.text = copy_string(start, length);
        token.value = value;

        return token;
    }

    /* Identifier / keyword */
    if (isalpha((unsigned char)c) || c == '_') {
        const char *start = lexer->source + lexer->position;

        while (isalnum((unsigned char)lexer_peek(lexer)) ||
               lexer_peek(lexer) == '_') {
            lexer_advance(lexer);
        }

        size_t length =
            (size_t)(lexer->source + lexer->position - start);

        char *text = copy_string(start, length);

        Token token;

        if (strcmp(text, "let") == 0) {
            token = make_token(TOKEN_LET);
        } else if (strcmp(text, "print") == 0) {
            token = make_token(TOKEN_PRINT);
        } else {
            token = make_token(TOKEN_IDENTIFIER);
        }

        token.text = text;

        return token;
    }

    lexer_advance(lexer);

    switch (c) {
    case '+':
        return make_token(TOKEN_PLUS);

    case '-':
        return make_token(TOKEN_MINUS);

    case '*':
        return make_token(TOKEN_STAR);

    case '/':
        return make_token(TOKEN_SLASH);

    case '=':
        return make_token(TOKEN_EQUAL);

    case '(':
        return make_token(TOKEN_LPAREN);

    case ')':
        return make_token(TOKEN_RPAREN);

    case ';':
        return make_token(TOKEN_SEMICOLON);

    default:
        fprintf(stderr, "Unknown character: '%c'\n", c);
        exit(EXIT_FAILURE);
    }
}


/* ============================================================
 * AST
 * ============================================================ */

typedef enum {
    EXPR_NUMBER,
    EXPR_VARIABLE,
    EXPR_BINARY
} ExprType;

typedef enum {
    OP_ADD,
    OP_SUB,
    OP_MUL,
    OP_DIV
} BinaryOp;

typedef struct Expr Expr;

struct Expr {
    ExprType type;

    union {
        long number;

        char *variable;

        struct {
            BinaryOp op;
            Expr *left;
            Expr *right;
        } binary;
    };
};

static Expr *new_number(long value)
{
    Expr *expr = malloc(sizeof(*expr));

    if (!expr) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    expr->type = EXPR_NUMBER;
    expr->number = value;

    return expr;
}

static Expr *new_variable(const char *name)
{
    Expr *expr = malloc(sizeof(*expr));

    if (!expr) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    expr->type = EXPR_VARIABLE;
    expr->variable = strdup(name);

    return expr;
}

static Expr *new_binary(BinaryOp op, Expr *left, Expr *right)
{
    Expr *expr = malloc(sizeof(*expr));

    if (!expr) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    expr->type = EXPR_BINARY;
    expr->binary.op = op;
    expr->binary.left = left;
    expr->binary.right = right;

    return expr;
}


/* ============================================================
 * PARSER
 * ============================================================ */

typedef struct {
    Lexer lexer;
    Token current;
} Parser;

static void parser_advance(Parser *parser)
{
    free(parser->current.text);

    parser->current = lexer_next(&parser->lexer);
}

static void parser_init(Parser *parser, const char *source)
{
    lexer_init(&parser->lexer, source);

    parser->current = lexer_next(&parser->lexer);
}

static void parser_error(Parser *parser, const char *message)
{
    fprintf(
        stderr,
        "Parse error: %s\n",
        message
    );

    exit(EXIT_FAILURE);
}

static void expect(Parser *parser, TokenType type)
{
    if (parser->current.type != type) {
        parser_error(parser, "unexpected token");
    }

    parser_advance(parser);
}

/*
 * Grammar:
 *
 * expression  -> addition
 *
 * addition    -> multiplication
 *                (("+" | "-") multiplication)*
 *
 * multiplication -> primary
 *                (("*" | "/") primary)*
 *
 * primary     -> NUMBER
 *             | IDENTIFIER
 *             | "(" expression ")"
 */

static Expr *parse_expression(Parser *parser);

static Expr *parse_primary(Parser *parser)
{
    Token *token = &parser->current;

    if (token->type == TOKEN_NUMBER) {
        long value = token->value;

        parser_advance(parser);

        return new_number(value);
    }

    if (token->type == TOKEN_IDENTIFIER) {
        Expr *expr = new_variable(token->text);

        parser_advance(parser);

        return expr;
    }

    if (token->type == TOKEN_LPAREN) {
        parser_advance(parser);

        Expr *expr = parse_expression(parser);

        expect(parser, TOKEN_RPAREN);

        return expr;
    }

    parser_error(parser, "expected expression");

    return NULL;
}

static Expr *parse_multiplication(Parser *parser)
{
    Expr *left = parse_primary(parser);

    while (parser->current.type == TOKEN_STAR ||
           parser->current.type == TOKEN_SLASH) {

        TokenType type = parser->current.type;

        parser_advance(parser);

        Expr *right = parse_primary(parser);

        BinaryOp op =
            type == TOKEN_STAR ? OP_MUL : OP_DIV;

        left = new_binary(op, left, right);
    }

    return left;
}

static Expr *parse_expression(Parser *parser)
{
    Expr *left = parse_multiplication(parser);

    while (parser->current.type == TOKEN_PLUS ||
           parser->current.type == TOKEN_MINUS) {

        TokenType type = parser->current.type;

        parser_advance(parser);

        Expr *right = parse_multiplication(parser);

        BinaryOp op =
            type == TOKEN_PLUS ? OP_ADD : OP_SUB;

        left = new_binary(op, left, right);
    }

    return left;
}


/* ============================================================
 * VARIABLES
 * ============================================================ */

#define MAX_VARIABLES 256

typedef struct {
    char *name;
    long value;
} Variable;

typedef struct {
    Variable variables[MAX_VARIABLES];
    size_t count;
} Environment;

static void environment_set(
    Environment *env,
    const char *name,
    long value)
{
    for (size_t i = 0; i < env->count; i++) {
        if (strcmp(env->variables[i].name, name) == 0) {
            env->variables[i].value = value;
            return;
        }
    }

    if (env->count >= MAX_VARIABLES) {
        fprintf(stderr, "Too many variables\n");
        exit(EXIT_FAILURE);
    }

    env->variables[env->count].name = strdup(name);
    env->variables[env->count].value = value;

    env->count++;
}

static long environment_get(
    Environment *env,
    const char *name)
{
    for (size_t i = 0; i < env->count; i++) {
        if (strcmp(env->variables[i].name, name) == 0) {
            return env->variables[i].value;
        }
    }

    fprintf(stderr, "Undefined variable: %s\n", name);
    exit(EXIT_FAILURE);
}


/* ============================================================
 * INTERPRETER
 * ============================================================ */

static long evaluate(
    Expr *expr,
    Environment *env)
{
    switch (expr->type) {

    case EXPR_NUMBER:
        return expr->number;

    case EXPR_VARIABLE:
        return environment_get(
            env,
            expr->variable
        );

    case EXPR_BINARY: {
        long left =
            evaluate(expr->binary.left, env);

        long right =
            evaluate(expr->binary.right, env);

        switch (expr->binary.op) {

        case OP_ADD:
            return left + right;

        case OP_SUB:
            return left - right;

        case OP_MUL:
            return left * right;

        case OP_DIV:
            if (right == 0) {
                fprintf(stderr, "Division by zero\n");
                exit(EXIT_FAILURE);
            }

            return left / right;
        }
    }
    }

    fprintf(stderr, "Invalid expression\n");
    exit(EXIT_FAILURE);
}


/* ============================================================
 * STATEMENTS
 * ============================================================ */

static void parse_program(Parser *parser)
{
    Environment env = {0};

    while (parser->current.type != TOKEN_EOF) {

        /* let NAME = expression; */

        if (parser->current.type == TOKEN_LET) {

            parser_advance(parser);

            if (parser->current.type != TOKEN_IDENTIFIER) {
                parser_error(
                    parser,
                    "expected variable name"
                );
            }

            char *name =
                strdup(parser->current.text);

            parser_advance(parser);

            expect(parser, TOKEN_EQUAL);

            Expr *expr =
                parse_expression(parser);

            expect(parser, TOKEN_SEMICOLON);

            long value =
                evaluate(expr, &env);

            environment_set(
                &env,
                name,
                value
            );

            free(name);

            continue;
        }

        /* print expression; */

        if (parser->current.type == TOKEN_PRINT) {

            parser_advance(parser);

            Expr *expr =
                parse_expression(parser);

            expect(parser, TOKEN_SEMICOLON);

            long value =
                evaluate(expr, &env);

            printf("%ld\n", value);

            continue;
        }

        parser_error(
            parser,
            "expected 'let' or 'print'"
        );
    }
}


/* ============================================================
 * MAIN
 * ============================================================ */

int main(void)
{
    const char *program =
        "let x = 10;"
        "let y = 20;"
        "let z = x + y * 2;"
        "print x;"
        "print y;"
        "print z;"
        "print (z + 5) * 2;";

    Parser parser;

    parser_init(&parser, program);

    parse_program(&parser);

    free(parser.current.text);

    return 0;
}
```

---

# 5. Compile It

On Linux/macOS:

```bash
cc -std=c11 -Wall -Wextra -O2 minilang.c -o minilang
```

Then:

```bash
./minilang
```

You should get:

```text
10
20
50
110
```

The program:

```text
let z = x + y * 2;
```

correctly evaluates to:

```text
10 + 20 * 2
```

which is:

```text
50
```

because multiplication has higher precedence than addition.

---

# 6. What We Just Built

Although the program is small, it already contains the fundamental components of a real language.

```text
                 MiniLang
                    │
        ┌───────────┴───────────┐
        │                       │
      Lexer                   Parser
        │                       │
        ▼                       ▼
     Tokens                    AST
                                │
                                ▼
                           Interpreter
                                │
                                ▼
                              Result
```

Let's examine each piece.

---

# 7. Lexer

The lexer converts characters:

```text
let x = 10 + 20;
```

into tokens:

```text
LET
IDENTIFIER("x")
EQUAL
NUMBER(10)
PLUS
NUMBER(20)
SEMICOLON
```

The lexer doesn't care what the program *means*.

It only recognizes pieces.

This:

```text
10 + 20
```

becomes:

```text
NUMBER(10)
PLUS
NUMBER(20)
```

---

# 8. Parser

The parser determines structure.

For:

```text
10 + 20 * 3
```

the parser creates:

```text
       +
      / \
    10   *
        / \
       20  3
```

rather than:

```text
       *
      / \
     +   3
    / \
   10 20
```

This is how operator precedence is implemented.

---

# 9. Our Grammar

The parser is implementing approximately:

```text
expression
    = addition ;

addition
    = multiplication
      { ("+" | "-") multiplication } ;

multiplication
    = primary
      { ("*" | "/") primary } ;

primary
    = NUMBER
    | IDENTIFIER
    | "(" expression ")" ;
```

This is essentially a tiny context-free grammar.

---

# 10. Why the Parser Is Written This Way

Notice:

```c
static Expr *parse_multiplication(Parser *parser)
```

calls:

```c
parse_primary()
```

while:

```c
parse_expression()
```

calls:

```c
parse_multiplication()
```

That gives us:

```text
expression
    ↓
addition
    ↓
multiplication
    ↓
primary
```

So:

```text
1 + 2 * 3
```

naturally becomes:

```text
        +
       / \
      1   *
         / \
        2   3
```

This technique is called **recursive descent parsing**.

It is one of the easiest parser techniques to implement manually in C.

---

# 11. AST

The AST represents the meaning of the source code structurally.

For:

```text
x + 10 * 2
```

we have:

```text
             Binary(+)
              /      \
          Variable    Binary(*)
             x        /       \
                     10        2
```

Our C representation is:

```c
struct Expr {
    ExprType type;

    union {
        long number;

        char *variable;

        struct {
            BinaryOp op;
            Expr *left;
            Expr *right;
        } binary;
    };
};
```

This is a classic tagged-union representation of an AST.

---

# 12. Interpreter

Once the AST exists, interpretation is surprisingly simple.

For:

```text
10 + 20
```

the interpreter does:

```text
evaluate(+)
    │
    ├── evaluate(10)
    │      └── 10
    │
    └── evaluate(20)
           └── 20

10 + 20
   ↓
30
```

That's why:

```c
long evaluate(Expr *expr, Environment *env)
```

is essentially a recursive tree traversal.

---

# 13. Variables

We also introduced an **environment**:

```text
Environment
    │
    ├── x → 10
    ├── y → 20
    └── z → 50
```

When evaluating:

```text
x + y
```

the interpreter performs:

```text
lookup("x")
    ↓
10

lookup("y")
    ↓
20

10 + 20
    ↓
30
```

Real languages use considerably more sophisticated structures:

```text
hash tables
symbol tables
scope chains
closures
modules
```

but the principle is the same.

---

# 14. How a Real Language Grows

You can now expand MiniLang incrementally.

I'd recommend this order:

```text
                    MiniLang
                       │
        ┌──────────────┴──────────────┐
        │                             │
      Current                       Next
        │                             │
        ▼                             ▼
 expressions                     booleans
 variables                       comparisons
 print                           if
                                 while
                                 functions
                                 scopes
                                 arrays
                                 strings
```

For example, add:

```text
if x > 10 {
    print x;
}
```

Then:

```text
while x < 100 {
    print x;
    x = x + 1;
}
```

Then functions:

```text
fn add(a, b) {
    return a + b;
}

print add(10, 20);
```

At that point you have something that starts looking like a real language.

---

# 15. The Next Major Step: Separate Statements From Expressions

Our current implementation handles statements directly inside:

```c
parse_program()
```

A proper language should introduce an AST for statements too.

For example:

```text
AST
│
├── Expression
│   ├── Number
│   ├── Variable
│   └── Binary
│
└── Statement
    ├── Let
    ├── Assignment
    ├── Print
    ├── If
    ├── While
    ├── Return
    └── Block
```

Then:

```text
let x = 10;
```

becomes:

```text
LetStatement
    │
    ├── name = x
    │
    └── value
          │
          └── Number(10)
```

This architecture scales much better.

---

# 16. Then Add Scopes

Consider:

```text
let x = 10;

{
    let x = 20;
    print x;
}

print x;
```

The output should be:

```text
20
10
```

You need nested environments:

```text
Global Environment
       │
       ├── x = 10
       │
       ▼
Local Environment
       │
       └── x = 20
```

Lookup becomes:

```text
look in current scope
        │
        ├── found → return
        │
        └── not found
              │
              ▼
         parent scope
```

This is the foundation for lexical scoping.

---

# 17. Then Add Functions

Eventually:

```text
fn square(x) {
    return x * x;
}

print square(5);
```

requires:

```text
Function declaration
       │
       ▼
Function object
       │
       ├── parameters
       ├── body
       └── closure/environment
```

Calling it creates a new scope:

```text
global
  │
  │ square
  ▼
function call
  │
  └── x = 5
       │
       ▼
     x * x
       │
       ▼
      25
```

At this point you're implementing many of the concepts found in languages like Python, JavaScript, Ruby, etc.

---

# 18. Interpreter → Compiler

Once your interpreter works, you have another interesting option.

Instead of:

```text
AST
 ↓
evaluate
```

you can generate bytecode:

```text
AST
 ↓
bytecode
 ↓
VM
```

For:

```text
print 10 + 20 * 3;
```

you might generate:

```text
PUSH 10
PUSH 20
PUSH 3
MUL
ADD
PRINT
HALT
```

Then build a virtual machine:

```text
             bytecode
                │
                ▼
        ┌────────────────┐
        │ Virtual Machine│
        │                │
        │ stack          │
        │ instruction    │
        │ pointer        │
        └────────────────┘
```

This is a fantastic next step because you learn how languages such as Lua and many JVM/.NET-style systems work conceptually.

---

# 19. Compiler to Native Code

Eventually you can go even further:

```text
MiniLang
   │
   ▼
Lexer
   │
   ▼
Parser
   │
   ▼
AST
   │
   ▼
Semantic analysis
   │
   ▼
IR
   │
   ▼
Machine code
   │
   ▼
Executable
```

For example:

```text
let x = 10;
print x;
```

could eventually become native machine code.

You can either write your own backend or generate code for an existing compiler infrastructure such as LLVM.

---

# 20. A Good Architecture for a Serious C Compiler

If you want to turn this experiment into a real language, I'd eventually organize the project like this:

```text
mylang/
│
├── src/
│   ├── main.c
│   │
│   ├── lexer.c
│   ├── lexer.h
│   │
│   ├── parser.c
│   ├── parser.h
│   │
│   ├── ast.c
│   ├── ast.h
│   │
│   ├── semantic.c
│   ├── semantic.h
│   │
│   ├── interpreter.c
│   ├── interpreter.h
│   │
│   ├── value.c
│   ├── value.h
│   │
│   └── error.c
│       error.h
│
├── tests/
│   ├── lexer/
│   ├── parser/
│   ├── interpreter/
│   └── programs/
│
├── examples/
│   ├── hello.ml
│   ├── fibonacci.ml
│   └── factorial.ml
│
└── Makefile
```

Then your compiler becomes a real project rather than one large C file.

---

# 21. The Full Learning Path

If your goal is to **actually understand language implementation**, I'd follow this progression:

```text
                    Programming Language
                            │
                            ▼
                       1. Lexer
                            │
                            ▼
                       2. Parser
                            │
                            ▼
                          3. AST
                            │
                            ▼
                    4. Interpreter
                            │
                            ▼
                     5. Variables
                            │
                            ▼
                      6. Scopes
                            │
                            ▼
                      7. Functions
                            │
                            ▼
                    8. Type system
                            │
                            ▼
                  9. Semantic analysis
                            │
                            ▼
                    10. Bytecode VM
                            │
                            ▼
                    11. Garbage collector
                            │
                            ▼
                       12. Modules
                            │
                            ▼
                    13. Optimizations
                            │
                            ▼
                       14. Compiler
                            │
                            ▼
                    15. Native machine code
```

The important thing is **not to jump directly to machine code**. Build the language in layers.

The tiny MiniLang above already gives you the essential skeleton:

```text
source
  ↓
lexer
  ↓
tokens
  ↓
recursive-descent parser
  ↓
AST
  ↓
environment
  ↓
interpreter
```

From there, the most educational next step is to turn this into a **proper multi-file C compiler/interpreter**, adding `if`, `while`, assignments, booleans, strings, functions, lexical scopes, and a real AST—then replace the interpreter with a **bytecode virtual machine**.
