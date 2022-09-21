# Fred Miranda Buy/Sell Post Exporter

This is a python script that has been containerized into a Docker container to pull all new content from the Fred Miranda Buy & Sell Forums and dump the data to a Postgres DB.

## Prerequisites

- Postgres Database
    - Postgres Database Name (DBNAME)
    - Postgres Database Username (DBUSER)
    - Postgres Database Password (DBPASS)
    - Postgres Database Hostname (DBHOST)
- Docker

## Docker Hub Repo

[https://hub.docker.com/repository/docker/yenba/fredmiranda-post-upload-docker](https://hub.docker.com/repository/docker/yenba/fredmiranda-post-upload-docker)

## Docker Run Command

Run your docker command like this:

```
docker run -it --rm --env "DBNAME=YOUR_DB_NAME_HERE" --env "DBUSER=YOUR_DB_USERNAME_HERE" --env "DBPASS=YOUR_DB_PASSWORD_HERE" --env "DBHOST=YOUR_DB_HOSTNAME_OR_IP_HERE" yenba/fredmiranda-post-upload-docker

```
