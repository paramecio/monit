#!/usr/bin/python3

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

@post('/monit/getinfo/<ip>/<api_key>')
def post(ip, api_key):
    
    getpost=GetPostFiles()
    
    if config_task.api_key==api_key:
        
        conn=WebModel.connection()
        
        server=servers.Server(conn)
        
        ipcheck=IpField('', '')
        
        ip=ipcheck.check(ip)
        
        server.set_conditions('WHERE ip=%s', [ip])
        
        c=server.select_count()
        
        if ipcheck.error!=True and c>0:
            
            status_disk=servers.StatusDisk(conn)
            
            status_net=servers.StatusNet(conn)
            
            status_cpu=servers.StatusCpu(conn)           
            
            server.set_conditions('where ip=%s', [ip])
            
            server.yes_reset_conditions=False
            
            if server.select_count()>0:
                
                arr_update={'status': 1, 'monitoring':1, 'date': datetime.now()}
            
                getpost.obtain_post(['data_json'], True)
            
                try:
            
                    arr_info=json.loads(getpost.post['data_json'])
                    
                except:
                
                    return 'Ouch'
                
                if 'net_info' in arr_info:
                    
                    net_info=arr_info['net_info']
                    
                    if type(net_info).__name__=='list':
                        
                        post={'bytes_sent': net_info[0], 'bytes_recv': net_info[1], 'errin': net_info[2], 'errout': net_info[3], 'dropin': net_info[4], 'dropout': net_info[5], 'date': datetime.now(), 'ip': ip, 'last_updated': 1}
                        
                        status_net.reset_require()
                                
                        status_net.create_forms()
                        
                        status_net.set_order(['id'], ['DESC'])
                        
                        status_net.set_limit([1])
                        
                        status_net.set_conditions('WHERE ip=%s', [ip])
                        
                        status_net.update({'last_updated': 0})
                        
                        status_net.insert(post)
                        
                if 'cpu_idle' in arr_info:
                    
                    status_cpu.reset_require()
                                
                    status_cpu.create_forms()
                    
                    status_cpu.set_order(['id'], ['DESC'])
                    
                    status_cpu.set_limit([1])
                    
                    status_cpu.set_conditions('WHERE ip=%s', [ip])
                    
                    status_cpu.update({'last_updated': 0})
                            
                    status_cpu.insert({'ip': ip, 'idle': arr_info['cpu_idle'], 'date': datetime.now(), 'last_updated': 1})
                            
                    arr_update['actual_idle']=arr_info['cpu_idle']
                
                if 'disks_info' in arr_info:
                    
                    status_disk.create_forms()
                            
                    status_disk.set_conditions('WHERE ip=%s', [ip])
                    
                    method_update=status_disk.insert
                    
                    if status_disk.select_count()>0:
                        
                        method_update=status_disk.update
                    
                    for disk, data in arr_info['disks_info'].items():
                        
                        status_disk.set_conditions('where ip=%s and disk=%s', [ip, disk])
                        
                        method_update({'ip' : ip, 'disk' : disk, 'date' : datetime.now(), 'size' : data[0], 'used' : data[1], 'free' : data[2], 'percent' : data[3]})
                        
                #Save status
            
                server.reset_require()
                
                server.create_forms()
                
                server.update(arr_update)
                
                return 'Ok'
    
    return "Ouch"
    
@route('/monit/getupdates/<ip>/<api_key>', ['POST'])
def get_updates(ip, api_key):
    
    getpost=GetPostFiles()
    
    if config_task.api_key==api_key:
        
        ipcheck=IpField('', '')
        
        ip=ipcheck.check(ip)
        
        if ipcheck.error!=True:
            
            getpost.obtain_post(['num_updates'], True)
            
            try:
                
                num_updates=int(getpost.post.get('num_updates', '0'))
                
            except:
                
                num_updates=0
                
            #if num_updates>0:
                
            conn=WebModel.connection()
        
            server=servers.Server(conn)
            
            server.valid_fields=['num_updates'];

            server.set_conditions('where ip=%s', [ip])

            server.reset_require()

            server.update({'num_updates': num_updates})
            
            return 'Ok'
            
    
    return "Ouch"
    
    """
    
    public function get_updates($ip, $api_key)
    {
    
        if($api_key===ConfigTask::$api_key)
        {
            
            if(filter_var($ip, FILTER_VALIDATE_IP)) 
            {
                
                settype($_POST['num_updates'], 'integer');
                
                if($_POST['num_updates']>0)
                {
                
                    Webmodel::$m->server->fields_to_update=['num_updates'];

                    Webmodel::$m->server->set_conditions(['where ip=?', [$ip]]);

                    Webmodel::$m->server->reset_require();

                    Webmodel::$m->server->update(['num_updates' => $_POST['num_updates']]);

                }
                
            }
            
        }
        
    }

}
    """
    
