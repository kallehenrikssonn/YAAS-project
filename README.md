# 2019-web-services-project-skeleton

This is a tutorial how to setup and use the framework.

## Packages installation

First thing first, you need to install all packages in the `requirements.txt` file. 
They should be automatically detected and installed by Python Interpreter.

## Initializing the database

Before running the project, you need to initialize/update the database (i.e., `db.sqlite3`). Run the following command
in your project directory:
```
$ ./manage.py migrate
```
Read more django migrations [here](https://docs.djangoproject.com/en/2.2/topics/migrations/)

## Settings

There are some attributes in `settings.py` file that you need to pay attention.

- `SECRET_KEY`: It should be unique and kept secret if you plan to deploy your web application. You can generate a new one 
for your project. You can generate a key by using an online generator like this 
[Djecrety](https://djecrety.ir/); or by the below code in Python console:
```
>>> import random
>>> ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50))
```

- `INSTALLED_APPS`: A list of strings of used packages and apps in this project. It is split into 
`PREREQ_APPS` and `PROJECT_APPS` for clarity reasons. The former consists of Django packages and 
the latter contains project user-defined apps. One can freely add more packages or apps 
if needed in their appropriate locations.

- `AUTH_PASSWORD_VALIDATORS`: A list of strings for types of password validators. 
In the beginning, it is empty for the sake of testing.

## Structure

The project comes with two apps, auction and user. All required URLs are provided in `urls.py` 
files of the project and apps. The routes of `urls` can be changed if wanted but the `name` and 
`namespace` are not allowed to change. The `views.py` files have empty functions that are ready 
to be implemented. You are open to create new apps if you want, just make sure followwing
the structure.
