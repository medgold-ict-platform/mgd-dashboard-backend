import os
import json
import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection

elastic_endpoint = os.environ['ES_ENDPOINT']
path = '{}/{}/{}/{}/{}'
cwd = os.getcwd()
index = '{}_{}_{}_{}'

# variables = {
#     "precipitation_monthly":["tp",['#f7fbff','#deebf7','#c6dbef','#9ecae1','#6baed6','#4292c6','#2171b5','#08519c','#08306b']],
#     "tmax_monthly":["tmax",['#ffffcc','#ffeda0','#fed976','#feb24c','#fd8d3c','#fc4e2a','#e31a1c','#bd0026','#800026']],
#     "tmin_monthly":["tmin",['#f7f4f9','#e7e1ef','#d4b9da','#c994c7','#df65b0','#e7298a','#ce1256','#980043','#67001f']],
#     "taverage_monthly":["t2m",['#fff5eb','#fee6ce','#fdd0a2','#fdae6b','#fd8d3c','#f16913','#d94801','#a63603','#7f2704']],
#     "gst":["gst",['#ffffcc','#ffeda0','#fed976','#feb24c','#fd8d3c','#fc4e2a','#e31a1c','#bd0026','#800026']],
#     "heat_risk":["heatrisk",['#006837','#1a9850', '#66bd63', '#a6d96a', '#d9ef8b', '#ffcc33', '#fee08b', '#fdae61', '#d73027', '#a50026']],
#     "harvestr":["harvestr",['#f7fbff','#deebf7','#c6dbef','#9ecae1','#6baed6','#4292c6','#2171b5','#08519c','#08306b']],
#     "su35":["su35",['#ffffcc','#ffeda0','#fed976','#feb24c','#fd8d3c','#fc4e2a','#e31a1c','#bd0026','#800026']],
#     "sprr":["sprr",['#f7fbff','#deebf7','#c6dbef','#9ecae1','#6baed6','#4292c6','#2171b5','#08519c','#08306b']],
#     "wsdi":["wsdi",['#ffffcc','#ffeda0','#fed976','#feb24c','#fd8d3c','#fc4e2a','#e31a1c','#bd0026','#800026']],
#     "sanitary_risk":["sanitaryrisk",['#006837','#1a9850', '#66bd63', '#a6d96a', '#d9ef8b', '#ffcc33', '#fee08b', '#fdae61', '#d73027', '#a50026']],
#     "gdd":["gdd",['#ffffcc','#ffeda0','#fed976','#feb24c','#fd8d3c','#fc4e2a','#e31a1c','#bd0026','#800026']],
#     "sprtx":["sprtx",['#ffffcc','#ffeda0','#fed976','#feb24c','#fd8d3c','#fc4e2a','#e31a1c','#bd0026','#800026']],

# }

variables = {
    "precipitation_monthly":["tp",['#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000']],
    "tmax_monthly":["tmax",['#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000']],
    "tmin_monthly":["tmin",['#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000']],
    "taverage_monthly":["t2m",['#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000']],
    "gst":["gst",['#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000']],
    "heat_risk":["heatrisk",['#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000']],
    "harvestr":["harvestr",['#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000']],
    "su35":["su35",['#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000']],
    "sprr":["sprr",['#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000']],
    "wsdi":["wsdi",['#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000']],
    "sanitary_risk":["sanitaryrisk",['#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000']],
    "gdd":["gdd",['#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000']],
    "su36":["su36",['#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000']],
    "su40":["su40",['#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000']],
    "spr32":["spr32",['#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000']],
    "sprtx":["sprtx",['#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000','#000000']],
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

def process_hits(hits, colors):
    values = []
    l = [x['_source']['value'] for x in hits]
    #minimum = min(l)
    if len(l) != 0:
        maximum = max(l)
        minimum = min(l)
        try:
            for item in hits:
                b = (item['_source']['value'] - abs(minimum)) / (maximum - abs(minimum))
                lenght = 1 / (len(colors)-1)
                color  = colors[int(b/lenght)]
                label = item['_source']['type'].split('_')
                if label[-3] == 'index':
                    el = {
                        "value": item['_source']['value'],
                        "year" : label[-1],
                        "color": color
                    }
                else:
                    el = {
                        "value": item['_source']['value'],
                        "year" : label[-1],
                        "month": label[-2],
                        "color": color
                    }
                # el.setdefault(month, []).append(value)
                # print(el)
                values.append(el)
            return values
        except Exception as E:
            print(E)
            print('Exception')
    return values

def match_location(event,context):
    values = []
    print(event)
    size = 0
    month = "0"
    es = connect()
    index = event["queryStringParameters"]["tab"]
    stype = event["queryStringParameters"]["stype"]
    value = variables[event["queryStringParameters"]["value"]][0]
    location = event["queryStringParameters"]["location"].split(',')
    distance = '1mm'

    if stype == 'ecv':
        if index == "climatology" or index =='era5':
            size = 780
        else:
            size = 300
        month = event["queryStringParameters"]["month"]
    elif stype == 'ecvp':
        if month == "0":
            size = 320
        else:
            size = 27
        month = event["queryStringParameters"]["month"]
    else:
        if stype == 'indexp':
            distance = '15km'
        if index =='era5':
            size = 40
        else:
            size = 65

    print(size)

    if month != '0' and month != '-1':
        size = 65
        my_filter = "{}_{}_{}*".format(stype,value, month.zfill(2))
    else:
        my_filter = "{}_{}*".format(stype,value)
    print(my_filter)

    body = {"query": {
        "bool" : {
            "must" : {
                "wildcard" : {
                    "type": my_filter
                }
            },
            "filter" : {
                "geo_distance" : {
                    "distance" : distance,
                    "location" :  [float(location[1]),float(location[0])]
                    }
                }
            }
        }
    }

    try:
        data = es.search(index=index, body=body, size=size, request_cache=True)
        print(data)
        colors = variables[event["queryStringParameters"]["value"]][1]
        values = process_hits(data['hits']['hits'], colors)
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