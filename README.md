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

## Environment variables for Docker Compose
Environment variables can be set in a .env file for Docker Compose. You might use [.env.example](./.env.example) as a starting point.

## Detailed Docker Install Instructions
If you are unfamiliar with Docker or Jupyter, this guide will take you through downloading Docker to setting up a Cube in a Box Jupyter Server running the Open Data Cube. While these instructions specifically suit windows, the steps can easily be adapted for other a different OS, using a Terminal instead of PowerShell, and the appropriate Docker version.

* First, [download Docker for Windows](https://docs.docker.com/docker-for-windows/install/).
In Windows, we can use PowerShell to interact with the Docker command line. Please note, PowerShell ISE will not work.
* Next, download the [Data Cube setup files and code](https://github.com/LSgeo/opendatacube-cloudformation-testing/archive/master.zip) from the above repository and unzip into a local folder of your choice. Navigate to this folder in PowerShell using the cd command, e.g. 'cd C:/cubeinabox/'. Don't forget, you can use tab to complete, and dir to display the contents of the current folder.
* Follow [Docker's Orientation](https://docs.docker.com/get-started/) to familiarise yourself with Docker. At the end, you should be able to run `docker info` to view your installation details. These details can help troubleshoot a Docker installation.
* Now, we are going to create and run the Docker Container for our CIAB install. 
* In your folder containing the downloaded CIAB files, enter the command `docker-compose up`. If your shell is not currently in the directory containing docker-compose.yml, the command will fail. You also need to use linux containers, not windows containers for your docker installation.  
* If you receive an error `Drive has not been shared`, you will need to share your drive. Docker will prompt for this when it is required, but if you miss it, the setting is available under Docker's Settings > Shared Drives
* You should now see a variety of text outputs as the Docker Compose executes. Please note even if the final output reads `No web browser found: could not locate runnable browser`, the Jupyter notebooks are accessible via your host computer's browser.
* The Docker Jupyter instance is now running, and accessible in your computer’s web browser at: http://localhost/, with password  `secretpassword`. However, before we can use our Data Cube, we need to add some satellite data.
* Minimise the shell containing your running docker containers, then create a new shell instance by opening a new PowerShell window.
* As shown above, we:
 * Set up your local postgres database: `docker-compose exec jupyter datacube -v system init`
 * [Add the Landsat 8 dataset](https://datacube-core.readthedocs.io/en/latest/ops/indexing.html#loading-product-definitions), you need to grab the pathrows index. Download the file from [here](https://landsat.usgs.gov/sites/default/files/documents/WRS2_descending.zip) and save the zip file to `data/wrs2_descending.zip`
  * [_Index_](https://datacube-core.readthedocs.io/en/latest/ops/indexing.html#adding-data-indexing) the Landsat ls_usgs products: `docker-compose exec jupyter datacube product add /opt/odc/docs/config_samples/dataset_types/ls_usgs.yaml`
 * Index a default region with:
   * `docker-compose exec jupyter bash -c "cd /opt/odc/scripts && python3 ./autoIndex.py -p '/opt/odc/data/wrs2_descending.zip' -e '146.30,146.83,-43.54,-43.20'"`These commands initialise the database, and index the [AWS LandSat-8 PDS Product](https://docs.opendata.aws/landsat-pds/readme.html). 
* The LandSat-8 product requires the USGS Pathrows file, available above. Finally, autoIndex.py is used to index a particular region of the global product, with the region definable by the coordinates listed after the command is called.
* Once the download finishes and the prompt returns, it is okay to return to the Jupyter notebooks, at http://localhost on your host machine. You should now see several notebook files, which can be run and examined.


