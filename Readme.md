# Todoapp

## Overview

The app has been written in django framework using python 3 and is deployed on K8s. The app uses a High availibility postgres database cluster with a main postgres and a standby replica.

You can go to the app using the URL: `todoapp.devopsnote.com` (I own the devopsnote.com domain and it points to the loadbalancer service on K8s cluster). You can also use the load balancer IP address(35.202.60.45), but then you have to whitelist the IP address under allowed hosts settings in file todoapp/settings.py


## Architecture Diagram

![alt text](https://github.com/harmansethi92/todoapp/blob/master/todoapp/todoapp.png)


### django application
1. It's written in python3 and dependencies are stored in the requirments.txt file
2. todoapp directory has the settings and urls for the project
3. todolist directory consists of the db models.py and the views.py which consists the main logic, admin.py and apps.py files.
4. the todolist/templates/index.html has the html form for the application
5. the todolist/migrations directory consists of all the db migrations
6. Dockerfile can be used to create the image of the app.
7. docker-compose.yaml can be used to run the app locally

#### postgres
1. using the basic postgres image to build the app locally and on k8s using kubeDB postgres.
2. All records are stored under the todolist_todolist table in postgres db


## Deployment
The deployment for the app is setup on kubernetes cluster (gorgias). It's a basic 3 node cluster with minimal resources.

The k8s cluster has 2 main pieces and all pods, services, storage is setup under the todolist namespace on the k8s cluster.

#### 1. django
- k8s/django/deployment.yaml (django backend app in 3 pods)
- k8s/django/service.yaml (loadbalancer services which exposes the app)
- k8s/django/secrets.yaml (which stores the user,password and db name for postgres)

All the files can be built using the command: kubectl apply -f <filename> -n todolist

#### 2. postgres
- postgres cluster with a primary and a standby node which has a streaming replication.

- I have set this up using KubeDB. And have installed the kubeDB operator using the following script. You can also use Helm to setup the deployment.

$ curl -fsSL https://github.com/kubedb/installer/raw/v0.13.0-rc.0/deploy/kubedb.sh | bash

- I'm using the file k8s/postgres/statefulset.yaml to build stateful postgres db, services, persistent volume and persistent volume claims. 

- The password of the db is randomly generated after it has been created and can be fetched by connecting through the cloud shell using the command:

$ kubectl get secrets -n todolist ha-postgres-auth -o jsonpath='{.data.\POSTGRES_PASSWORD}' | base64 -d

This password is then stored in the secrets.yaml file for django application to pull the values from.



## Setup

### On Local environment

1. You can clone the application using `git clone https://github.com/harmansethi92/todoapp.git`

2. You can use the docker-compose file to setup the django application and postgres container. Use the command `docker-compose up`

3. After the containers are setup, exec into the django container and run migration

$ docker exec -it <name of container> /bin/bash

$ python3 manage.py migrate

4. After you make changes to your code you can run following commands to rebuild the app.

$ docker-compose up --build


### On K8s cluster

You can connect to the cluster using the google cloud shell on GKE console or the kube config file.

#### postgres:
1. Setup the kubeDB operator on the k8s cluster.

$ curl -fsSL https://github.com/kubedb/installer/raw/v0.13.0-rc.0/deploy/kubedb.sh | bash

2. setup postgres through the statefulset file. Run the command:

$ kubectl apply -f k8s/postgres/statefulset.yaml -n todolist

2. Run the command to get the user for db.
$ kubectl get secrets -n todolist ha-postgres-auth -o jsonpath='{.data.\POSTGRES_USER}' | base64 -d

3. Run the command to get pwd for db.
$ kubectl get secrets -n todolist ha-postgres-auth -o jsonpath='{.data.\POSTGRES_PASSWORD}' | base64 -d

Add the above credentials output to the secrets.yaml file base64 encoded for django application under k8s/django/secrets.yaml

#### django

1. create the secrets using secrets.yaml file. You need to update the password from above, not versioning the password for enhanced security

$ kubectl apply -f k8s/django/secrets.yaml -n todolist

2. create the django deployment using the command:

$ kubectl apply -f k8s/django/deployment.yaml -n todolist

3. create the django service and load balancer to serve the application:

$ kubectl apply -f k8s/django/service.yaml -n todolist



4. After the deployment becomes live, exec into the django kubernetes pod and run the migration to create tables on postgres.

$ kubectl exec <pod-name> -n todolist /bin/bash

/usr/src/app# python3 manage.py migrate

This step can also be done through a k8s Job service to run it.



## Testing

1. Docker Image

- We are using the image harmansethi92/todolist:1.1 which is a public repo setup on Dockerhub, you can use the repository to push more images with different tags.

2. Automatic failover
 
- The postgres cluster is in a primary/standy mode with asynchronous replication. As of now pod ha-postgres-0 is primary server and ha-postgres-1 is serving as standby server. You can delete the primary node to test out the High availibility feature using command `kubectl delete pod -n todolist ha-postgres-0`, which would promote standy pod ha-postgres-1 to primary and make ha-postgres-0 as standy.

3. Streaming information

- You can check pg_stat_replication information to know who is currently streaming from primary. Run following commands to test it.

$ kubectl exec -it <pod-name> -n todolist /bin/bash

bash-4.3# psql -h 127.0.0.1 -U postgres -d postgres -p 5432

postgres=# select * from pg_stat_replication;

4. DEBUG=True for the django backend as of now. So anytime you hit an exception/error it would give you detailed info on the browser. 

5. The django is setup as deployment and not a replication controller, so the pods are not self healing. 

6. You can use the rolling update k8s feature to deploy new code without any downtime. 

7. There is also an option to setup the k8s deployment files using helm or Terraform, but I have just used simple way of deployment for this project. 




## Helpful Links
- [Documentaton KubeDB](https://kubedb.com/docs/0.11.0/guides/postgres/clustering/streaming_replication/)














