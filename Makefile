IGNORE_FLAG = 
ifeq ($(OS),Windows_NT)
    IGNORE_FLAG = '--ignore-garbage'
endif

create-infra:
	aws cloudformation create-stack \
		--region ap-southeast-2 \
		--stack-name esp-v2-infrastructure \
		--template-body file://opendatacube-test.yml \
		--parameter file:///parameters.json \
		--tags Key=name,Value=OpenDataCube \
		--capabilities CAPABILITY_NAMED_IAM

update-infra:
	aws cloudformation update-stack \
		--stack-name esp-v2-infrastructure \
		--template-body file://opendatacube-test.yml \
		--parameter file:///parameters.json \
		--tags Key=name,Value=OpenDataCube \
		--capabilities CAPABILITY_NAMED_IAM