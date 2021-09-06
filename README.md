# Cube in a Box

The Cube in a Box is a simple way to run the [Open Data Cube](https://www.opendatacube.org).

## How to use:

### 1. Setup:
_First time users of Docker should run:_
* `bash setup.sh` - This will get your system running and install everything you need.
* Note that after this step you will either need to logout/login, or run the next step with `sudo`

*If you already have `make` , `docker` and `docker-compose` installed*
* `make setup`

*If you do not have `make` installed and would rather run the commands individually run the following:*

* Build a local environment: `docker-compose build`
* Start a local environment: `docker-compose up`
* Set up your local postgres database (after the above has finished) using:
  * `docker-compose exec jupyter datacube -v system init`
  * `docker-compose exec jupyter datacube product add https://raw.githubusercontent.com/digitalearthafrica/config/master/products/esa_s2_l2a.odc-product.yaml`
* Index a default region with:
  * `docker-compose exec jupyter bash -c "stac-to-dc --bbox='25,20,35,30' --collections='sentinel-s2-l2a-cogs' --datetime='2020-01-01/2020-03-31'"`
* Shutdown your local environment:
  * `docker-compose down`

### 2. Usage:
View the Jupyter notebook `Sentinel_2.ipynb` at [http://localhost](http://localhost) using the password `secretpassword`. Note that you can index additional areas using the `Indexing_More_Data.ipynb` notebook.

## Deploying to AWS

To deploy to AWS, you can either do it on the command line, with the AWS command line installed or the magic URL below and the AWS console. Detailed instructions are [available](docs/Detailed_Install.md).

Once deployed, if you navigate to the IP of the deployed instance, you can access Jupyter with the password you set in the parameters.json file or in the AWS UI if you used the magic URL.

### Magic link

[Launch a Cube in a Box](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=cube-in-a-box&templateURL=http://opendatacube-cube-in-a-box.s3.amazonaws.com/cube-in-a-box-cloudformation.yml)

You need to be logged in to the AWS Console deploy using this URL. Once logged in, click the link, and follow the prompts including settings a bounding box region of interest, EC2 instance type and password for Jupyter.

### Command line

* Alter the parameters in the [parameters.json](./parameters.json) file
* Run `make create-infra`
* If you want to change the stack, you can do `make update-infra` (although it may be cleaner to delete and re-create the stack)
