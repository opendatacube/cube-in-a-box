# Cube in a Box

The Cube in a Box is a simple way to run the [Open Data Cube](https://www.opendatacube.org).
 
## How to use:
_If you have `make` installed you can use it to save some typing using the instructions a little further down._

All you need to know:

* Start a local environment: `docker-compose up`
* Set up your local postgres database (after the above has finished) using:
  * `docker-compose exec jupyter datacube -v system init`
  * `docker-compose exec jupyter datacube product add https://raw.githubusercontent.com/digitalearthafrica/config/master/products/esa_s2_l2a.yaml`
* Index a default region with either:
  * `docker-compose exec jupyter bash -c "stac-to-dc --bbox='25,20,35,30' --collections='sentinel-s2-l2a-cogs' --datetime='2020-01-01/2020-03-31' s2_l2a"`
* Shutdown your local environment:
* `docker-compose down`

If you have `make`:

* Start a local environment using `make up`
* Set up your local postgres database (after the above has finished) using `make init`
* Add the Sentinel-2 product definition `make product`
* Index a default region with `make index`
  * (optional) Edit the Makefile to change the region of interest

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
