---

title: "Django and Django REST Framework Cheat Sheet"
category: "Web Development"
subcategory: "Python / Django / REST APIs"
tags:

* Django
* Django REST Framework
* DRF
* Python
* REST
* ORM
* API
* serializers
* views
* authentication
  type: "reference"

---

# Django and Django REST Framework Cheat Sheet

## 1. Mental Model

Django is a **full-featured Python web framework**.

Django REST Framework (DRF) builds on Django to provide tools for creating **REST APIs**.

The basic architecture is:

```text
HTTP Request
     │
     ▼
   URLconf
     │
     ▼
    View
     │
     ├──────► Serializer
     │           │
     │           ▼
     │      Validation
     │
     ▼
   Model
     │
     ▼
  Database
     │
     ▼
   Model
     │
     ▼
 Serializer
     │
     ▼
HTTP Response
```

A useful distinction:

```text
Django
├── HTTP
├── URLs
├── Views
├── Templates
├── Forms
├── ORM
├── Authentication
├── Admin
└── Middleware

Django REST Framework
├── Serializers
├── APIViews
├── Generic Views
├── ViewSets
├── Routers
├── Authentication
├── Permissions
├── Throttling
└── Content negotiation
```

---

# 2. Create a Django Project

Install:

```bash
pip install django djangorestframework
```

Create project:

```bash
django-admin startproject config .
```

Typical structure:

```text
project/
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── app/
```

Create an app:

```bash
python manage.py startapp users
```

---

# 3. Django Project vs App

A **project** is the overall Django application.

An **app** contains a particular domain/functionality.

For example:

```text
project
│
├── users
├── products
├── orders
└── payments
```

Each app can contain:

```text
users/
├── models.py
├── views.py
├── urls.py
├── admin.py
├── apps.py
├── tests.py
└── migrations/
```

---

# 4. `settings.py`

Important settings:

```python
INSTALLED_APPS = [
    ...
    "rest_framework",
    "users",
]
```

Database:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "mydb",
        "USER": "postgres",
        "PASSWORD": "...",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

Debug:

```python
DEBUG = True
```

Allowed hosts:

```python
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]
```

---

# 5. Development Server

```bash
python manage.py runserver
```

Specific port:

```bash
python manage.py runserver 8080
```

---

# 6. Django Models

A model represents persistent data.

```python
from django.db import models


class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
```

Django translates this into a database table.

Conceptually:

```text
User
─────────────────────
id
name
email
age
created_at
```

Django automatically adds an `id` primary key unless you define another primary key.

---

# 7. Common Model Fields

```python
models.AutoField()
models.BigAutoField()

models.CharField(max_length=255)
models.TextField()

models.IntegerField()
models.BigIntegerField()
models.PositiveIntegerField()

models.FloatField()
models.DecimalField()

models.BooleanField()

models.DateField()
models.DateTimeField()
models.TimeField()

models.UUIDField()

models.JSONField()

models.BinaryField()
```

File:

```python
models.FileField()
models.ImageField()
```

---

# 8. Field Options

```python
name = models.CharField(
    max_length=100,
    null=False,
    blank=False,
    default="",
    unique=True,
    db_index=True,
)
```

Important distinction:

```text
null
    → database-level NULL

blank
    → validation/forms
```

Usually:

```python
null=True
```

is not needed for string fields; an empty string is commonly used instead.

---

# 9. Primary Keys

Default:

```python
id = models.BigAutoField(primary_key=True)
```

UUID:

```python
import uuid

id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False,
)
```

---

# 10. Relationships

### ForeignKey

```python
class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
```

Conceptually:

```text
User
  │
  ├── Order
  ├── Order
  └── Order
```

### One-to-one

```python
profile = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
)
```

### Many-to-many

```python
class Article(models.Model):
    tags = models.ManyToManyField(Tag)
```

---

# 11. `on_delete`

Common options:

```python
models.CASCADE
models.PROTECT
models.RESTRICT
models.SET_NULL
models.SET_DEFAULT
models.SET(...)
models.DO_NOTHING
```

Example:

```python
user = models.ForeignKey(
    User,
    on_delete=models.PROTECT,
)
```

