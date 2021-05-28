from warrant import Cognito, exceptions, AWSSRP
import requests
import os
import boto3
import pytest
import json
import sys
from collections import OrderedDict 
import subprocess

endpoint = os.environ["endpoint"]
sections = ['Index', 'Ecv', 'Risk']

@pytest.fixture(scope="session", autouse=True)
def test_00():
    """Get authentication token """
    username = os.environ['username']
    password = os.environ['password']
    print(username)
    print(password)
    awssrp = AWSSRP(username, password, "eu-west-1_owfEtSFcp", pool_region="eu-west-1",client_id="7efjel0mg7qrjrvgb19dr3ooff")
    try:
        response=awssrp.authenticate_user(password)
    except exceptions.ForceChangePasswordException:
        awssrp=AWSSRP(username, password, "eu-west-1_owfEtSFcp", pool_region="eu-west-1", client_id="7efjel0mg7qrjrvgb19dr3ooff")
        awssrp.set_new_password_challenge(new_password=password)
        response = awssrp.authenticate_user(password)
    print(response["AuthenticationResult"]["IdToken"])
    os.environ['token'] = response["AuthenticationResult"]["IdToken"]

# endpoint /ids
def test_02_get_ids():
    """Test /ids resource that returns all id in {stage}-mgd-dashboard dynamoDB table"""
    auth_token= os.environ['token']
    url = endpoint + "ids"
    l = []
    response = requests.request("GET", url=url, headers={"Authorization": auth_token})
    path = "../items/"
    for file in os.listdir(path):
        with open(path+file) as f:
            data = json.load(f)
            l.append(data['label'])
    print(response.json())
    for el in response.json():
        assert el['label'] in l

# endpoint /{id}/info   
def test_03_get_info():
    """Test {id}/info resource that returns all information about a tab {Climatology, Projection or Seasonal Forecast}"""
    auth_token= os.environ['token']
    l = []
    path = "../items/"
    for file in os.listdir(path):
        with open(path+file) as f:
            data = json.load(f)
            l.append(data['id'])
            url = endpoint + "{}/info".format(data['id'])
            response = requests.request("GET", url=url, headers={"Authorization": auth_token})
            try:
                response = response.json()[0][sec]
                for sec in sections:
                    assert response == data[sec]
            except:
                pass

# endpoint /all
def test_04_get_all():
    """Test /all resource that returns all items in {stage}-mgd-dashboard"""
    auth_token= os.environ['token']
    l = []
    path = "../items/"
    url = endpoint + "all"
    for file in os.listdir(path):
        with open(path+file) as f:
            data = json.load(f)
            l.append(data)
            response = requests.request("GET", url=url, headers={"Authorization": auth_token})
    for el in response.json():
        assert el in l
