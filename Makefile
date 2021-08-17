## You can follow the steps below in order to get yourself a local ODC.
## Start by running `setup` then you should have a system that is fully configured
##
## Once running, you can access a Jupyter environment
## at 'http://localhost' with password 'secretpassword'

BBOX := 25,20,35,30

help: ## Print this help
	@grep -E '^##.*$$' $(MAKEFILE_LIST) | cut -c'4-'
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-10s\033[0m %s\n", $$1, $$2}'

setup: build up init product index ## Run a full setup, or manually run the following 4 steps

up: ## 1. Bring up your Docker environment
	docker-compose up --detach postgres
	docker-compose run checkdb
	docker-compose up --detach jupyter

init: ## 2. Prepare the database
	docker-compose exec jupyter datacube -v system init

product: ## 3. Add a product definition for Sentinel-2
	docker-compose exec jupyter \
		datacube product add \
			https://raw.githubusercontent.com/digitalearthafrica/config/master/products/esa_s2_l2a.odc-product.yaml \
			https://raw.githubusercontent.com/opendatacube/datacube-dataset-config/master/products/io_lulc.odc-product.yaml \
			https://raw.githubusercontent.com/opendatacube/datacube-dataset-config/master/products/nasadem.odc-product.yaml


index: ## 4. Index some data (Change extents with BBOX='<left>,<bottom>,<right>,<top>')
	docker-compose exec jupyter bash -c \
		"stac-to-dc \
			--bbox='$(BBOX)' \
			--catalog-href='https://earth-search.aws.element84.com/v0/' \
			--collections='sentinel-s2-l2a-cogs' \
			--datetime='2021-06-01/2021-07-01'"
	docker-compose exec jupyter bash -c \
		"stac-to-dc \
			--catalog-href=https://planetarycomputer.microsoft.com/api/stac/v1/ \
			--collections='io-lulc'"
	docker-compose exec jupyter bash -c \
		"stac-to-dc \
			--catalog-href='https://planetarycomputer.microsoft.com/api/stac/v1/' \
			--collections='nasadem' \
			--bbox='$(BBOX)'"

down: ## Bring down the system
	docker-compose down

build: ## Rebuild the base image
	docker-compose pull
	docker-compose build

shell: ## Start an interactive shell
	docker-compose exec jupyter bash

clean: ## Delete everything
	docker-compose down --rmi all -v

logs: ## Show the logs from the stack
	docker-compose logs --follow

upload-s3: # Update S3 template (this is owned by Digital Earth Australia)
	aws s3 cp cube-in-a-box-cloudformation.yml s3://opendatacube-cube-in-a-box/ --acl public-read

build-image:
	docker build --tag opendatacube/cube-in-a-box .

push-image:
	docker push opendatacube/cube-in-a-box

up-prod: ## Bring up production version
	docker-compose -f docker-compose-prod.yml pull
	docker-compose -f docker-compose.yml -f docker-compose-prod.yml up --no-build

# This section can be used to deploy onto CloudFormation instead of the 'magic link'
create-infra:
	aws cloudformation create-stack \
		--region ap-southeast-2 \
		--stack-name odc-test \
		--template-body file://opendatacube-test.yml \
		--parameter file://parameters.json \
		--tags Key=Name,Value=OpenDataCube \
		--capabilities CAPABILITY_NAMED_IAM

update-infra:
	aws cloudformation update-stack \
		--stack-name odc-test \
		--template-body file://opendatacube-test.yml \
		--parameter file://parameters.json \
		--tags Key=Name,Value=OpenDataCube \
		--capabilities CAPABILITY_NAMED_IAM
