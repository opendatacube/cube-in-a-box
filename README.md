# Cube in a Box
The Cube in a Box is a simple way to run the [OpenDataCube](https://opendatacube.com). This repository is a work in progress that 
 
# Some notes:
 * Start a local environment using `make up` or `docker-compose up`
 * Set up your local postgres database (after the above has finished) using `make init-db` (or see the [Makefile](./Makefile) for the exact commands)
 * Before indexing Landsat 8, you need to grab the pathrows index using `make download-pathrows-file`
 * Index a default region with `make index` 
    * Edit the Makefile to change the region of interest
 * View the Jupyter notebook at [http://localhost](http://localhost) using the password `secretpassword`

Todo:
 * Set up notebooks that work on indexed data

# Deploying to AWS:
To deploy to AWS, you cam either do it on the command line, with the AWS command line installed or the magic URL below and the AWS console.

Once deployed, if you navigate to the IP of the deployed instance, you can access Jupyter with the password you set in the parameters.json file or in the AWS UI if you used the magic URL.

## Magic URL
[Launch a Cube in a Box](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=cube-in-a-box&templateURL=https://s3-ap-southeast-2.amazonaws.com/cubeinabox/opendatacube-test.yml)

You need to be logged in to the AWS Console deploy using this URL. Once logged in, click the link, and follow the prompts including settings a bounding box region of interest, EC2 instance type and password for Jupyter.

## Command line
 * Alter the parameters in the [parameters.json](./parameters.json) file
 * Run `make create-infra`
 * If you want to change the stack, you can do `make update-infra` (although it may be cleaner to delete and re-create the stack)

# IMPORTANT NOTES
In your local environment, in order to be able to get data from S3, you need to ensure that the environment variables `ODC_ACCESS_KEY` and `ODC_SECRET_KEY` are set to something valid.