This prevents deleting the user while dependent records exist.

---

# 12. Migrations

After changing models:

```bash
python manage.py makemigrations
```

Apply:

```bash
python manage.py migrate
```

Show migrations:

```bash
python manage.py showmigrations
```

SQL generated by a migration:

```bash
python manage.py sqlmigrate app 0001
```

Mental model:

```text
models.py
    │
    ▼
makemigrations
    │
    ▼
migration files
    │
    ▼
migrate
    │
    ▼
database schema
```

---

# 13. Django ORM

Create:

```python
user = User.objects.create(
    name="Alice",
    email="alice@example.com",
    age=30,
)
```

Get all:

```python
users = User.objects.all()
```

Filter:

```python
users = User.objects.filter(age__gte=18)
```

Get one:

```python
user = User.objects.get(pk=1)
```

First:

```python
user = User.objects.first()
```

Last:

```python
user = User.objects.last()
```

Exists:

```python
User.objects.filter(email=email).exists()
```

Count:

```python
User.objects.count()
```

---

# 14. Query Lookups

```python
User.objects.filter(age__gt=18)
User.objects.filter(age__gte=18)

User.objects.filter(age__lt=18)
User.objects.filter(age__lte=18)

User.objects.filter(name__exact="Alice")
User.objects.filter(name__iexact="alice")

User.objects.filter(name__contains="Ali")
User.objects.filter(name__icontains="ali")

User.objects.filter(name__startswith="A")
User.objects.filter(name__endswith="e")

User.objects.filter(created_at__year=2026)
```

Relationship:

```python
Order.objects.filter(user__email__icontains="@gmail.com")
```

---

# 15. Exclude

```python
User.objects.exclude(age__lt=18)
```

Equivalent conceptually to:

```sql
WHERE NOT age < 18
```

---

# 16. Ordering

```python
User.objects.order_by("name")
```

Descending:

```python
User.objects.order_by("-created_at")
```

Multiple:

```python
User.objects.order_by("-created_at", "name")
```

---

# 17. Slicing / Pagination at ORM Level

```python
users = User.objects.all()[0:20]
```

This becomes a SQL `LIMIT`/`OFFSET` style query.

---

# 18. `Q` Objects

Useful for complex OR conditions:

```python
from django.db.models import Q

users = User.objects.filter(
    Q(name__icontains="alice") |
    Q(email__icontains="alice")
)
```

AND:

```python
users = User.objects.filter(
    Q(age__gte=18) &
    Q(age__lte=30)
)
```

NOT:

```python
users = User.objects.filter(
    ~Q(name="Alice")
)
```

---

# 19. `F` Expressions

Reference another database field:

```python
from django.db.models import F

Product.objects.filter(
    stock__gt=F("reserved")
)
```

Update without pulling rows into Python:

```python
Product.objects.update(
    stock=F("stock") - 1
)
```

This is important for avoiding race-prone read/modify/write operations.

---

# 20. Aggregation

```python
from django.db.models import Count, Avg, Sum, Max, Min
```

Count:

```python
User.objects.aggregate(
    Count("id")
)
```

Average:

```python
Product.objects.aggregate(
    Avg("price")
)
```

Group-like query:

```python
User.objects.values("country").annotate(
    count=Count("id")
)
```

---

# 21. `select_related`

For foreign key / one-to-one relationships:

```python
orders = Order.objects.select_related("user")
```

Instead of:

```text
query orders
    ↓
query user
    ↓
query user
    ↓
query user
```

you can retrieve related objects efficiently with SQL joins.

---

# 22. `prefetch_related`

For many-to-many and reverse relationships:

```python
users = User.objects.prefetch_related("orders")
```

Mental model:

```text
select_related
    → SQL JOIN
    → FK / OneToOne

prefetch_related
    → separate queries + Python joining
    → ManyToMany / reverse relations
```

This is critical for avoiding the **N+1 query problem**.

---

# 23. Transactions

```python
from django.db import transaction

with transaction.atomic():
    user = create_user()
    create_order(user)
```

If an exception occurs, the transaction is rolled back.

Decorator:

```python
@transaction.atomic
def create_order():
    ...
```

---

# 24. Django Admin

