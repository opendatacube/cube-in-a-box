# Open Data Cube in Docker

## What have we got here
The goal of this project is to enable a very simple reference implementation of the Open Data Cube for Docker.

## How can I use it
There's a Makefile with a number of commands in it, but we use standard Docker and Docker Compose processes.

## Getting started

1. Install [Docker](https://docs.docker.com/install/) and [Docker Compose](https://docs.docker.com/compose/install/).
2. Start the docker-compose process with `make up` or `docker-compose up`
3. To initialise the database for use, run the command `make initdb` or `docker-compose exec opendatacube datacube -v system init`. _Note that you must have the system running in step 2 for this to work._
4. Load some data (there is an example load script in 'data_scripts', although you will need to grab some Landsat 5 data that is in Australia to work with... TODO: find a good place to get this from).
5. Open up the Jupyter interface, which is running at http://localhost:8888 (or your docker machine IP on Windows)
