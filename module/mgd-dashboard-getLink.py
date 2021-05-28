import boto3
import os 
import json 

s3 = boto3.resource('s3')
mybucket = s3.Bucket(os.environ['BUCKET'])

variables = {
    "precipitation_monthly":"tp",
    "tmax_monthly":"tmax",
    "tmin_monthly":"tmin",
    "taverage_monthly":"t2m",
    "gst":"GST",
    "heat_risk":"Heat-Risk",
    "harvestr":"HarvestR",
    "su35":"SU-35",
    "sprr":"SprR",
    "wsdi":"WSDI",
    "sanitary_risk":"Sanitary-Risk"
}

def getLink(event,context):
    month = ""
    par = event["queryStringParameters"]
    index = par["tab"]
    stype = par["stype"]
    value = variables[par["value"]]
    year = par["year"].replace('-', '_')
    ecvList = ['ecv', 'ecvp', 'ecvavg', 'ecvanom']
    if stype in ecvList:
        month = par["month"]
    
    if index == 'seasonal_forecast':
        leadt = par["leadt"]
        bucket_prefix="{}/{}/{}/leadt_{}/".format(index, stype, value, leadt)
        if month is not '':
            my_filter = '{}-{}_leadt_{}'.format(year, month.zfill(2), leadt)
        else:
            my_filter = year
    elif index == 'projection':
        if month is not '':
            if year != '1971-2000':
                rcp = par['rcp']
                my_filter = '{}_{}_{}.nc'.format(rcp, year, month.zfill(2))
            else:
                my_filter = '{}_{}.nc'.format(year, month.zfill(2))
        else:
            if year != '1971-2000':
                rcp = par['rcp']
                my_filter = '{}_{}.nc'.format(rcp,year)
            else:
                my_filter = year
        bucket_prefix="{}/{}/{}/".format(index, stype, value)
    else:
        if month is not '':
            if 'avg' in stype:
                my_filter = '{}_AVERAGE_{}.nc'.format(year, month.zfill(2))
            else:
                my_filter = '{}_{}.nc'.format(year, month.zfill(2))
        else:
            my_filter = year
        bucket_prefix="{}/{}/{}/".format(index, stype, value)

    print(my_filter)
    try:
        objs = mybucket.objects.filter(Delimiter = '/',
            Prefix = bucket_prefix)
        print(bucket_prefix)
        size = sum(1 for obj in objs)
        print(size)
        for obj in objs:
            path, filename = os.path.split(obj.key)
            if my_filter in filename:
                print(obj)
                return {
                    'statusCode': 200,
                    'body': json.dumps({"url":'http://{}.s3.amazonaws.com/{}'.format(os.environ['BUCKET'], obj.key)}),
                    "headers": {
                        "Access-Control-Allow-Origin": '*'
                    }
                }
    except Exception as e:
        print(e)
    return {
        'statusCode': 404,
        'body': json.dumps({"Message":"File not found"}),
        "headers": {
            "Access-Control-Allow-Origin": '*'
        }
    }

    