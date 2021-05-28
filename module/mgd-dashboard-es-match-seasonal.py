import os
import json
import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection

elastic_endpoint = os.environ['ES_ENDPOINT']
path = '{}/{}/{}/{}/{}'
cwd = os.getcwd()
index = '{}_{}_{}_{}'

# colors = [ "#73ff00","#f1c40f","#fe5009"]

val = {
    "1":["0,33.3", "Lower Tercile"],
    "2":["33.4,66.7", "Medium Tercile"],
    "3":["66.7,100", "Upper Tercile"],
    "-1":["", ""]
}

variables = {
    "precipitation_monthly":["tp",['#deebf7','#9ecae1','#08519c']],
    "tmax_monthly":["tmax",['#ffeda0','#feb24c','#bd0026']],
    "tmin_monthly":["tmin",['#e7e1ef','#c994c7','#980043']],
    "taverage_monthly":["t2m",['#fee6ce','#fdae6b','#a63603']],
    "gst":["gst",['#ffeda0','#feb24c','#bd0026']],
    "heat_risk":["heatrisk",['#a6d96a','#fdae61','#d73027']],
    "harvestr":["harvestr",['#deebf7','#9ecae1','#08519c']],
    "su35":["su35",['#ffeda0','#feb24c','#bd0026']],
    "su36":["su36",['#ffeda0','#feb24c','#bd0026']],
    "su40":["su40",['#ffeda0','#feb24c','#bd0026']],
    "spr32":["spr32",['#ffeda0','#feb24c','#bd0026']],
    "sprr":["sprr",['#deebf7','#9ecae1','#08519c']],
    "wsdi":["wsdi",['#ffeda0','#feb24c','#bd0026']],
    "sanitary_risk":["sanitaryrisk",['#a6d96a','#fdae61','#d73027']],
    "sprtx":["sprtx",['#ffeda0','#feb24c','#bd0026']]
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

def process_hits(hits, colors, stype):
    print('dentro process')
    values = []
    # el = dict()
    # value = {}
    try:
        for item in hits:
            color = ""
            label = item['_source']['type'].split('_')
            print(label)
            value = int(item['_source']['value'])
            if value > 0:
                color = colors[int(value)-1]
            if stype == "ecv":
                month = label[-4].zfill(2)
                el = {
                    "value": val[str(value)][0],
                    "integer_value": str(value),
                    "year" : label[-3],
                    "month": label[-4].zfill(2),
                    "leadt": label[-1],
                    "color": color,
                    "name" : val[str(value)][1]
                }
            else:
                el = {
                    "value": val[str(value)][0],
                    "integer_value": str(value),
                    "year" : label[-3],
                    "leadt": label[-1],
                    "color": color,
                    "name" : val[str(value)][1]
                }
            # el.setdefault(month, []).append(value)
            values.append(el)
        return values
    except Exception as E:
        print(E)
        exit(3)

def match_location_seas(event,context):
    values = []
    print(event)
    size = 0
    month = "0"
    es = connect()
    try:
        index = "seasonal_forecast"
        # index = event["queryStringParameters"]["tab"]
        stype = event["queryStringParameters"]["stype"]
        value = variables[event["queryStringParameters"]["value"]][0]
        location = event["queryStringParameters"]["location"].split(',')
        leadt = event["queryStringParameters"]["leadt"]

        if stype == 'ecv':
            month = event["queryStringParameters"]["month"]
            size = 324
            if month != '0':
                size = 65
                my_filter = "{}_{}_{}*_leadt_{}".format(stype,value,month.zfill(2),leadt)
            else:
                my_filter = "{}_{}*_leadt_{}".format(stype,value, leadt)
        else:
            size = 65
            my_filter = "{}_{}*_stdt_{}".format(stype,value, leadt)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"message": str(e) + ' value not found!'}),
            "headers": {
                "Access-Control-Allow-Origin": '*'
            }
        }
    
    print(my_filter)

    # body = {
    #     "query": {
    #         "bool": {
    #             "must": [
    #                 { "wildcard" : { "type" : "{}_{}*_leadt_{}".format(stype,value,leadt)}},
    #                 { "match" : { "location" : location}}
    #             ]
    #         }
    #     }
    # }

    body = {"query": {
            "bool" : {
                "must" : {
                    "wildcard" : {
                        "type": my_filter
                    }
                },
                "filter" : {
                    "geo_distance" : {
                        "distance" : "1mm",
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
        values = process_hits(data['hits']['hits'], colors,stype)
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