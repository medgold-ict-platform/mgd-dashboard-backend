from warrant import Cognito, exceptions, AWSSRP
import requests
import os
import time
import boto3
import pytest
import sys
import json
import random
import time 
endpoint = os.environ['endpoint']
stype = ['index','indexavg','ecvavg','ecv']
sections = [{'Index':['index','indexavg'],'Ecv':['ecvavg','ecv'],'Risk':['index']}]
seas_sections = [{'Index':['index'],'Ecv':['ecv'],'Risk':['index']}]

ecv_stype = ['ecv', 'ecvavg']
index_stype = ['index', 'indexavg']
path = '../items/'

variables = {
    "Precipitation monthly":"tp",
    "Tmax monthly":"tmax",
    "Tmin monthly":"tmin",
    "Taverage monthly":"t2m",
    "GST":"GST",
    "Heat-Risk":"Heat_Risk",
    "HarvestR":"HarvestR",
    "SU35":"SU35",
    "SprR":"SprR",
    "WSDI":"WSDI",
    "Sanitary-Risk":"Sanitary_Risk",
    "GDD":"GDD",
    "sprtx":"sprtx",
}

#endpoint /index/match-all without params
def test_02_match_all_no_query_params():
    """Test index/match-all resource - Passing no params"""
    auth_token= os.environ['token']
    url = endpoint + "index/match-all"
    response = requests.request("GET", url=url, headers={"Authorization": auth_token})
    assert 'Missing required request parameters: [tab, year, stype, top_left, bottom_right, value]' in response.json()['message']

# endpoint /index/match-all no tab param
def test_03_match_all_no_tab_param():
    """Test index/match-all resource - Passing no [tab, year, stype, top_left, bottom_right, value] params"""
    auth_token= os.environ['token']
    url = endpoint + "index/match-all?var=''"
    response = requests.request("GET", url=url, headers={"Authorization": auth_token})
    assert 'Missing required request parameters: [tab, year, stype, top_left, bottom_right, value]' in response.json()['message']

# endpoint /index/match-all no stype param
def test_04_match_all_no_stype_param():
    """Test index/match-all resource - Passing no [year, stype, top_left, bottom_right, value] params"""
    auth_token= os.environ['token']
    path = "../items/"
    for file in os.listdir(path):
        with open(path+file) as f:
            data = json.load(f)
            #l.append(data['label'])
            url = endpoint + "index/match-all?tab={}".format(data['id'].replace('-','_').lower())
            response = requests.request("GET", url=url, headers={"Authorization": auth_token})
            assert 'Missing required request parameters: [year, stype, top_left, bottom_right, value]' in response.json()['message']

# endpoint /index/match-all no value param
def test_05_match_all_no_value_param():
    """Test index/match-all resource - Passing no [year, top_left, bottom_right, value] params"""
    auth_token= os.environ['token']
    path = "../items/"
    for file in os.listdir(path):
        with open(path+file) as f:
            data = json.load(f)
            for el in stype:
                url = endpoint + "index/match-all?tab={}&stype={}".format(data['id'].replace('-','_').lower(), el)
                response = requests.request("GET", url=url, headers={"Authorization": auth_token})
                assert 'Missing required request parameters: [year, top_left, bottom_right, value]' in response.json()['message']

# endpoint /index/match-all no year param
def test_06_match_all_no_year_param():
    """Test index/match-all resource - Passing no [year, top_left, bottom_right] params"""
    auth_token= os.environ['token']
    path = "../items/"
    for file in os.listdir(path):
        with open(path+file) as f:
            data = json.load(f)
            for sec in sections[0].keys():
                for el in stype:
                    try:
                        values = data[sec]['Name']
                    except Exception as e:
                        pass 
                    for value in values:
                        url = endpoint + "index/match-all?tab={}&stype={}&value={}".format(data['id'].replace('-','_').lower(), el, value)
                        response = requests.request("GET", url=url, headers={"Authorization": auth_token})
                        assert 'Missing required request parameters: [year, top_left, bottom_right]' in response.json()['message']
            

    
