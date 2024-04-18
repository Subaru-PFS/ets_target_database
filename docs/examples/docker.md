# Run `targetdb` in a Docker container

If you do not have a PostgreSQL server, you can use a Docker container to host a database for testing without affecting the host environment.
To set up a PostgreSQL Docker container, you need to install Docker from [Docker Hub](https://hub.docker.com/search?type=edition&offering=community).

## Build a Docker container

Example `docker-compose.yml` and `Dockerfile` files are provided in the `examples/docker` directory.

```bash
# Build the Docker container with the Q3C extension.
docker-compose build

# Start the Docker container.
docker-compose up -d
```

In the above will create a Docker container with the Q3C extension and start the PostgreSQL server.
The database data will be stored in the `examples/docker/db-data` directory and can be assessed from the host
by using the PostgreSQL client via the port 15432 (see `examples/docker/db-conf.toml`).

You need to enable the Q3C extension in the database as follows:

```bash
psql -h localhost -U admin -d targetdb_local_test -p 15432 -c "CREATE EXTENSION q3c;"
```

After finishing the test, you can stop the Docker container as follows:

```bash
# Stop the Docker container.
docker-compose down
```
