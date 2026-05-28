---
layout: post
title: "Python FastAPI Apps with Declarative Dependencies"
date: 2026-05-28
type: how-to
summary: "Build FastAPI apps with clean, declarative dependency injection using Claude Code."
image: "/claude-daily-tips/assets/images/2026-05-28-python-fastapi-apps-with-declarative-dependencies.jpg"
tags:
  - claude-code
  - productivity
  - cli
  - devtools
---



![Python FastAPI Apps with Declarative Dependencies](/claude-daily-tips/assets/images/2026-05-28-python-fastapi-apps-with-declarative-dependencies.jpg)



Manually managing dependencies in Python, like passing database connections or service instances through constructors and function arguments, quickly leads to brittle, tightly coupled code that’s a pain to test and maintain as projects scale. This boilerplate can obscure your application's core logic and slow down development. FastAPI's built-in dependency injection system, however, offers a more elegant, Pythonic solution that significantly streamlines this process, and tools like Claude Code can help you leverage it effectively.

FastAPI’s dependency injection works by defining functions that act as dependency providers. When a route handler or another dependency needs an object, FastAPI automatically calls these provider functions, injects their return values, and caches them for subsequent requests within the same scope. This declarative approach abstracts away the instantiation and management of objects, promoting modularity and making your code inherently more testable by allowing you to easily substitute real dependencies with mocks during testing.

Consider building a simple user API. Instead of scattering database connection logic throughout your codebase, you can define a `get_user_repository` provider function. This function, when called by FastAPI, instantiates and returns your `UserRepository`. A `UserService` can then declare its dependency on `UserRepository` using `Depends()`, and FastAPI will ensure the repository is available when the service is instantiated, as shown in the following example:

```python
from fastapi import FastAPI, Depends, HTTPException
from typing import Dict, Optional

# Mock Repository
class UserRepository:
    def __init__(self):
        self.users: Dict[int, Dict] = {1: {"name": "Alice"}, 2: {"name": "Bob"}}

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        return self.users.get(user_id)

# Dependency Provider for Repository
def get_user_repository() -> UserRepository:
    # In a real app, this would establish a DB connection
    return UserRepository()

# Mock Service that depends on the Repository
class UserService:
    def __init__(self, user_repo: UserRepository = Depends(get_user_repository)):
        self.user_repo = user_repo

    def get_user_details(self, user_id: int) -> Optional[Dict]:
        return self.user_repo.get_user_by_id(user_id)

# Dependency Provider for Service
def get_user_service(user_repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repo)

app = FastAPI()

@app.get("/users/{user_id}")
async def read_user(user_id: int, user_service: UserService = Depends(get_user_service)):
    user = user_service.get_user_details(user_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")
```

While this built-in system is remarkably powerful, a subtle gotcha emerges with very complex, nested dependencies or when dealing with circular dependencies. In such intricate scenarios, managing the dependency graph without a dedicated DI container can become unwieldy. However, for the vast majority of FastAPI applications, this declarative, Python-native approach is not only effective but also significantly more readable and maintainable than manual injection, offering a clear path to building robust and testable APIs.