# endpoint /index/match-all no top_left param
def test_07_match_all_no_top_left():
    auth_token= os.environ['token']
    """Test index/match-all resource - Passing no [top_left, bottom_right] params"""
    path = "../items/"
    for file in os.listdir(path):
        with open(path+file) as f:
            data = json.load(f)
            for sec in sections[0].keys():
                for el in stype:
                    try:
                        values = data[sec]['Name']
                        year = random.randint(int(data[sec]['Timeline']['default']['start_date']),int(data[sec]['Timeline']['default']['end_date']))
                    except Exception as e:
                        pass  
                    for value in values:                    
                        url = endpoint + "index/match-all?tab={}&stype={}&value={}&year={}".format(data['id'].replace('-','_').lower(), el, value, year)
                        response = requests.request("GET", url=url, headers={"Authorization": auth_token})
                        assert 'Missing required request parameters: [top_left, bottom_right]' in response.json()['message']

# endpoint /index/match-all no bottom_right param
def test_08_match_all_no_bottom_right():
    """Test index/match-all resource - Passing no [bottom_right] params"""
    auth_token= os.environ['token']
    path = "../items/"
    for file in os.listdir(path):
        with open(path+file) as f:
            data = json.load(f)
            for sec in sections[0].keys():
                for el in sections[0][sec]:
                    top_left = "0"
                    year =0
                    try:
                        values = data[sec]['Name']
                        if data['id'].replace('-','_') != 'projection':
                            year = random.randint(int(data[sec]['Timeline']['default']['start_date']),int(data[sec]['Timeline']['default']['end_date']))
                            top_left = data[sec]['Timeline']['default']['top_left']
                        else:
                            year = data[sec]['Intervals'][0]
                            top_left = "41.99,-8.99"
                    except Exception as e:
                        pass
                    for value in values:
                        url = endpoint + "index/match-all?tab={}&stype={}&value={}&year={}&top_left={}".format(data['id'].replace('-','_').lower(), el, value, year, top_left)
                        response = requests.request("GET", url=url, headers={"Authorization": auth_token})
                        print(url)
                        assert 'Missing required request parameters: [bottom_right]' in response.json()['message']

# endpoint /index/match-all  
def test_09_match_all_climatology():
    """Test index/match-all resource - Climatology PTHRES dataset (Douro Valley)
        Testing for each year in range and a random month.
        
        tab: climatology

        Variables values: 
        - Climate: 
            values: ["Precipitation monthly","Tmax monthly","Tmin monthly","Taverage monthly"]
            stype: ['ecv', 'ecvavg']
        - Bioclimatic: 
            values: ["GST","HarvestR","SprR","SU35","WSDI"]
            stype: ['index', 'indexavg']
        - Wine Risk Indicators: 
            values: ["Heat Risk", "Sanitary Risk"]
            stype: ['index']

        top_left and bottom_right: bounding box coordinates

        url params Climate: "index/match-all?tab={}&stype={}&value={}&year={}&month={}&top_left={}&bottom_right={}"
        url params Bioclimatic and Wine Risk Indicators: "index/match-all?tab={}&stype={}&value={}&year={}&top_left={}&bottom_right={}"
    """
    auth_token= os.environ['token']
    path = "../items/"
    top_left = ""
    bottom_right = ""
    for file in os.listdir(path):
        with open(path+file) as f:
            if 'Climatology' in f.name:
                data = json.load(f)
                for sec in sections[0].keys():
                    for el in sections[0][sec]:
                        try:
                            f = 'Average' if 'avg' in el else 'default'
                            values = data[sec]['Name']
                            if f == 'Average':
                                years = data[sec]['Timeline'][f]['Intervals'][0]
                            else:
                                years = [i for i in range(int(data[sec]['Timeline'][f]['start_date']),int(data[sec]['Timeline']['default']['end_date']))]
                            for year in years:
                                top_left = data[sec]['Timeline']['default']['top_left']
                                bottom_right= data[sec]['Timeline']['default']['bottom_right']                      
                                for value in values:
                                    if data[sec]['Monthly']:
                                        month = str(random.randint(1,12)).zfill(2)
                                        url = endpoint + "index/match-all?tab={}&stype={}&value={}&year={}&month={}&top_left={}&bottom_right={}".format(data['id'].replace('-','_').lower(), el, value.replace(' ', '_').lower(), year, month, top_left, bottom_right)
                                        filter = "{}_{}_{}_{}".format(el, value, month, year)                                
                                    else:
                                        url = endpoint + "index/match-all?tab={}&stype={}&value={}&year={}&top_left={}&bottom_right={}".format(data['id'].replace('-','_').lower(), el, value.replace(' ', '_').lower(), year, top_left, bottom_right)
                                        filter = "{}_{}_{}".format(el, value, year)
                                    response = requests.request("GET", url=url, headers={"Authorization": auth_token})
                                    print(filter)
                                    response = response.json()[0]
                                    assert response != []
                                    assert filter.replace(value, variables[value]) == response['type']
                        except Exception as e:
                            print(filter)
                            print(response.json())
                            raise  

