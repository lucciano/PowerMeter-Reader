#!/usr/bin/python
# coding: utf-8

from settings import PM_config, PM_SETTINGS_LABELS, InfluxDBConfig
from SchneiderElectric_iEM3255 import SchneiderElectric_iEM3255

from influxdb import InfluxDBClient
import time
import datetime

from logmanagement import logmanagement
log = logmanagement.getlog('main', 'utils').getLogger()

def main():
    # client = InfluxDBClient(host=PM_config['influxDB'], port=8086)

    PM_cacheEnabled = PM_config['cacheEnabled']
    pm = SchneiderElectric_iEM3255(PM_config['host'], PM_config['port'], 
        int(PM_config['address']), PM_config['start_reg'], 
        PM_config['max_regs'], PM_config['timeout'], 
        PM_config['endian'], PM_config['addressoffset'], 
        PM_cacheEnabled, PM_config['base_commands'])

    print("Connected? %s" % pm.mb.isConnected)

    info = {}

    for i in PM_SETTINGS_LABELS:
        value = pm._modbusRead(i)
        info[i.replace(" ", "")] = str(value).strip().replace(" ", "")
        print("%s = %s" % (i, value))
    
    print(info)

    print("--------------------------------------")
    print(" Active Power ")
    ap1 = pm.readL1Active()
    ap2 = pm.readL2Active()
    ap3 = pm.readL3Active()
    print("line 1: %s 2: %s 3: %s" % (ap1, ap2, ap3))
    
    print("--------------------------------------")
    print(" Current")
    c1 = pm.readL1Current()
    c2 = pm.readL2Current()
    c3 = pm.readL3Current()
    print("line 1: %s 2: %s 3: %s" % (c1, c2, c3))

    print("--------------------------------------")
    print(" Voltage")
    v1 = pm.readL1Voltage()
    v2 = pm.readL2Voltage()
    v3 = pm.readL3Voltage()
    print("line 1: %s 2: %s 3: %s" % (v1, v2, v3))

    current_time = datetime.datetime.now()
    print(current_time)

    json_body = [
    {
        "measurement": "power",
        "tags": info,
        # "time": current_time,
        "fields": {
            "power1": ap1,
            "power2": ap2,
            "power3": ap3,

            "voltage1": v1,
            "voltage2": v2,
            "voltage3": v3,
            
            "current1": c1,
            "current2": c2,
            "current3": c3

        }
    }]

    for hostConfig in InfluxDBConfig:
        try:
            client = InfluxDBClient(host=hostConfig['host'], port=hostConfig['port'], username=hostConfig['username'], password=hostConfig['password'])
            databases = client.get_list_database()
            if  {u'name': u'sensores'} not in databases:
                 client.create_database(hostConfig['database'])
            client.switch_database(hostConfig['database'])
            client.write_points(json_body)
            print("Write data to ", hostConfig['host'])
            print(json_body);   
        except Exception as e:
            print('Exception:',e)
        print('......................................')


if __name__ == '__main__':
    main()
