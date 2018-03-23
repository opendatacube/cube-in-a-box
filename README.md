# opendatacube-cloudformation-testing
 
# Some notes:
 * Start the thing with `make up`
 * Index a default region with `make index`
 * Edit the Makefile to change the region of interest

Todo:
 * Make sure indexing works
 * Set up notebooks that work on indexed data
 * Get this working on AWS

Deploying to AWS:
 * To deploy to AWS, you need the AWS command line installed
 * Then do `make create-infra`
 * If you want to change the stack, you can do `make update-infra`
 * You may not want to update the stack though, as the DB will still be there and it'll get messy. Maybe destroy and re-create.


# IMPORTANT NOTES
To be able to get data from S3, you need to ensure that the environment variables `ODC_ACCESS_KEY` and `ODC_SECRET_KEY` are set to something valid.