# endpoint /index/match-all  
def test_10_match_all_era5():
    """Test index/match-all resource - Climatology ERA5 dataset (Iberian Peninsula)
        Testing for each year in range and a random month.
        
        tab: era5

        Variables values: 
        - Climate: 
            values: ["Precipitation monthly","Tmax monthly","Tmin monthly","Taverage monthly"]
            stype = ['ecv', 'ecvavg']
        - Bioclimatic: 
            values: ["GST","HarvestR","SprR","SU35","WSDI"]
            stype: ['index', 'indexavg']
        - Wine Risk Indicators:
            values: ["Heat Risk", "Sanitary Risk"]
            stype: ['index']

        top_left and bottom_right: bounding box coordinates

        url params Climate: "index/match-all?tab={}&stype={}&value={}&year={}&month={}&top_left={}&bottom_right={}"
        url params Bioclimatic and Wine Risk Indicators: "index/match-all?tab={}&stype={}&value={}&year={}&top_left={}&bottom_right={}"
    """
    auth_token= os.environ['token']
    t = 'era5'
    path = "../items/"
    with open(path+'Climatology.json') as f:
        data = json.load(f)
        for sec in sections[0].keys():
            for el in sections[0][sec]:
                try:
                    f = 'Average' if 'avg' in el else 'era5'
                    values = data[sec]['Name']
                    if f == 'Average':
                        years = data[sec]['Timeline'][f]['Intervals']
                    else:
                        years = [i for i in range(int(data[sec]['Timeline'][f]['start_date']),int(data[sec]['Timeline']['default']['end_date'])+1)]
                    for year in years:
                        top_left = data[sec]['Timeline'][str(t)]['top_left']
                        bottom_right= data[sec]['Timeline'][str(t)]['bottom_right']                      
                        for value in values:
                            if data[sec]['Monthly']:
                                month = str(random.randint(1,12)).zfill(2)
                                url = endpoint + "index/match-all?tab={}&stype={}&value={}&year={}&month={}&top_left={}&bottom_right={}".format(t, el, value.replace(' ', '_').lower(), year, month, top_left, bottom_right)
                                filter = '{}_{}_{}_{}'.format(el, value, month, year)
                            else:
                                url = endpoint + "index/match-all?tab={}&stype={}&value={}&year={}&top_left={}&bottom_right={}".format(t, el, value.replace(' ', '_').lower(), year, top_left, bottom_right)
                                filter = '{}_{}_{}'.format(el, value, year)
                            print(filter)
                            response = requests.request("GET", url=url, headers={"Authorization": auth_token})
                            response = response.json()[0]
                            assert response != []
                            assert filter.replace(value, variables[value]).replace(' ','') == response['type']
                            time.sleep(2)
                except Exception as e:
                    print(e)
                    print(filter)
                    print(response)
                    raise 


