<h1 align="center">Cinema-backend of 4 microservices by Q1nfo</h1>



**Source Code**: [github.com/q1nfo/Fastapi-movie](https://github.com/Q1nfo/fastapi-movie)

**1 PART - admin panel in django** : [Django-admin](https://github.com/Q1nfo/django-admin) \
**2 PART - core functionality manager on FastApi** : [Fastapi-movie](https://github.com/Q1nfo/fastapi-movie) \
**3 PART - service updating data from the database in ElasticSearch** : [Db-to-Elastic](https://github.com/Q1nfo/service_db_to_elastic) \
**4 PART - auth service on Flask**: [Flask-auth]()

---

<!--intro-start-->

Cinema project, which consists of 3 microservices interacting with each other via docker-compose


Еhis is the second backend service for the cinema, which is written 
in the asynchronous FastApi framework, and allows you to very quickly 
interact with the full-text database of this Elasticsearch, which is 
filled thanks to another service

To get started, jump to the [installation](#installation) section or keep reading to learn more about the included
features.
<!--intro-end-->

<!--readme-start-->

## ✨ Features

### 📦️ FastApi technologies

* [FastApi](https://fastapi.tiangolo.com/) - FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints.
* [Uvicorn](https://www.uvicorn.org/) - Uvicorn is an ASGI web server implementation for Python.
* [Elasticsearch](https://www.elastic.co/elasticsearch) - Elasticsearch is a distributed, RESTful search and analytics engine capable of addressing a growing number of use cases.
* [Pydantic](https://docs.pydantic.dev/latest/) - Pydantic is the most widely used data validation library for Python.
* [Pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Pydantic Settings provides optional Pydantic features for loading a settings or config class from environment variables or secrets files.
* [SQlAlchemy](https://www.sqlalchemy.org/) - SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.
* [Pytest](https://docs.pytest.org/en/7.4.x/) - The pytest framework makes it easy to write small, readable tests, and can scale to support complex functional testing for applications and libraries.

### 🩺 Code Quality, Formatting, and Linting Tools

* [Flake8](https://flake8.pycqa.org/) - Tool For Style Guide Enforcement
* [pre-commit](https://pre-commit.com/) - Git hook scripts are useful for identifying simple issues before submission to code review.
* [isort](https://pycqa.github.io/isort/) - isort is a Python utility / library to sort imports alphabetically, and automatically separated into sections and by type.

### Tests

    run in bash: pytest

## Installation

### Requirements

Before proceeding make sure you have installed [Docker](https://docs.docker.com/engine/installation/) . Docker with Docker Compose is used for local development.

### Manual Installation

    $ gh repo clone Q1nfo/fastapi-movies
    $ mv fastapi-movies example
    $ cd example

    touch .env

    pip install -r requirements


<!--readme-end-->