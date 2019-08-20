# You can follow the steps below in order to get yourself a local ODC.
# Once running, you can access a Jupyter environment 
# at 'http://localhost' with password 'secretpassword'

# 1. Get the pathrows file
download-pathrows-file:
	wget https://landsat.usgs.gov/sites/default/files/documents/WRS2_descending.zip -O ./data/wrs2_descending.zip

# 2. Start your Docker environment
up:
	docker-compose up

# 3. Prepare the database
initdb:
	docker-compose exec jupyter datacube -v system init
	docker-compose exec jupyter datacube product add /opt/odc/docs/config_samples/dataset_types/ls_usgs.yaml

# 4. Index a dataset (just an example, you can change the extents)
index:
	# Note that you need environment variables ODC_ACCESS_KEY and ODC_SECRET_KEY set.
	# These need to be valid AWS keys. KEEP THEM SECRET, KEEP THEM SAFE!

	docker-compose exec jupyter bash -c \
		"cd /opt/odc/scripts && python3 ./autoIndex.py \
			-p '/opt/odc/data/wrs2_descending.zip' \
			-e '146.30,146.83,-43.54,-43.20'"

product-landsat:
	docker-compose exec jupyter \
		datacube product add /opt/odc/scripts/product_definitions/ls_usgs_sr_scene.yaml

product-wofs:
	docker-compose exec jupyter \
		datacube product add /opt/odc/scripts/product_definitions/wofs.yaml

product-fc:
	docker-compose exec jupyter \
		datacube product add /opt/odc/scripts/product_definitions/ls_usgs_fc_scene.yaml

index-landsat:
	docker-compose exec jupyter bash -c \
		"cd /opt/odc/scripts && python3 ./ls_public_bucket.py frontiersi-odc-test \
		-p test \
		--suffix="T1.xml" \
		--start_date 1980-01-01 --end_date 2020-01-01"

index-wofs:
	docker-compose exec jupyter bash -c \
		"cd /opt/odc/scripts && python3 ./ls_public_bucket.py frontiersi-odc-data \
		-p case-studies/wofs/usgs \
		--suffix=".yaml" \
		--start_date 1980-01-01 --end_date 2020-01-01"

index-fc:
	docker-compose exec jupyter bash -c \
		"cd /opt/odc/scripts && python3 ./ls_public_bucket.py frontiersi-odc-data \
		-p case-studies/fc/usgs \
		--suffix=".yaml" \
		--start_date 1980-01-01 --end_date 2020-01-01"

index-landsat-prod:
	docker-compose exec jupyter bash -c \
		"cd /opt/odc/scripts && python3 ./ls_public_bucket.py frontiersi-odc-data \
		-p case-studies/usgs/LANDSAT_8 \
		--suffix="T1.xml" \
		--start_date 1980-01-01 --end_date 2020-01-01"

check-landsat:
	docker-compose exec jupyter bash -c \
		datacube product list \
		&& datacube dataset search product ='landsat_8_USARD' |grep id |wc -l

# for DEAfrica
index-africa-vic-landsat:
	docker-compose exec jupyter bash -c \
		"cd /opt/odc/scripts && python3 ./ls_public_bucket.py deafrica-data \
		-p test \
		--suffix=".xml" \
		--start_date 1980-01-01 --end_date 2020-01-01"


# Some extra commands to help in managing things.
# Rebuild the image
build:
	docker-compose build

# Start an interactive shell
shell:
	docker-compose exec jupyter bash

# Delete everything
clear:
	docker-compose stop
	docker-compose rm -fs

# Blow it all away and start again. First start the stack with `make up`
load-from-scratch: initdb download-pathrows-file index

# Update S3 template (this is owned by FrontierSI)
update-s3:
	aws s3 cp opendatacube-test.yml s3://cubeinabox/ --acl public-read

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

# For testing DEAfrica

#  Initialise the database
af_initdb:
	docker-compose exec jupyter datacube -v system init

#  Add the DEAfrica products
af_add_prod:
	cp -R ${DEAFRICA_PRODUCTS} ./data/products
	#docker-compose exec jupyter datacube metadata add /opt/odc/data/products/eo3.yaml
	docker-compose exec jupyter datacube product add /opt/odc/data/products/ls5_usgs_sr_scene.yaml
	docker-compose exec jupyter datacube product add /opt/odc/data/products/ls7_usgs_sr_scene.yaml
	docker-compose exec jupyter datacube product add /opt/odc/data/products/ls8_usgs_sr_scene.yaml
	docker-compose exec jupyter datacube product add /opt/odc/data/products/ls_usgs_fc_scene.yaml
	docker-compose exec jupyter datacube product add /opt/odc/data/products/ls_usgs_wofs_scene.yaml