def send_request(rcp, data, sec, el, value, year, auth_token, top_left, bottom_right):
    if data[sec]['Monthly']: 
        month = random.randint(1,12)   
        filter = '{}_{}_{}_rcp{}_{}'.format(el, variables[value], str(month).zfill(2), rcp, year)
        url = endpoint + "index/match-all?tab={}&stype={}&value={}&year={}&month={}&top_left={}&bottom_right={}&rcp={}".format(data['id'].replace('-','_').lower(), el, value.replace(' ', '_').lower(), year, month, top_left, bottom_right, rcp)
    else:
        filter = '{}_{}_rcp{}_{}'.format(el, variables[value], rcp, year)
        url = endpoint + "index/match-all?tab={}&stype={}&value={}&year={}&top_left={}&bottom_right={}&rcp={}".format(data['id'].replace('-','_').lower(), el, value.replace(' ', '_').lower(), year, top_left, bottom_right, rcp)
    if rcp == 0:
        filter = filter.replace('_rcp0','')
    print(filter)
    response = requests.request("GET", url=url, headers={"Authorization": auth_token})
    response = response.json()[0]
    assert response != []
    assert filter.replace(value, variables[value]) == response['type']

# # # endpoint /index/match-all  
def test_11_match_all_projection():
    """Test index/match-all resource - Projection
        Testing for each Interval and each month.
        
        tab: projection

        Variables values: 
        - Climate: 
            values: ["Precipitation monthly","Tmax monthly","Tmin monthly","Taverage monthly"] 
            stype: ['ecv', 'ecvanom']
            Intervals: ["1971-2000","2031-2060","2071-2100"]
            Monthly: yes
        - Bioclimatic: 
            values: ["GST","HarvestR","SprR","SU35","WSDI", "GDD"]
            stype = ['index', 'indexanom']
            Intervals: ["1971-2000","2031-2060","2071-2100"]
            Monthly: no

        RCP: ['8.5', '4.5']
        top_left and bottom_right: bounding box coordinates

        url params Climate: "index/match-all?tab={}&stype={}&value={}&year={}&month={}&top_left={}&bottom_right={}&rcp={}"
        url params Bioclimatic: "index/match-all?tab={}&stype={}&value={}&year={}&top_left={}&bottom_right={}&rcp={}"
    """
    auth_token= os.environ['token']
    path = "../items/"
    top_left = ""
    bottom_right = ""
    with open(path+'Projection.json') as f:
        data = json.load(f)
        for sec in sections[0].keys():
            if sec != 'Risk':
                for el in sections[0][sec]:
                    try:
                        top_left = data['top_left']
                        bottom_right= data['bottom_right']
                        values = data[sec]['Name']
                        for value in values: 
                            for year in data[sec]['Intervals']: 
                                if 'avg' in el or 'anom' in el: 
                                    el = el.replace('avg', 'anom')
                                if year in data['RCP']['Intervals']:
                                    for rcp in data['RCP']['Values'][0].values():
                                        send_request(rcp, data, sec, el,  value, year, auth_token, top_left, bottom_right)
                                elif 'avg' not in el and 'anom' not in el:
                                    send_request(0,data, sec, el,  value, year, auth_token, top_left, bottom_right)
                    except Exception as e:
                        print(filter)
                        print('projection')
                        raise


def send_request_s(url, value, filter):
    time.sleep(1)
    auth_token= os.environ['token']
    response = requests.request("GET", url=url, headers={"Authorization": auth_token})
    response = response.json()[0]
    assert response != []
    assert filter.replace(value, variables[value]).replace(' ','') == response['type']

