#!/usr/bin/env python3

import json
from bottle import post, route
from settings import config
from modules.pastafari.models import servers
from modules.pastafari.libraries.configclass import config_task
from paramecio.cromosoma.extrafields.ipfield import IpField
from paramecio.cromosoma.webmodel import WebModel
from paramecio.citoplasma import datetime
from paramecio.citoplasma.httputils import GetPostFiles

#http://192.168.1.79:8080/monit/getinfo/192.168.2.5/key

@route('/monit/graphs/<ip>/<api_key>')
def graph(ip, api_key):
    
    getpost=GetPostFiles()
    
    if config_task.api_key==api_key:
        
        ipcheck=IpField('', '')
        
        ip=ipcheck.check(ip)
        
        if ipcheck.error!=True:
            
            pass
    
