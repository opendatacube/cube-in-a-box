create-infra:
	aws cloudformation create-stack \
		--region ap-southeast-2 \
		--stack-name odc-test \
		--template-body file://opendatacube-test.yml \
		--parameter file://parameters.json \
		--tags Key=name,Value=OpenDataCube \
		--capabilities CAPABILITY_NAMED_IAM

update-infra:
	aws cloudformation update-stack \
		--stack-name odc-test \
		--template-body file://opendatacube-test.yml \
		--parameter file://parameters.json \
		--tags Key=name,Value=OpenDataCube \
		--capabilities CAPABILITY_NAMED_IAM

up:
	docker-compose up

# Prepare the database
initdb:

	docker-compose exec opendatacube datacube -v system init
	docker-compose exec opendatacube datacube product add /opt/odc/docs/config_samples/dataset_types/ls_usgs.yaml


# Index a dataset (just an example)
index:
	# Note that you need environment variables ODC_ACCESS_KEY and ODC_SECRET_KEY set.
	# These need to be valid AWS keys. KEEP THEM SECRET, KEEP THEM SAFE!

	docker-compose exec opendatacube bash -c \
		"cd /opt/odc/scripts && python3 ./autoIndex.py -p '/opt/odc/data/wrs2_asc_desc.zip'"

# Get the pathrows file
download-pathrows-file:
	wget https://landsat.usgs.gov/sites/default/files/documents/wrs2_asc_desc.zip -O ./data/wrs2_asc_desc.zip

# Delete everything
clear:
	docker-compose stop
	docker-compose rm -fs
