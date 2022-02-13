# Setup

Budget-app uses a containerized postgres Docker container. Choose a better
password and start that container with the following command:

```
docker run -it --rm -e POSTGRES_PASSWORD=password -e POSTGRES_USER=postgres -e POSTGRES_DB=budget -p 5432:5432 --name budget postgres
```