Register:

```python
from django.contrib import admin
from .models import User

admin.site.register(User)
```

Create admin user:

```bash
python manage.py createsuperuser
```

Access:

```text
/admin/
```

Customize:

```python
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "email"]
    search_fields = ["name", "email"]
    list_filter = ["created_at"]
```

---

# 25. Django URLs

`urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path("users/", views.users),
]
```

Dynamic parameter:

```python
path("users/<int:id>/", views.user_detail)
```

Include app URLs:

```python
path("api/", include("users.urls"))
```

---

# 26. Django Function-Based View

```python
from django.http import JsonResponse


def hello(request):
    return JsonResponse({
        "message": "Hello"
    })
```

---

# 27. Django Class-Based View

```python
from django.views import View
from django.http import JsonResponse


class UserView(View):

    def get(self, request):
        return JsonResponse({
            "message": "GET"
        })

    def post(self, request):
        return JsonResponse({
            "message": "POST"
        })
```

---

# 28. DRF Installation

```bash
pip install djangorestframework
```

Add:

```python
INSTALLED_APPS = [
    ...
    "rest_framework",
]
```

---

# 29. DRF Serializer

A serializer converts between:

```text
Python / Django objects
        ↕
JSON / primitive data
```

Example:

```python
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "age",
        ]
```

---

# 30. Serializer Validation

Field validation:

```python
class UserSerializer(serializers.ModelSerializer):

    def validate_age(self, value):
        if value < 18:
            raise serializers.ValidationError(
                "User must be an adult."
            )

        return value
```

Object-level:

```python
def validate(self, attrs):
    if attrs["password"] != attrs["password_confirmation"]:
        raise serializers.ValidationError(
            "Passwords do not match."
        )

    return attrs
```

---

# 31. Serializer Fields

```python
serializers.CharField()
serializers.IntegerField()
serializers.BooleanField()
serializers.FloatField()
serializers.DecimalField()
serializers.DateTimeField()
serializers.EmailField()
serializers.UUIDField()
serializers.URLField()
serializers.JSONField()
```

Optional:

```python
email = serializers.EmailField(
    required=False
)
```

Read-only:

```python
id = serializers.IntegerField(
    read_only=True
)
```

Write-only:

```python
password = serializers.CharField(
    write_only=True
)
```

---

# 32. Nested Serializers

```python
class UserSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "orders",
        ]
```

Result:

```json
{
  "id": 1,
  "name": "Alice",
  "orders": [
    {
      "id": 10
    },
    {
      "id": 11
    }
  ]
}
```

---

# 33. Serializer `create()`

```python
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["name", "email"]

    def create(self, validated_data):
        return User.objects.create(
            **validated_data
        )
```

For `ModelSerializer`, the default implementation already handles ordinary model creation, so override it only when custom behavior is needed.

---

# 34. Serializer `update()`

```python
def update(self, instance, validated_data):
    instance.name = validated_data.get(
        "name",
        instance.name,
    )

    instance.save()

    return instance
```

Again, only override when custom behavior is required.

---

# 35. APIView

Basic DRF API:

```python
from rest_framework.views import APIView
from rest_framework.response import Response


class UserView(APIView):

    def get(self, request):
        users = User.objects.all()

        serializer = UserSerializer(
            users,
            many=True,
        )

        return Response(serializer.data)
```

---

# 36. APIView POST

```python
def post(self, request):
    serializer = UserSerializer(
        data=request.data
    )

    serializer.is_valid(raise_exception=True)

    user = serializer.save()

    return Response(
        UserSerializer(user).data,
        status=201,
    )
```

The flow is:

```text
request.data
     ↓
Serializer(data=...)
     ↓
is_valid()
     ↓
validated_data
     ↓
save()
     ↓
response
```

---

# 37. Generic API Views

DRF provides reusable generic views.

```python
from rest_framework.generics import (
    ListCreateAPIView,
)

class UserListCreateView(
    ListCreateAPIView
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

This provides:

```text
GET  /users/
POST /users/
```

---

# 38. Common Generic Views

```text
ListAPIView
CreateAPIView
RetrieveAPIView
UpdateAPIView
DestroyAPIView

