# Cube in a Box
The Cube in a Box is a simple way to run the [OpenDataCube](https://opendatacube.com). This repository is a work in progress that 
 
# Some notes:
 * Start a local environment using `make up` or `docker-compose up`
 * Set up your local postgres database (after the above has finished) using `make init-db` (or see the [Makefile](./Makefile) for the exact commands)
 * Before indexing Landsat 8, you need to grab the pathrows index using `make download-pathrows-file`
 * Index a default region with `make index` 
 * Edit the Makefile to change the region of interest
 * You can set up the Dashboard using `make prepare-dashboard`

Todo:
 * Set up notebooks that work on indexed data

# Deploying to AWS:
To deploy to AWS, you cam either do it on the command line, with the AWS command line installed or the magic URL below and the AWS console.

## Magic URL
[Launch a Cube in a Box](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=cube_in_a_box&templateURL=https://raw.githubusercontent.com/crc-si/opendatacube-cloudformation-testing/master/opendatacube-test.yml)

## Command line
 * Alter the parameters in the [parameters.json](./parameters.json) file
 * Run `make create-infra`
 * If you want to change the stack, you can do `make update-infra` (although it may be cleaner to delete and re-create the stack)


# IMPORTANT NOTES
In your local environment, in order to be able to get data from S3, you need to ensure that the environment variables `ODC_ACCESS_KEY` and `ODC_SECRET_KEY` are set to something valid.
