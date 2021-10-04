## You can follow the steps below in order to get yourself a local ODC.
## Start by running `setup` then you should have a system that is fully configured
##
## Once running, you can access a Jupyter environment
## at 'http://localhost' with password 'secretpassword'
.PHONY: help setup up down clean

BBOX := 25,20,35,30

help: ## Print this help
	@grep -E '^##.*$$' $(MAKEFILE_LIST) | cut -c'4-'
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-10s\033[0m %s\n", $$1, $$2}'

setup: build up init products index ## Run a full local/development setup
setup-prod: up-prod init products index ## Run a full production setup

up: ## 1. Bring up your Docker environment
	docker-compose up -d postgres
	docker-compose run checkdb
	docker-compose up -d jupyter

init: ## 2. Prepare the database
	docker-compose exec -T jupyter datacube -v system init

products: ## 3. Add all product definitions
	docker-compose exec -T jupyter dc-sync-products https://raw.githubusercontent.com/digitalearthafrica/config/master/prod/products_prod.csv

index: index-sentinel index-landsat ## 4. Index a few products

index-sentinel:
	docker-compose exec -T jupyter stac-to-dc \
		--catalog-href=https://explorer.digitalearth.africa/stac/ \
		--collections=s2_l2a \
		--bbox=$(BBOX) \
		--limit=10

index-landsat:
	docker-compose exec -T jupyter stac-to-dc \
		--catalog-href=https://explorer.digitalearth.africa/stac/ \
		--collections=ls8_sr \
		--bbox=$(BBOX) \
		--datetime=2020-01-02

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
	aws s3 cp cube-in-a-box-cloudformation.yml s3://cube-in-a-box-deafrica/ --acl public-read

build-image:
	docker build --tag digitalearthafrica/cube-in-a-box .

push-image:
	docker push digitalearthafrica/cube-in-a-box

up-prod: ## Bring up production version
	docker-compose -f docker-compose-prod.yml pull
	docker-compose -f docker-compose.yml -f docker-compose-prod.yml up --detach postgres
	docker-compose run checkdb
	docker-compose -f docker-compose.yml -f docker-compose-prod.yml up --detach --no-build

create-infra:  ## Deploy to AWS
	aws cloudformation create-stack \
		--region eu-west-1 \
		--stack-name odc-test \
		--template-body file://cube-in-a-box-cloudformation.yml \
		--parameter file://parameters.json \
		--tags Key=Name,Value=OpenDataCube \
		--capabilities CAPABILITY_NAMED_IAM

update-infra: ## Update AWS deployment
	aws cloudformation update-stack \
		--stack-name eu-west-1 \
		--template-body file://cube-in-a-box-cloudformation.yml \
		--parameter file://parameters.json \
		--tags Key=Name,Value=OpenDataCube \
		--capabilities CAPABILITY_NAMED_IAM
