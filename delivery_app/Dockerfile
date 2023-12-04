FROM python:3.10-slim
# This is where we'll put the requirements.txt file and the app directory.
WORKDIR /code

##
# As this file doesn't change often, Docker will detect it and use the cache for this step,
# enabling the cache for the next step too.
##
COPY delivery/requirements.txt /code/requirements.txt
##
# The --no-cache-dir option tells pip to not save the downloaded packages locally,
# as that is only if pip was going to be run again to install the same packages,
# but that's not the case when working with containers.
##
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

##
# As this has all the code which is what changes most frequently
# the Docker cache won't be used for this or any following steps easily.
#
# So, it's important to put this near the end of the Dockerfile,
# to optimize the container image build times.
##
COPY delivery/app /code/app

##
# Run application using uvicorn server
##
#ENTRYPOINT uvicorn --host 0.0.0.0 --port 80 --log-config ${LOG_CONFIG_FILENAME} app.main:app
ENTRYPOINT uvicorn --host 0.0.0.0 --port 443 --log-config ${LOG_CONFIG_FILENAME} --ssl-keyfile /code/certs/fastapi.key --ssl-certfile /code/certs/fastapi.crt app.main:app

