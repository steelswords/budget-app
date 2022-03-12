# Budget App

# Python virtual environment usage

**python version 3.8**

Included in this repo is a pip package list to use with a python virtual environment (venv)

## Create and activate the environment

`python -m venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

`cp sample.env .env`

## Set Up the Database

Budget-app uses a containerized postgres Docker container. Choose a better
password and start that container with the following command:

```
docker run -d --env-file .env -p 5432:5432 --name budget postgres
```

Afterward, be sure to update the values in

## Maintainance

Update the list of all packages/libraries in use in `requirements.txt` (with version if neccessary)
