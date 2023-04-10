# Automated archive search and notification
A python program for automating and scheduling archive searches on UP42. If new archives are found a notification is 
sent via email. 

This serves as an example of capabilities and might not be the best solution for everyone out of the box. Please make 
this code your own and modify it at will, especially the notification component.

You will need an UP42 account. Signing up and searching the archive is free of cost, if you want to order data you only 
pay for the area that intersects your AOI.<br>https://up42.com/ <br>

Authentication:<br>
For authenticating, provide your UP42 credentials into: ./credentials/proj_config_file.json<br>
If you need help finding your credentials on UP42 follow these instructions.<br>
https://docs.up42.com/processing-platform/projects#find-project-credentials <br>

Area of interest:<br>
AOI file must be placed in the aoi folder and must be a geojson single polygon in WGS84 (EPSG:4326) with no more than 
999 vertices.<br>

Search parameters:<br>
The search parameters are defined in main.py file. Modify these as needed by pointing to a different aoi file, changing
cloud cover percentage and collections. 

Example:
>aoi_file_name = 'aoi_europe.geojson'<br>
collection = ['pneo', 'spot', 'phr']<br>
>cloud_cover = 10<br>

Available collections can be discovered using the following code. It will print out all the currently available datasets 
that can be queried via the API. For now, you can search for collections within a host. You can not for instance search 
for Hexagon and OneAtlas collections at the same time as these are different host endpoints.<br> 
>all_collection_list = catalog.get_collections() <br>
for x in all_collection_list: <br>
>print(f"{x['host']['name']} -> {x['name']}")

Automation and scheduling:<br>
In its current state, this code will run every 60 minutes. You can modify this as needed in the main.py file. Some example
are commented in that file.

Notification:<br>
In this current version I send an email notification using my Google email account. In order to send emails via python 
you must first create a dedicated app password. See this documentation on how to do so:<br>
https://support.google.com/accounts/answer/185833?hl=en <br>

The program uses the following Libraries:<br>
+ up42
+ datetime
+ pathlib
+ time
+ smtplib
+ ssl
+ EmailMessage
+ json
+ schedule

Happy archive searching !!

