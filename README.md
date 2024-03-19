# Wishlist

## Usage

You will need python and pip. First, create a virtual environment.

    python -m venv venv

Activate the virtual environment and install requirements with pip.

    source venv/bin/activate
    pip install -r requirements.txt


Then, using docker or podman, start a mongodb container.

    docker run -p 27017:27017 -d mongo

Start the application with the flask CLI.

    flask run

You can also add the `--debug` flag for automatic reloading and debugging.