# endpoint /index/match-all  
def test_12_match_all_seasonal_forecast():
    """Test index/match-all resource - Seasonal Forecast
        Testing for each Interval and a random month.
        
        tab: seasonal_forecast

        Variables values: 
        - Climate: 
            values: ["Precipitation monthly","Tmax monthly","Tmin monthly","Taverage monthly"] 
            stype: ['ecv']
            Monthly: yes
            leadt: [1, 2, 3, 4]
        - Bioclimatic: 
            values: ["GST","HarvestR","SprR","sprtx"]
            stype = ['index']
            leadt: [2, 4]
            Monthly: no
        - Wine Risk Indicators:
            values: ["Sanitary Risk"]
            stype = ['index']
            leadt: [2, 4]
            Monthly: no

        top_left and bottom_right: bounding box coordinates

        url params Climate: "index/match-all?tab={}&stype={}&value={}&year={}&top_left={}&bottom_right={}&leadt={}&month={}"
        url params Bioclimatic and Wine Risk Indicators: "index/match-all?tab={}&stype={}&value={}&year={}&top_left={}&bottom_right={}&leadt={}"
    """
    t = 'seasonal_forecast'
    with open(path+'Seasonal-Forecast.json') as f:
        data = json.load(f)
        for sec in seas_sections[0].keys():
            for el in seas_sections[0][sec]:
                filter=""
                try:
                    values = data[sec]['Name']
                    for value in values:
                        top_left = data[sec]['Timeline']['default']['top_left']
                        bottom_right= data[sec]['Timeline']['default']['bottom_right']                      
                        if 'index' in el:
                            for var in data[sec]['Timeline'][value]:
                                for year in range(int(data[sec]['Timeline'][value][var]['start_date']),int(data[sec]['Timeline'][value][var]['end_date'])+1):
                                    leadt = data[sec]['Timeline'][value][var]['leadt']
                                    url = endpoint + "index/match-all?tab={}&stype={}&value={}&year={}&top_left={}&bottom_right={}&leadt={}".format(t, el, value.replace(' ', '').lower(), year, top_left, bottom_right, leadt)
                                    filter = '{}_{}_{}_stdt_{}'.format(el, value.replace(' ', ''), year, leadt)
                                    print(filter)
                                    send_request_s(url, value, filter)
                        else:
                            for year in range(int(data[sec]['Timeline']['default']['start_date']),int(data[sec]['Timeline']['default']['end_date'])):
                                for leadt in data[sec]['leadtime']:
                                    leadt = int(leadt) + 1
                                    if year == int(data[sec]['Timeline']['default']['end_date']):
                                        month = random.randint(int(data[sec]['Timeline']['default']['sm_ed']),int(data[sec]['Timeline']['default']['em_ed']))
                                    else:
                                        month = random.randint(1,12) 
                                    if year == int(data[sec]['Timeline']['default']['start_date']):
                                        month = 4
                                    url = endpoint + "index/match-all?tab={}&stype={}&value={}&year={}&top_left={}&bottom_right={}&leadt={}&month={}".format(t, el, value.replace(' ', '_').lower(), year, top_left, bottom_right, leadt, month)
                                    filter = '{}_{}_{}_{}_leadt_{}'.format(el, variables[value], str(month).zfill(2), year, leadt)
                                    send_request_s(url, value, filter)
                                    print(filter)
                except Exception as e:
                    print(filter)
                    print(e)
                    raise