ListCreateAPIView
RetrieveUpdateAPIView
RetrieveDestroyAPIView
RetrieveUpdateDestroyAPIView
```

These are useful when your API follows conventional CRUD behavior.

---

# 39. ViewSets

Instead of writing separate views:

```python
from rest_framework.viewsets import ModelViewSet


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

This gives standard actions:

```text
list
retrieve
create
update
partial_update
destroy
```

---

# 40. Routers

```python
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(
    "users",
    UserViewSet,
)

urlpatterns = router.urls
```

The router generates routes such as:

```text
GET     /users/
POST    /users/

GET     /users/{id}/
PUT     /users/{id}/
PATCH   /users/{id}/
DELETE  /users/{id}/
```

---

# 41. ViewSet Mental Model

A `ModelViewSet` roughly maps:

```text
HTTP       action
────────────────────────
GET /users/       list
POST /users/      create

GET /users/1/     retrieve
PUT /users/1/     update
PATCH /users/1/   partial_update
DELETE /users/1/  destroy
```

This is why ViewSets + Routers are so convenient for conventional CRUD APIs.

---

# 42. Custom ViewSet Actions

```python
from rest_framework.decorators import action


class UserViewSet(ModelViewSet):

    @action(
        detail=True,
        methods=["post"],
    )
    def activate(self, request, pk=None):
        user = self.get_object()
        user.active = True
        user.save()

        return Response({
            "status": "activated"
        })
```

Route:

```text
POST /users/{id}/activate/
```

---

# 43. Request Object

DRF:

```python
request.data
```

Query parameters:

```python
request.query_params
```

Headers:

```python
request.headers
```

Authenticated user:

```python
request.user
```

Uploaded files:

```python
request.FILES
```

Example:

```text
GET /users/?page=2&active=true

request.query_params["page"]
request.query_params["active"]
```

---

# 44. Response

```python
return Response({
    "message": "hello"
})
```

Status:

```python
return Response(
    {"created": True},
    status=201,
)
```

Common statuses:

```text
200 OK
201 Created
202 Accepted
204 No Content

400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Unprocessable Entity

500 Internal Server Error
```

---

# 45. HTTP Methods

Typical REST mapping:

```text
GET
    retrieve resources

POST
    create resource

PUT
    replace resource

PATCH
    partially update resource

DELETE
    delete resource
```

Example:

```text
GET    /users/
POST   /users/

GET    /users/42/
PUT    /users/42/
PATCH  /users/42/
DELETE /users/42/
```

---

# 46. DRF Permissions

Global:

```python
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
```

Per-view:

```python
from rest_framework.permissions import IsAuthenticated


class UserViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated
    ]
```

Common permissions:

```python
AllowAny
IsAuthenticated
IsAdminUser
IsAuthenticatedOrReadOnly
```

---

# 47. Authentication

DRF supports authentication mechanisms such as:

```text
SessionAuthentication
BasicAuthentication
TokenAuthentication
```

Third-party packages are commonly used for JWT authentication.

Important distinction:

```text
Authentication
    → Who are you?

Authorization / Permission
    → Are you allowed to do this?
```

---

# 48. Object-Level Permissions

Example:

```python
class IsOwner(BasePermission):

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        return obj.owner == request.user
```

Use:

```python
permission_classes = [IsOwner]
```

This is important for APIs where users may access only their own resources.

---

# 49. Filtering

Install:

```bash
pip install django-filter
```

Settings:

```python
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
}
```

ViewSet:

```python
filterset_fields = [
    "active",
    "country",
]
```

Query:

```text
GET /users/?active=true&country=AR
```

---

# 50. Search

```python
from rest_framework.filters import SearchFilter


class UserViewSet(ModelViewSet):
    filter_backends = [SearchFilter]
    search_fields = [
        "name",
        "email",
    ]
```

Query:

```text
/users/?search=alice
```

---

# 51. Ordering

```python
from rest_framework.filters import OrderingFilter


class UserViewSet(ModelViewSet):
    filter_backends = [
        OrderingFilter
    ]

    ordering_fields = [
        "name",
        "created_at",
    ]

    ordering = ["-created_at"]
```

Query:

