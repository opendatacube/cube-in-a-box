# Cube in a Box
The Cube in a Box is a simple way to run the [OpenDataCube](https://opendatacube.com).
 
# How to use:
_If you have `make` installed you can use it to save some typing using the instructions a little further down._

All you need to know:
 * Set environment variables for `ODC_ACCESS_KEY` and `ODC_SECRET_KEY` to something valid with your AWS account credentials.
 * Start a local environment: `docker-compose up`
 * Set up your local postgres database (after the above has finished) using:
   * `docker-compose exec jupyter datacube -v system init`
   * `docker-compose exec jupyter datacube product add /opt/odc/docs/config_samples/dataset_types/ls_usgs.yaml`
 * Before indexing Landsat 8, you need to grab the pathrows index. Download the file from [here](https://landsat.usgs.gov/sites/default/files/documents/WRS2_descending.zip) and save the zip file to `data/wrs2_descending.zip`
 * Index a default region with:
   * `docker-compose exec jupyter bash -c "cd /opt/odc/scripts && python3 ./autoIndex.py -p '/opt/odc/data/wrs2_descending.zip' -e '146.30,146.83,-43.54,-43.20'"`
 * View the Jupyter notebook at [http://localhost](http://localhost) using the password `secretpassword`
 * Shutdown your local environment:
   * `docker-compose down`

If you have `make`:
 * Set environment variables for `ODC_ACCESS_KEY` and `ODC_SECRET_KEY` to something valid with your AWS account credentials.
 * Start a local environment using `make up`
 * Set up your local postgres database (after the above has finished) using `make initdb`
 * Before indexing Landsat 8, you need to grab the pathrows index using `make download-pathrows-file`
 * Index a default region with `make index` 
    * Edit the Makefile to change the region of interest
 * View the Jupyter notebook at [http://localhost](http://localhost) using the password `secretpassword`

To-do:
 * Set up notebooks that work on indexed data

# Deploying to AWS:
To deploy to AWS, you can either do it on the command line, with the AWS command line installed or the magic URL below and the AWS console. Detailed instructions are [provided below](https://github.com/LSgeo/opendatacube-cloudformation-testing/blob/master/README.md#detailed-amazon-web-services-aws-install-instructions).

Once deployed, if you navigate to the IP of the deployed instance, you can access Jupyter with the password you set in the parameters.json file or in the AWS UI if you used the magic URL.

## Magic URL
[Launch a Cube in a Box](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=cube-in-a-box&templateURL=https://s3-ap-southeast-2.amazonaws.com/cubeinabox/opendatacube-test.yml)

You need to be logged in to the AWS Console deploy using this URL. Once logged in, click the link, and follow the prompts including settings a bounding box region of interest, EC2 instance type and password for Jupyter.

## Command line
 * Alter the parameters in the [parameters.json](./parameters.json) file
 * Run `make create-infra`
 * If you want to change the stack, you can do `make update-infra` (although it may be cleaner to delete and re-create the stack)

# IMPORTANT NOTES
In your local environment, in order to be able to get data from S3, you need to ensure that the environment variables `ODC_ACCESS_KEY` and `ODC_SECRET_KEY` are set to something valid. If using AWS, these parameters are automatically included.

## Environment variables for Docker Compose
Environment variables can be set in a .env file for Docker Compose. You might use [.env.example](./.env.example) as a starting point.
