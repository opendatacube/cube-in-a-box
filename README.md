# Cube in a Box
The Cube in a Box is a simple way to run the [Open Data Cube](https://opendatacube.com).
 
# How to use:
_If you have `make` installed you can use it to save some typing using the instructions a little further down._

All you need to know:
 * Set environment variables for `ODC_ACCESS_KEY` and `ODC_SECRET_KEY` to something valid with your AWS account credentials.
 * Start a local environment: `docker-compose up`
 * Set up your local postgres database (after the above has finished) using:
   * `docker-compose exec jupyter datacube -v system init`
   * `docker-compose exec jupyter datacube product add https://raw.githubusercontent.com/opendatacube/datacube-dataset-config/master/products/ls_usgs_level1_scene.yaml`
 * Index a default region with either:
   * `docker-compose exec jupyter bash -c "cd /opt/odc/scripts && python3 ./autoIndex.py -e '146.30,146.83,-43.54,-43.20'"`
   * `docker-compose exec jupyter bash -c "cd /opt/odc/scripts && python3 ./autoIndex.py -e '146.30,146.83,-43.54,-43.20' --start_date '2018-01-01' --end_date '2018-10-09'"`
 * View the Jupyter notebook at [http://localhost](http://localhost) using the password `secretpassword`
 * Shutdown your local environment:
   * `docker-compose down`

If you have `make`:
 * Set environment variables for `ODC_ACCESS_KEY` and `ODC_SECRET_KEY` to something valid with your AWS account credentials.
 * Start a local environment using `make up`
 * Set up your local postgres database (after the above has finished) using `make initdb`
 * Add the Landsat level 1 product definition `make add-product-definition`
 * Index a default region with `make index` 
    * (optional) Edit the Makefile to change the region of interest
 * View the Jupyter notebook at [http://localhost](http://localhost) using the password `secretpassword`

# Deploying to AWS:
To deploy to AWS, you can either do it on the command line, with the AWS command line installed or the magic URL below and the AWS console. Detailed instructions are [available](docs/Detailed_Install.md).

Once deployed, if you navigate to the IP of the deployed instance, you can access Jupyter with the password you set in the parameters.json file or in the AWS UI if you used the magic URL.

## Magic link
[Launch a Cube in a Box](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=cube-in-a-box&templateURL=http://opendatacube-cube-in-a-box.s3.amazonaws.com/cube-in-a-box-cloudformation.yml)

You need to be logged in to the AWS Console deploy using this URL. Once logged in, click the link, and follow the prompts including settings a bounding box region of interest, EC2 instance type and password for Jupyter.

## Command line
 * Alter the parameters in the [parameters.json](./parameters.json) file
 * Run `make create-infra`
 * If you want to change the stack, you can do `make update-infra` (although it may be cleaner to delete and re-create the stack)

# IMPORTANT NOTES
In your local environment, in order to be able to get data from S3, you need to ensure that the environment variables `ODC_ACCESS_KEY` and `ODC_SECRET_KEY` are set to something valid. If using AWS, these parameters are automatically included.

## Environment variables for Docker Compose
Environment variables can be set in a .env file for Docker Compose. You might use [.env.example](./.env.example) as a starting point.
