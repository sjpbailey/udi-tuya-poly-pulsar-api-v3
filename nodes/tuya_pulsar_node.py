"""
Polyglot v3 node server
Copyright (C) 2023 Steven Bailey
MIT License
Version 3.0.1 Jun 2023
"""
import asyncio
import udi_interface
import time
import json
import logging
from tuya_connector import (
    TuyaOpenAPI,
    TuyaOpenPulsar,
    TuyaCloudPulsarTopic,
    TUYA_LOGGER,)

LOGGER = udi_interface.LOGGER


class PullNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, new_id, deviceid, apiAccessId, apiSecret, apiEndpoint, apiMq):
        super(PullNode, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.lpfx = '%s:%s' % (address, name)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        self.new_id = new_id
        self.deviceid = deviceid
        self.DEVICESW_ID = deviceid
        self.apiAccessId = apiAccessId
        self.ACCESS_ID = apiAccessId
        self.apiSecret = apiSecret
        self.ACCESS_KEY = apiSecret
        self.apiEndpoint = apiEndpoint
        self.API_ENDPOINT = apiEndpoint
        self.apiMq = apiMq
        self.API_MQ = apiMq
        self.setDriver('ST', 1)
        self.setDriver('GV2', 0)
        self.setDriver('GV3', 0)

    def logPulsarOn(self, command):
        API_ENDPOINT = self.API_ENDPOINT
        ACCESS_ID = self.ACCESS_ID
        ACCESS_KEY = self.ACCESS_KEY
        DEVICESW_ID = self.DEVICESW_ID
        ACCESS_MQ = self.API_MQ
        LOGGER.info(ACCESS_MQ)
        
        # Enable debug log
        TUYA_LOGGER.setLevel(logging.DEBUG)

        # Init openapi and connect
        openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
        openapi.connect()

        #LOGGER.info("GV2")
        #if "GV2" == 0 and "GV3" == 0:
        #LOGGER.info("Pulsar Running")
        #time.sleep(1)
        # Init Message Queue
        open_pulsar = TuyaOpenPulsar(ACCESS_ID, ACCESS_KEY, ACCESS_MQ, TuyaCloudPulsarTopic.PROD)
        # Add Message Queue listener
        open_pulsar.add_message_listener(lambda msg: LOGGER.info(f"---\nData received: {msg}"))
        #open_pulsar.add_message_listener(lambda msg: json.dumps(LOGGER.info(str({msg}))))
        
        ivr_one = 'percent'
        percent = int(command.get('value'))

        def set_percent(self, command):
            percent = int(command.get('value'))
        if percent < 1 or percent > 9999:
            LOGGER.error('Invalid Level {}'.format(percent))
        else:
            self.setDriver('GV4', int(percent))
            LOGGER.info('Scanner Time = ' + str(percent) + ' Level')
            
        open_pulsar.start()
        self.setDriver('GV2', 1)
        self.setDriver('GV3', 0)
        LOGGER.info("Pulsar Start")
        time.sleep(percent)
        LOGGER.info(int(percent)) 
        open_pulsar.stop()
        self.setDriver('GV2', 0)
        self.setDriver('GV3', 1)
        LOGGER.info("Pulsar Stop")

    def poll(self, polltype):
        if 'longPoll' in polltype:
            LOGGER.debug('longPoll (node)')
        else:
            pass
            LOGGER.debug('shortPoll (node)')

    def query(self, command=None):
        self.reportDrivers()

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2},
        {'driver': 'GV2', 'value': 0, 'uom': 2},
        {'driver': 'GV3', 'value': 0, 'uom': 2},
        {'driver': 'GV4', 'value': 0, 'uom': 57},
    ]

    id = 'pulsa'

    commands = {
        'SWTON': logPulsarOn,
        'STLVL': logPulsarOn,
        'QUERY': query
    }