# # endpoint index/match-location climatology
def test_13_match_location_climatology():
    """Test index/match-location resource - Climatology PTHRES dataset (Douro Valley)
        Testing for a random month.
        
        tab: climatology

        Variables values: 
        - Climate: 
            values: ["Precipitation monthly","Tmax monthly","Tmin monthly","Taverage monthly"]
            stype: ['ecv']
            Monthly: yes
        - Bioclimatic: 
            values: ["GST","HarvestR","SprR","SU35","WSDI"]
            stype: ['index']
            Monthly: no
        - Wine Risk Indicators: 
            values: ["Heat Risk", "Sanitary Risk"]
            stype: ['index']
            Monthly: no

       location: point inside bounding box

        url params Climate:  "index/match-location?tab={}&stype={}&value={}&month={}&location={}"
        url params Bioclimatic and Wine Risk Indicators: "index/match-location?tab={}&stype={}&value={}&location={}"
    """
    loc_indexes = ['harvestr', 'sprr', 'precipitation_monthly', 'sanitary_risk']
    auth_token= os.environ['token']
    path = "../items/"
    with open(path+'Climatology.json') as f:
        data = json.load(f)
        for sec in sections[0].keys():
            for el in seas_sections[0][sec]:
                values = data[sec]['Name']
                for value in values:
                    try:
                        if 'avg' not in el:
                            if value.replace(' ', '_').lower() in loc_indexes:
                                location = "40,-9"
                            else:
                                location = "40.005,-8.985"
                            if data[sec]['Monthly']:
                                month = str(random.randint(1,12)).zfill(2)
                                url = endpoint + "index/match-location?tab={}&stype={}&value={}&month={}&location={}".format(data['id'].replace('-','_').lower(), el, value.replace(' ', '_').lower(), month, location)
                            else:
                                url = endpoint + "index/match-location?tab={}&stype={}&value={}&location={}".format(data['id'].replace('-','_').lower(), el, value.replace(' ', '').lower(),location)
                            response = requests.request("GET", url=url, headers={"Authorization": auth_token})
                            print(value.replace(' ', '_').lower())
                            print(url)
                            response = response.json()[0]
                            assert response != []  
                            time.sleep(1)
                    except Exception as e:
                        raise

# # endpoint index/match-location/seasonal_forecast 
def test_14_match_location_seasonal():
    """Test index/match-location/seasonal_forecast resource - Seasonal Forecast
        Testing for a random month.
        
        tab: climatology

        Variables values: 
        - Climate: 
            values: ["Precipitation monthly","Tmax monthly","Tmin monthly","Taverage monthly"] 
            stype: ['ecv']
            Monthly: yes
            leadt: [1, 2, 3, 4]
        - Bioclimatic: 
            values: ["GST","HarvestR","SprR","sprtx"]
            stype = ['index']
            leadt: [2, 4]
            Monthly: no
        - Wine Risk Indicators:
            values: ["Sanitary Risk"]
            stype = ['index']
            leadt: [2, 4]
            Monthly: no

       location: point inside bounding box

        url params Climate:  "index/match-location/seasonal_forecast?tab={}&stype={}&value={}&month={}&location={}&leadt={}"
        url params Bioclimatic and Wine Risk Indicators: "index/match-location/seasonal_forecast?tab={}&stype={}&value={}&location={}&leadt={}"
    """
    loc_indexes = ['harvestr', 'sprr', 'precipitation_monthly', 'sanitary_risk']
    auth_token= os.environ['token']
    path = "../items/"
    with open(path+'Seasonal-Forecast.json') as f:
        data = json.load(f)
        for sec in sections[0].keys():
            for el in seas_sections[0][sec]:
                values = data[sec]['Name']
                for value in values:
                    try:
                        if 'avg' not in el:
                            location = "40,-7"
                            if 'index' in el:
                                for var in data[sec]['Timeline'][value]:
                                    leadt = data[sec]['Timeline'][value][var]["leadt"]
                                    url = endpoint + "index/match-location/seasonal_forecast?tab={}&stype={}&value={}&location={}&leadt={}".format(data['id'].replace('-','_').lower(), el, value.replace(' ','_').lower(),location, leadt)
                                    response = requests.request("GET", url=url, headers={"Authorization": auth_token})
                                    response = response.json()[0]
                                    assert response != [] 
                                    time.sleep(1)
                            else:
                                for leadt in data[sec]['leadtime']:
                                    leadt = int(leadt) + 1
                                    month = 4
                                    url = endpoint + "index/match-location/seasonal_forecast?tab={}&stype={}&value={}&month={}&location={}&leadt={}".format(data['id'].replace('-','_').lower(), el, value.replace(' ', '_').lower(), month, location, leadt)
                                    response = requests.request("GET", url=url, headers={"Authorization": auth_token})
                                    response = response.json()[0]
                                    assert response != [] 
                                    time.sleep(1)
                    except Exception as e:
                        print(e)
                        print(url)
                        raise