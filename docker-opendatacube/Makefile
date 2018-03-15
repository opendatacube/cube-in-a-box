build-core:
	docker build -t alexgleith/opendatacube .

build-odc-jupyter:
	docker build -t odc-jupyter:local --file DockerfileJupyter .

build:
	docker-compose build

push:
	docker push alexgleith/opendatacube

up:
	docker-compose up

odc-cmd:
	docker-compose exec opendatacube bash

# Prepare the database
initdb:
	docker-compose exec opendatacube datacube -v system init

# Load test data
load-LS8:
	docker-compose exec opendatacube /data_scripts/load-LS8.sh

# Test the system
test: create-db integration-tests

create-db:
	docker-compose exec postgres createdb -U postgres odcintegration

integration-tests:
	docker-compose exec opendatacube bash -c "cd /opt/opendatacube/ && ./check-code.sh integration_tests/"

# Clean up
clean:
	docker-compose rm -f
