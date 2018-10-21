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

# Detailed Install Instructions
## Detailed Docker Install Instructions
If you are unfamiliar with Docker or Jupyter, this guide will take you through downloading Docker to setting up a Cube in a Box Jupyter Server running the Open Data Cube. While these instructions specifically suit windows, the steps can easily be adapted for other a different OS, using a Terminal instead of PowerShell, and the appropriate Docker version.

* First, [download Docker for Windows](https://docs.docker.com/docker-for-windows/install/).
In Windows, we can use PowerShell to interact with the Docker command line. Please note, PowerShell ISE will not work.
* Next, download the [Data Cube setup files and code](https://github.com/LSgeo/opendatacube-cloudformation-testing/archive/master.zip) from the above repository and unzip into a local folder of your choice. Navigate to this folder in PowerShell using the cd command, e.g. 'cd C:/cubeinabox/'. Don't forget, you can use tab to complete, and dir to display the contents of the current folder.
* Follow [Docker's Orientation](https://docs.docker.com/get-started/) to familiarise yourself with Docker. At the end, you should be able to run `docker info` to view your installation details. These details can help troubleshoot a Docker installation.
* Now, we are going to create and run the Docker Container for our CIAB install. 
* In your folder containing the downloaded CIAB files, enter the command `docker-compose up`. If your shell is not currently in the directory containing docker-compose.yml, the command will fail. You also need to use Linux containers, not windows containers for your docker installation.  
* If you receive an error `Drive has not been shared`, you will need to share your drive. Docker will prompt for this when it is required, but if you miss it, the setting is available under Docker's Settings > Shared Drives
* You should now see a variety of text outputs as the Docker Compose executes. Please note even if the final output reads `No web browser found: could not locate runnable browser`, the Jupyter notebooks are accessible via your host computer's browser.
* The Docker Jupyter instance is now running, and accessible in your computer’s web browser at: http://localhost/, with password `secretpassword`. However, before we can use our Data Cube, we need to add some satellite data.
* Minimise the shell containing your running docker containers, then create a new shell instance by opening a new PowerShell window.
* As shown above, we:
  * Set up a local postgres database: `docker-compose exec jupyter datacube -v system init`
  * [Address the Landsat 8 data], using the pathrows file. Download the file from [the USGS Landsat site](https://landsat.usgs.gov/sites/default/files/documents/WRS2_descending.zip) and save the zip file to `/data/wrs2_descending.zip` on your local machine. This folder is mounted within the Docker container, and can be used to share files between your host machine and the container.
   * [Add the Landsat ls_usgs _Product Definition_](https://datacube-core.readthedocs.io/en/latest/ops/indexing.html#product-definition): `docker-compose exec jupyter datacube product add /opt/odc/docs/config_samples/dataset_types/ls_usgs.yaml`
   * [_Index_](https://datacube-core.readthedocs.io/en/latest/ops/indexing.html#adding-data-indexing) a default region with:
   * `docker-compose exec jupyter bash -c "cd /opt/odc/scripts && python3 ./autoIndex.py -p '/opt/odc/data/wrs2_descending.zip' -e '146.30,146.83,-43.54,-43.20'"`This commands indexes the [AWS LandSat-8 PDS Product](https://docs.opendata.aws/landsat-pds/readme.html). for a particular region of the global product, with the region definable by the coordinates listed.
* Once the download finishes and the prompt returns, it is okay to return to the Jupyter notebooks, at http://localhost on your host machine. You should now see several notebook files, which can be run and examined.

If you want to make changes within the docker container, the underlying Linux terminal is accessible by executing `docker-compose exec jupyter bash` in PowerShell. This will start a terminal session within the container, where you can execute Linux commands to install additional packages, etc. 
It is also possible to use [IPython Magic Commands](https://ipython.readthedocs.io/en/stable/interactive/magics.html) to execute some bash commands from within a Notebook. Use `%% Bash` at the top of a cell, and that cell will execute commands to the terminal. Not all commands work, however pip will function to install and update python packages.

## Detailed Amazon Web Services (AWS) Install Instructions
If you are unfamiliar with AWS, this detailed guide can help you set up an AWS account, and create the necessary AWS components using the provided template from the [Magic Link](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=cube-in-a-box&templateURL=https://s3-ap-southeast-2.amazonaws.com/cubeinabox/opendatacube-test.yml) as above.
* First you will need an AWS account. While a 12 month free trail to several different AWS products is available, the computing power offered by the trial remote server is not enough to run demonstration ODC products. The cheapest option is currently a `t2.small` EC2 server, which will cost approximately $10 USD per month, if left running for the entire month.
* Sign up for an [AWS account](https://portal.aws.amazon.com/billing/signup#/start). The account that is created is known as a root account. It has access to every capability of AWS, including your billing information.
* To follow recommended security practice, [you should first create an Administrator IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started_create-admin-group.html) for your main log-in account, which limits only access to billing and other large administrative policy changes. 
* The procedure listed in the above link will take you through creating the Administrator account, and when done, you should [log in as the Administrator](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started_how-users-sign-in.html).
* `It is now possible to begin testing CIAB immediately using the Administrator account. However, in a production ready environment, it would be best to create a second IAM account with access restricted to only the required functions of AWS. This part of the guide is a Work In Progress.`
* To access your Cube in a Box, you will need a set of EC2 SSH keys. __Keys are region specific, so you must ensure your region when creating the CIAB is the same as the region used when creating the Keys.__ As the LS8 PDS is on US-West-2 Oregon, it is suggested you create your CIAB and keys on US-West-2 (Oregon) to facilitate fast loading of scenes. Change the region in the upper left dropdown.
* Navigate to the EC2 service management page, and create a new Key Pair `https://us-west-2.console.aws.amazon.com/ec2/v2/home?region=us-west-2#KeyPairs`. The name of the key pair will be specified during the CIAB installation. Save the output .pem in a secure location.
* You are now ready to launch the [CIAB Magic URL](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=cube-in-a-box&templateURL=https://s3-ap-southeast-2.amazonaws.com/cubeinabox/opendatacube-test.yml), which navigates you to the CloudFormation Service, with a predefined template ready to launch.
* The only detail you specifically need to select is the KeyName on page 2. Using the drop down, select the key name you specified earlier. 
* It is also recommended to change the SecretPassword, which will be used to log in to your Jupyter server. You may also choose a different EC2 Server type, with [costs listed here](https://aws.amazon.com/ec2/pricing/on-demand/). Please ensure US West (Oregon) is selected to get correct pricing.
* Finally on page 2, change the ExtentToIndex to a small (1 degree x 1 degree or less) demonstration area. It is easy to add different or larger extents after familiarising yourself with the Open Data Cube.
* No other settings are required to be changed, so you may click through, acknowledge the IAM resources notification, and Create your resource Stack. 
* If these are successful, you will be taken to the Stack manager. Note the Filter “Active” option can be changed to see In Progress or Failed stacks.
* Click on the “Outputs” tab to see the publicDNS of your EC2 server, which can be navigated to in your browser. This contains your Jupyter server. It may take a minute or two for Jupyter to prepare itself (no more than 5 minutes). Your password will be the secretpassword you set earlier, or simply `secretpassword`.

You should now see several notebook files, which can be run and examined.