```text
/users/?ordering=name
/users/?ordering=-created_at
```

---

# 52. Pagination

Example:

```python
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS":
        "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}
```

Request:

```text
GET /users/?page=2
```

Typical response:

```json
{
  "count": 100,
  "next": "...",
  "previous": "...",
  "results": [
    {}
  ]
}
```

---

# 53. Custom Pagination

```python
from rest_framework.pagination import PageNumberPagination


class StandardPagination(
    PageNumberPagination
):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
```

Then:

```python
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS":
        "myapp.pagination.StandardPagination",
}
```

---

# 54. Throttling

Global:

```python
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],

    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
    },
}
```

Useful for controlling API abuse and resource consumption.

---

# 55. Content Negotiation

DRF can select an appropriate representation based on the request.

Common formats:

```text
JSON
Browsable API
```

Response:

```python
return Response(data)
```

DRF determines the appropriate renderer.

---

# 56. HTTP 404

Django:

```python
from django.shortcuts import get_object_or_404

user = get_object_or_404(
    User,
    pk=pk,
)
```

DRF:

```python
user = self.get_object()
```

Generic views and ViewSets automatically provide common 404 behavior.

---

# 57. Authentication + Permissions + Serialization

A typical protected API request:

```text
HTTP Request
     │
     ▼
Authentication
     │
     ▼
Permissions
     │
     ▼
View/ViewSet
     │
     ▼
Serializer
     │
     ▼
ORM
     │
     ▼
Database
```

This separation is extremely important.

---

# 58. Typical DRF CRUD Application

### Model

```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
```

### Serializer

```python
class ProductSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
        ]
```

### ViewSet

```python
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

### Router

```python
router.register(
    "products",
    ProductViewSet,
)
```

You now have a complete CRUD API.

---

# 59. Better ViewSet

Real applications usually add:

```python
class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer

    queryset = Product.objects.all()

    permission_classes = [
        IsAuthenticated
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "category",
    ]

    search_fields = [
        "name",
    ]

    ordering_fields = [
        "name",
        "price",
        "created_at",
    ]

    ordering = [
        "name"
    ]
```

This gives you:

```text
CRUD
+
authentication
+
permissions
+
filtering
+
search
+
ordering
```

---

# 60. Avoiding N+1 Queries

Bad:

```python
users = User.objects.all()

for user in users:
    print(user.orders.all())
```

Potentially:

```text
1 query → users
N queries → orders
```

Better:

```python
users = User.objects.prefetch_related(
    "orders"
)
```

For foreign keys:

```python
orders = Order.objects.select_related(
    "user"
)
```

A major Django performance rule:

> Always think about how many SQL queries your ORM code generates.

---

# 61. `SerializerMethodField`

Useful for computed output:

```python
class UserSerializer(
    serializers.ModelSerializer
):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
```

Output:

```json
{
  "first_name": "Alice",
  "last_name": "Smith",
  "full_name": "Alice Smith"
}
```

Don't use expensive database queries inside `SerializerMethodField` without considering N+1 problems.

---

# 62. `ModelSerializer` vs `Serializer`

### `ModelSerializer`

Use when directly representing a model:

```python
class UserSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = User
        fields = "__all__"
```

### `Serializer`

Use when the API representation doesn't map directly to a model:

```python
class LoginSerializer(
    serializers.Serializer
):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True
    )
```

Rule:

```text
Model data → ModelSerializer

Custom API data → Serializer
```

---

# 63. DTO-Like API Serializers

You don't have to expose your database model directly.

For example:

```python
class UserResponseSerializer(
    serializers.Serializer
):
    id = serializers.IntegerField()
    display_name = serializers.CharField()
    order_count = serializers.IntegerField()
```

This lets your API contract remain independent of the database schema.

---

# 64. Service Layer

For complex business logic, avoid turning ViewSets into huge functions.

Instead:

```text
ViewSet
   ↓
Serializer
   ↓
Service
   ↓
Domain/business logic
   ↓
ORM
```

Example:

```python
class OrderService:

    @staticmethod
    def create_order(user, items):
        ...
