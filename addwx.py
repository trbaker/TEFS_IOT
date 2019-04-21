
# coding: utf-8

# # Add x,y point to ArcGIS feature class, based on data from the DHT22 Raspberry Pi sensor.
# Spring 2019, Tom Baker, http://tbaker.com 
# 
# To use this script on your Pi:
# 1. Update the GIS organizatoin URL (xxx-prefix-xxx), username (xxx-username-xxx), and password (xxx-password-xxx) on line 33.
# 2. Update the latitude and longitude to the locatioin where you plan to place the Pi
# 3. Update the feature class service's object id (xxx-objectid-xxx) on line 35.
#  The feature service receiving data must be published and configured for use by the username/password above.
#  You may need to install additional python libraries. See import list on line ~ 17.
# 
# A sample feature class receiving data in a similar way is live at:
# http://tbaker.maps.arcgis.com/home/item.html?id=098f800df2ea45aa9a2a09e38caaa33f
# 

# import statements 
from arcgis.gis import GIS
from arcgis import geometry 
from copy import deepcopy
import time
import Adafruit_DHT

print("starting script.")

#fill out these variables --------------------------------------------------------
#lat and long are fixed, per unit
lat=38.73316
long=-90.190675   # longitude should be neagtive for north/south american locations

# enter your organization URL, username, and password for the owner of the feature service that will be updated
gis = GIS("https://xxx-prefix-xxxx.maps.arcgis.com", "xx-username-XX", "xx-password-xx")
# insert your feature service id in the line below
wx_layer_search = gis.content.search(query='id: xxx-objectid-xxx')

#convert layer list to collection
wx_layer_coll_item = wx_layer_search[0]
wx_layers = wx_layer_coll_item.layers
wx_layer = wx_layers[0]
wx_fset = wx_layer.query()
#print(wx_fset.spatial_reference)

#get geometries in the destination coordinate system
input_geometry = {'y':float(lat),'x':float(long)}
output_geometry = geometry.project(geometries = [input_geometry],in_sr = 4326, 
    out_sr = wx_fset.spatial_reference['latestWkid'],gis = gis)
print(output_geometry[0])

#output layers in object
for field in wx_layer.properties['fields']:
    print(field['name'])

#configure date - using UTC
dt=time.gmtime()  # pulls UTC time from the pi
time_string = time.strftime("%m/%d/%Y, %H:%M:%S", dt)  #formats the time to send to ArcGIS

#sensor data read
sensor = Adafruit_DHT.DHT22
#This is the GPIO Pin number, not just the Pin number.
#This pin in pin 7 but sits in GPIO Pin 4. Use 4 below.
pin = 4
humidityPerc, tempF = Adafruit_DHT.read_retry(sensor, pin)
tempF = tempF * 9/5.0 + 32


# calculate heat Index (F)
heatIndexF = 0.5 * (tempF + 61.0 + ((tempF-68.0)*1.2) + (humidityPerc*0.094))

#create point object for insertion into map
wx_dict = {"attributes": 
           {"lat": lat,
            "long": long,
            "date": time_string,
            "tempF": tempF,
            "heatIndexF" : heatIndexF,
            "humidityPerc": humidityPerc}, 
           "geometry": 
           output_geometry[0]}

add_result = wx_layer.edit_features(adds = [wx_dict])
add_result
print("complete.")


# In[ ]:



