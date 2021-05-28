from elasticsearch import Elasticsearch, RequestsHttpConnection
import os
import json
import boto3
import sys 

elastic_endpoint = os.environ['ES_ENDPOINT']
path = '{}/{}/{}/{}/{}'
cwd = os.getcwd()
index = '{}_{}_{}_{}'
variables = {
    "precipitation_monthly":"tp",
    "tmax_monthly":"tmax",
    "tmin_monthly":"tmin",
    "taverage_monthly":"t2m",
    "gst":"gst",
    "heat_risk":"heatrisk",
    "harvestr":"harvestr",
    "su35":"su35",
    "su36":"su36",
    "su40":"su40",
    "spr32":"spr32",
    "sprr":"sprr",
    "wsdi":"wsdi",
    "sanitary_risk":"sanitaryrisk",
    "gdd":"gdd",
    "sprtx":"sprtx"
}

def connect():
    print ('Connecting to the ES Endpoint {0}'.format(elastic_endpoint))
    try:
        esClient = Elasticsearch(
            hosts=[{'host': elastic_endpoint, 'port': 443, 'use_ssl':True}],
            timeout=30
        )
        return esClient
    except Exception as E:
        print("Unable to connect to {0}".format(elastic_endpoint))
        print(E)
        exit(3)

def process_hits(hits, values, index):
    for item in hits:
        if index == 'seasonal_forecast':
            mydoc = {
                "type": item['_source']['type'],
                "location":'{},{}'.format(item['_source']['location'][1],item['_source']['location'][0]),
                "value": item['_source']['value'],
                "rpss": item['_source']['rpss']
            }
        else:
            mydoc = {
                "type": item['_source']['type'],
                "location":'{},{}'.format(item['_source']['location'][1],item['_source']['location'][0]),
                "value": item['_source']['value']
            }
        values.append(mydoc)
    return values

def match_all_index(event,context):
    values = []
    region =''
    path_type = '{}_{}_{}'
    es = connect()
    try:
        par = event["queryStringParameters"]
        index = par["tab"]
        stype = par["stype"]
        value = variables[par["value"]]
        year = par["year"]
        top_left = par['top_left'].split(',')
        bottom_right = par['bottom_right'].split(',')
        if 'ecv' in stype:
            value = variables[par["value"]]
            month = '{}'.format(par["month"].zfill(2))
            if index == 'climatology' or index == 'era5':
                if stype == 'ecvavg':
                    path_type = '{}_{}_{}_{}*'
                    year = year.split('-')[0]
                else:
                    path_type = '{}_{}_{}_{}'
                path_type = path_type.format(stype, value, month, year)
            else:
                if index == 'seasonal_forecast':
                    path_type = '{}_{}_{}_{}_leadt_{}'.format(stype, value, month, year, par["leadt"])
                else:
                    region = event["queryStringParameters"]['region']
                    if year != '1971-2000':
                        rcp = par["rcp"] 
                        path_type = '{}_{}_{}_rcp{}_{}'.format(stype, value, month, rcp, year.split('-')[0]+'*')
                    else:
                        path_type = '{}_{}_{}_{}'.format(stype, value, month, year.split('-')[0]+'*')
        else:
            if index == 'climatology' or index == 'era5':
                if stype == 'indexavg':
                    path_type = '{}_{}_{}*'.format(stype, value, year.split('-')[0])
                else:
                    path_type = '{}_{}_{}'.format(stype, value, year)
            else:
                if index == 'seasonal_forecast':
                    path_type = '{}_{}_{}_stdt_{}'.format(stype, value, year, par["leadt"])
                else:
                    region = event["queryStringParameters"]['region']
                    if year != '1971-2000':
                        path_type = '{}_{}_rcp{}_{}'.format(stype, value,par["rcp"],year.split('-')[0]+'*')
                    else:
                        path_type = '{}_{}_{}'.format(stype, value, year.split('-')[0]+'*')
        print(path_type)
    except Exception as e:
        return {
            'statusCode': 404,
            'body': json.dumps({"Message": str(e)}),
            "headers": {
                "Access-Control-Allow-Origin": '*'
            }
        }
    
    body = {"query": {
            "bool" : {
                "must" : [{
                    "match" : {
                        "type": path_type
                    }
                }],
                "filter" : {
                    "geo_bounding_box" : {
                        "location" : {
                            "top_left" : {
                                "lat" : float(top_left[0]),
                                "lon" : float(top_left[1])
                            },
                            "bottom_right" : {
                                "lat" : float(bottom_right[0]),
                                "lon" : float(bottom_right[1])
                            }
                        }
                    }
                }
            }
        }
    }

    if region != '':
        new_match = {
          "match" : {
                "region": region
            }  
        }
        body['query']['bool']['must'].append(new_match)

    print(body)
    try:
        data = es.search(index=index, body=body,scroll = '2m', size=10000)
        sid = data['_scroll_id']
        scroll_size = len(data['hits']['hits'])
        print(data)
        while scroll_size > 0:
            # Before scroll, process current batch of hits
            values = process_hits(data['hits']['hits'], values, index)
            data = es.scroll(scroll_id=sid, scroll='2m')
            # Update the scroll ID
            sid = data['_scroll_id']
            # Get the number of results that returned in the last scroll
            scroll_size = len(data['hits']['hits'])
        if len(values) == 0:
            raise Exception('Data not available, check the passed parameters')
    except Exception as e:
        print(e)
        return {
            'statusCode': 404,
            'body': json.dumps({"Message": str(e)}),
            "headers": {
                "Access-Control-Allow-Origin": '*'
            }
        }

    return {
            'statusCode': 200,
            'body': json.dumps(values),
            "headers": {
                "Access-Control-Allow-Origin": '*'
            }
    }