```

Then:

```python
order = OrderService.create_order(
    request.user,
    validated_data["items"],
)
```

Django does not force a service-layer architecture; introduce it when domain complexity justifies it.

---

# 65. Signals

Example:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def user_created(
    sender,
    instance,
    created,
    **kwargs,
):
    if created:
        ...
```

Signals can be useful, but avoid hiding important business logic inside them.

A useful rule:

> If an operation is part of an important business workflow, explicit service/application code is often easier to understand than a signal.

---

# 66. Middleware

Middleware sits around request processing:

```text
Request
   ↓
Middleware
   ↓
Middleware
   ↓
View
   ↓
Middleware
   ↓
Middleware
   ↓
Response
```

Examples include:

* authentication/session handling
* security
* logging
* request IDs
* custom headers

Custom middleware:

```python
class MyMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # before view

        response = self.get_response(request)

        # after view

        return response
```

---

# 67. Async Django

Modern Django supports asynchronous views.

```python
async def view(request):
    ...
```

Async can be useful for I/O-heavy workloads.

However:

```text
async ≠ automatically faster
```

For CPU-heavy work, asynchronous code doesn't magically create more CPU capacity.

---

# 68. Django ASGI / WSGI

Traditional:

```text
Django
  ↓
WSGI
  ↓
Gunicorn/uWSGI/etc.
```

Async-capable deployment:

```text
Django
  ↓
ASGI
  ↓
Uvicorn/Daphne/etc.
```

ASGI enables Django applications to participate in asynchronous server/application patterns.

---

# 69. Production Architecture

A common deployment:

```text
             Internet
                │
                ▼
          Reverse Proxy
          (Nginx/etc.)
                │
        ┌───────┴────────┐
        ▼                ▼
     Django           Static
      app              files
        │
   ┌────┴─────┐
   ▼          ▼
PostgreSQL   Redis
   │
   │
   └──────────────┐
                  ▼
              Celery
               workers
```

Typical components:

```text
Django
DRF
PostgreSQL
Redis
Celery
Nginx
Gunicorn / Uvicorn
```

Not every project needs all of them.

---

# 70. Background Tasks

Don't perform long-running jobs directly inside an HTTP request.

Bad:

```text
POST /video/
      │
      ├── upload
      ├── process video
      ├── generate thumbnails
      └── respond
```

Better:

```text
POST /video/
      │
      ▼
create job
      │
      ▼
return 202
      │
      ▼
background worker
      │
      ├── process video
      └── generate thumbnails
```

Celery is a common choice for this architecture.

---

# 71. Security Essentials

Important Django protections include:

```text
CSRF
SQL injection protection
XSS protections
clickjacking protection
secure password hashing
security middleware
```

Never:

```python
password = models.CharField(...)
```

and store plaintext passwords.

Use Django's authentication/password hashing system.

Never manually construct SQL from untrusted input:

```python
# BAD
sql = f"SELECT * FROM users WHERE name = '{name}'"
```

Prefer ORM queries or parameterized SQL.

---

# 72. Environment Configuration

Don't hard-code secrets:

```python
SECRET_KEY = "..."
DATABASE_PASSWORD = "..."
```

Use environment/configuration management instead.

Typical pattern:

```python
import os

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
```

For production:

```text
DEBUG = False
```

and configure:

```text
ALLOWED_HOSTS
database
secret key
TLS/HTTPS
secure cookies
CSRF trusted origins
static/media storage
logging
```

---

# 73. Django Management Commands

Create:

```text
app/
└── management/
    └── commands/
        └── cleanup.py
```

Then:

```python
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Cleaning...")
```

Run:

```bash
python manage.py cleanup
```

Very useful for:

* maintenance
* imports
* migrations/data transformations
* batch processing
* administration

---

# 74. Django Shell

```bash
python manage.py shell
```

Then:

```python
from users.models import User

User.objects.all()
```

Useful for debugging and inspecting the ORM.

---

# 75. Useful Debugging Tools

Django shell:

```bash
python manage.py shell
```

Check configuration:

```bash
python manage.py check
```

Database migrations:

```bash
python manage.py showmigrations
```

Tests:

```bash
python manage.py test
```

For SQL performance, inspect generated queries and use database query-analysis tools.

---

