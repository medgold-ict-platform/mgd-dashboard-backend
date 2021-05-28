import boto3
import pandas as pd
import xarray as xr
import os
import datetime
from datetime import date
from netCDF4 import Dataset
import netCDF4
download_path = './'
BUCKET_PATH = 'climatology/ecv/'
BUCKET_NAME = 'dashboard.med-gold.eu'

s3 = boto3.resource("s3",region_name='eu-west-1')
s3Client = boto3.client('s3')
bucket = s3.Bucket(BUCKET_NAME)

if __name__ == "__main__":
    objs = bucket.objects.filter(Delimiter = '/', Prefix = BUCKET_PATH)
    size = sum(1 for obj in objs)
    for obj in objs:
        name_of_file = obj.key.split('/')[-1]
        print(name_of_file)
        if 'HRES' in name_of_file:
            bucket.download_file(obj.key, './'+name_of_file)
            # old
            data = xr.open_dataset(name_of_file, engine='netcdf4', decode_times=True)
            data['time'] = data.indexes['time'].normalize().astype(str)
            data = data.to_dataframe()
            print('convert to dataframe')
            data = data.to_csv(name_of_file.replace('nc', "csv"),index=True, header=True, encoding='utf-8')
            print('convert to gzip')
            #bucket.upload_file(name_of_file.replace('nc', "gzip"), BUCKET_PATH+'csv/'+ name_of_file.replace('nc', "gzip"))



            # nc = Dataset(download_path+name_of_file, mode='r')
            # print(nc)
            # nc.variables.keys()

            # lat = nc.variables['lat'][:]
            # lon = nc.variables['lon'][:]
            # time_var = nc.variables['time']
            # dtime = netCDF4.num2date(time_var[:],time_var.units)
            # precip = nc.variables['precipi'][:]
            # print(precip)
            # # a pandas.Series designed for time series of a 2D lat,lon grid
            # precip_ts = pd.Series(precip, index=dtime) 

            # precip_ts.to_csv('precip.csv',index=True, header=True)
            # csvwriter = csv.writer(tmp,  delimiter=',')
            # print (csvwriter)
