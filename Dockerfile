# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.10-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.10

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

RUN apt-get update ; \
    apt-get upgrade -y ; \
    apt install curl -y 

# TODO build GCC FROM sources to fix missing dependecy on Debian 11
# OSError: /usr/lib/x86_64-linux-gnu/libstdc++.so.6: version `GLIBCXX_3.4.29' not found (required by /usr/local/lib/python3.10/site-packages/gpt4all/llmodel_DO_NOT_MODIFY/build/libllmodel.so)
# or wait for Microsoft to update base image OS to Debian 12

COPY requirements.txt /

RUN pip install --upgrade pip && \
    pip install -r /requirements.txt


COPY . /home/site/wwwroot

