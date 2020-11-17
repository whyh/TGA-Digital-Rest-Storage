# TGA-Digital-Rest-Storage
## TGA Digital Test Assignment

A simple api to a key-value storage


I have chosen to use asynchronous FastAPI framework because it provides a simple and intuitive interface to develop APIs. 
For a key value storage I decided to use Redis. Another option I have considered was a Python dictionary.
While it's possible to provide persistence across multiple executions, dumping the dictinary with pickle / json, and loading it on the application startup.
Redis is a robust solution, and makes more sense to use


### Documentation
FastAPI has Swagger / OpenAPI integration out of the box. You can access it at `/docs`


### How to run
Clone the repository, run `docker-compose up`. Tests can be gathered and executed with `pytest tests`


### Code formatting
Code is formatted with `black`, `isort`, `autoflake`, `flake8` and is checked to be in compliance with `mypy`