# 76. Recommended DRF Architecture

For a medium/large API:

```text
project/
├── config/
│   ├── settings/
│   ├── urls.py
│   └── asgi.py
│
├── users/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   ├── filters.py
│   └── tests/
│
├── orders/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── services.py
│   └── tests/
│
└── manage.py
```

For very large systems, you can split domains into separate Django apps rather than organizing everything around technical layers.

---

# 77. Django vs DRF

| Feature             | Django        | DRF                     |
| ------------------- | ------------- | ----------------------- |
| ORM                 | ✅             | Uses Django             |
| Models              | ✅             | Uses Django             |
| HTML templates      | ✅             | Not its primary purpose |
| Forms               | ✅             | Has serializers instead |
| Admin               | ✅             | Uses Django             |
| URLs                | ✅             | Uses Django             |
| Middleware          | ✅             | Uses Django             |
| REST APIs           | Basic support | ✅                       |
| Serializers         | ❌             | ✅                       |
| ViewSets            | ❌             | ✅                       |
| Routers             | ❌             | ✅                       |
| API authentication  | Django auth   | DRF authentication      |
| API permissions     | Limited/basic | ✅                       |
| API pagination      | ❌             | ✅                       |
| API throttling      | ❌             | ✅                       |
| Content negotiation | Limited       | ✅                       |

---

# 78. The Most Important DRF Concepts

If learning DRF, prioritize these:

```text
1. Models
       ↓
2. QuerySets / ORM
       ↓
3. Serializers
       ↓
4. APIView
       ↓
5. Generic Views
       ↓
6. ViewSets
       ↓
7. Routers
       ↓
8. Authentication
       ↓
9. Permissions
       ↓
10. Filtering / Ordering
       ↓
11. Pagination
       ↓
12. Transactions
       ↓
13. Performance / N+1
       ↓
14. Testing
```

---

# 79. The DRF Request Lifecycle

For a typical API request:

```text
                    HTTP Request
                         │
                         ▼
                     URL Router
                         │
                         ▼
                    Middleware
                         │
                         ▼
                   Authentication
                         │
                         ▼
                    Permissions
                         │
                         ▼
                    ViewSet/View
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
          QuerySet              Serializer
              │                     │
              ▼                     ▼
          Database              Validation
              │                     │
              └──────────┬──────────┘
                         ▼
                     Response
                         │
                         ▼
                     Renderer
                         │
                         ▼
                    HTTP Response
```

---

# 80. One Complete DRF Example

### Model

```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    active = models.BooleanField(default=True)
```

### Serializer

```python
class ProductSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "active",
        ]
```

### ViewSet

```python
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

### Router

```python
router = DefaultRouter()

router.register(
    "products",
    ProductViewSet,
)
```

### API

```text
GET    /products/
POST   /products/

GET    /products/42/
PUT    /products/42/
PATCH  /products/42/
DELETE /products/42/
```

This is the core pattern to understand:

```text
             Model
               │
               ▼
          ModelSerializer
               │
               ▼
           ViewSet
               │
               ▼
            Router
               │
               ▼
              API
```

---

# 81. Django/DRF Performance Checklist

When an API becomes slow, check:

```text
□ N+1 queries
□ select_related()
□ prefetch_related()
□ missing database indexes
□ unnecessary serializer work
□ expensive SerializerMethodField
□ unnecessary model instances
□ queryset evaluation
□ pagination
□ large JSON responses
□ database connection configuration
□ caching
□ external API calls
□ synchronous long-running operations
```

And measure rather than guessing.

---

# 82. Core Mental Model

The entire Django + DRF stack can be reduced to:

```text
                 CLIENT
                    │
                    ▼
                 HTTP
                    │
                    ▼
                Django
                    │
             URL routing
                    │
                    ▼
              DRF ViewSet
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
     Permissions         Serializer
                              │
                         validation
                              │
                              ▼
                            Model
                              │
                              ▼
                            ORM
                              │
                              ▼
                          Database
```

The **five concepts worth mastering first** are:

> **Models → QuerySets → Serializers → ViewSets → Permissions**

Once those are solid, most conventional Django REST APIs become variations of the same underlying architecture.

