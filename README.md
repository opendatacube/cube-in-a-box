# Cuborizonte in a Box

The Cube in a Box is a simple way to run the [Open Data Cube](https://www.opendatacube.org).

## Setup:

  * If the above fails you can follow the following steps:
    1. `docker-compose up`
    2. When the a message like: `No web browser found: could not locate runnable browser` shows. Open a new shell and run the next commands
    3. `docker-compose exec jupyter datacube -v system init`
    4. `docker-compose exec jupyter datacube product add https://raw.githubusercontent.com/DiegoHMM/cuborizonte_products/main/product_aerial_image_1999.yaml`

5. You should now be able to go to <http://localhost>
6. Enter the password `secretpassword`
