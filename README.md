# Budget App

## Running the app

1. Activate the virtual env
1. run `python dash_frontend.py` to start the program
1. Navigate to the address the server is started on (i.e. `localhost:8050`)

## Python virtual environment usage

**python version 3.8**

Included in this repo is a pip package list to use with a python virtual environment (venv)

### Create and activate the environment

`python -m venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

`cp sample.env .env`

### Set Up the Database

Budget-app uses a containerized postgres Docker container. Choose a better
password and start that container with the following command:

```
docker run -d --env-file .env -p 5432:5432 --name budget postgres
```

Afterward, be sure to update the values in

### Maintainance

Update the list of all packages/libraries in use in `requirements.txt` (with version if neccessary)
