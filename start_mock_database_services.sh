#!/bin/bash
# Script to start up testing database inside a docker container and print our the container IP address

containername=budget-postgres
db_user=budgetadmin
db_password=supersecretpassword
db_name=budget

# Check if container already exists and start it
if [ $( docker ps -a | grep $containername | wc -l ) -gt 0 ]; then
    echo "Found container $containername, starting..."
    docker start $containername
    echo "$containername started"
else    # Create new container
    echo "Creating container $containername"
    docker pull postgres:13-alpine
    docker run -d --name $containername -p 5432:5432 -e POSTGRES_USER=$db_user -e POSTGRES_PASSWORD=$db_password -e POSTGRES_DB=$db_name postgres:13-alpine
    echo "Container $containername started"
fi

# Get IP address of container
echo "Container IP: $(docker inspect $containername | grep IPAddress | awk 'FNR == 2 {print $2}')"
