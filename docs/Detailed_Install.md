# Detailed Install Instructions

For most people running the `setup.sh` script will do all the below (except for Windows installs)

## Detailed Docker Install Instructions

1. Install Docker, and install Docker Compose.
  * Select your current OS from here [Install Docker](https://docs.docker.com/engine/install/) **Note that we currently do not support ARM machines**
  * For Windows and Mac OS X, docker compose comes with Docker Desktop.
  * For Windows make sure that you can run Linux containers.
2. Get the code for this repository here: [Git ZIP file](https://github.com/opendatacube/cube-in-a-box/archive/refs/heads/main.zip)
3. Extract the above ZIP file and go to that directory.
  * For Windows you will need to use PowerShell, by using the `cd` and `dir` commands, for example `cd C:/cubeinabox`.
  * For other OS's you can use your current shell.
4. Depnding on your system you can try one of the following commands:
  * First try running `make setup`, which will try setup everything on your machine.
    * On Mac the first time you try this it should request for you to install some tools.
    * On Windows this might not work at all, in which case you can continue to the next set of instructions.
    * On Linux this can be fixed by installing the make tools
  * If the above fails you can follow the following steps:
    1. `docker-compose up`
    2. When the a message like: `No web browser found: could not locate runnable browser` shows. Open a new shell and run the next commands
    3. `docker-compose exec jupyter datacube -v system init`
    4. `docker-compose exec jupyter datacube product add https://raw.githubusercontent.com/digitalearthafrica/config/master/products/esa_s2_l2a.odc-product.yaml`
    4. `docker-compose exec jupyter bash -c "stac-to-dc --bbox='25,20,35,30' --collections='sentinel-s2-l2a-cogs' --datetime='2020-01-01/2020-03-31'"`
5. You should now be able to go to <http://localhost>
6. Enter the password `secretpassword`


### Known Errors:

* On Windows if you receive the error `Drive has not been shared` then you need to change this setting in Docker Settings > Shared Drives

## Detailed Amazon Web Services (AWS) Install Instructions
If you are unfamiliar with AWS, this detailed guide can help you set up an AWS account, and create the necessary AWS components using the provided template from the [Magic Link](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=cube-in-a-box&templateURL=https://s3-ap-southeast-2.amazonaws.com/cubeinabox/opendatacube-test.yml) as above.
* First you will need an AWS account. While a 12 month free trail to several different AWS products is available, the computing power offered by the trial remote server is not enough to run demonstration ODC products. The cheapest option is currently a `t2.small` EC2 server, which will cost approximately $10 USD per month, if left running for the entire month.
* Sign up for an [AWS account](https://portal.aws.amazon.com/billing/signup#/start). The account that is created is known as a root account. It has access to every capability of AWS, including your billing information.
* To follow recommended security practice, [you should first create an Administrator IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started_create-admin-group.html) for your main log-in account, which limits only access to billing and other large administrative policy changes.
* The procedure listed in the above link will take you through creating the Administrator account, and when done, you should [log in as the Administrator](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started_how-users-sign-in.html).
* _It is now possible to begin testing CIAB immediately using the Administrator account. However, in a production ready environment, it would be best to create a second IAM account with access restricted to only the required functions of AWS. This part of the guide is a Work In Progress_.
* To access your Cube in a Box, you will need a set of EC2 SSH keys. __Keys are region specific, so you must ensure your region when creating the CIAB is the same as the region used when creating the Keys.__ As the LS8 PDS is on US-West-2 Oregon, it is suggested you create your CIAB and keys on US-West-2 (Oregon) to facilitate fast loading of scenes. Change the region in the upper right dropdown.
* Navigate to the [EC2 service management page, and create a new Key Pair](https://us-west-2.console.aws.amazon.com/ec2/v2/home?region=us-west-2#KeyPairs). The name of the key pair will be specified during the CIAB installation. Save the output .pem in a secure location.
* You are now ready to launch the [CIAB Magic URL](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=cube-in-a-box&templateURL=https://s3-ap-southeast-2.amazonaws.com/cubeinabox/opendatacube-test.yml), which navigates you to the CloudFormation Service, with a predefined template ready to launch.
* The only detail you specifically need to select is the KeyName on page 2. Using the drop down, select the key name you specified earlier.
* It is also recommended to change the SecretPassword, which will be used to log in to your Jupyter server. You may also choose a different EC2 Server type, with [costs listed here](https://aws.amazon.com/ec2/pricing/on-demand/). Please ensure US West (Oregon) is selected to get correct pricing.  The R series of memory optimised instances [listed here](https://aws.amazon.com/ec2/instance-types/#Memory_Optimized) is a good starting point to look at for heavier workloads.  Previous versions are [listed here](https://aws.amazon.com/ec2/previous-generation/)
* Finally on page 2, change the ExtentToIndex to a small (1 degree x 1 degree or less) demonstration area. It is easy to add different or larger extents after familiarising yourself with the Open Data Cube.
* No other settings are required to be changed, so you may click through, acknowledge the IAM resources notification, and Create your resource Stack.
* If these are successful, you will be taken to the Stack manager. Note the Filter “Active” option can be changed to see In Progress or Failed stacks.
* Click on the “Outputs” tab to see the publicDNS of your EC2 server, which can be navigated to in your browser. This contains your Jupyter server. It may take a minute or two for Jupyter to prepare itself (no more than 5 minutes). Your password will be the secretpassword you set earlier, or simply `secretpassword`.

You should now see several notebook files, which can be run, edited and examined.
