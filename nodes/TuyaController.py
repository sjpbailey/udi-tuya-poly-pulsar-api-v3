"""
Polyglot v3 node server
Copyright (C) 2023 Steven Bailey
MIT License
This node server polls Tuya TreatLife LED's and Switches for
API control via GET and POST
Version 3.0.1 Jun 2023
Version 3.0.1 Jun 2023
"""
import udi_interface
import time
import json
from tuya_connector import (
    TuyaOpenAPI,)

from nodes import tuya_pulsar_node


LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom


class TuyaController(udi_interface.Node):
    id = 'ctl'
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        {'driver': 'GV0', 'value': 0, 'uom': 56},
    ]

    def __init__(self, polyglot, parent, address, name):
        super(TuyaController, self).__init__(polyglot, parent, address, name)
        self.poly = polyglot
        self.count = 0
        self.n_queue = []
        self.Parameters = Custom(polyglot, 'customparams')
        self.Notices = Custom(polyglot, 'notices')
        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.STOP, self.stop)
        polyglot.subscribe(polyglot.START, self.start, address)
        polyglot.subscribe(polyglot.ADDNODEDONE, self.node_queue)
        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    def parameterHandler(self, params):
        self.Parameters.load(params)
        default_apiAccessId = "apiAccessId"
        default_apiSecret = "apiSecret"
        default_apiEndpoint = "apiEndpoint"
        default_apiMq = "apiMq"
        default_apiUid = "apiUid"
        default_apiRegion = "apiRegion"

        self.apiAccessId = self.Parameters.apiAccessId
        if self.apiAccessId is None:
            self.apiAccessId = default_apiAccessId
            LOGGER.error('check_params: apiKey not defined in customParams, please add it.  Using {}'.format(
                default_apiAccessId))
            self.AccessId = default_apiAccessId
        
        #if  self.AccessId == default_apiAccessId:   
        #   self.Notices['accessid'] = 'ACCESS ID must be configured.'

        self.apiSecret = self.Parameters.apiSecret
        if self.apiSecret is None:
            self.apiSecret = default_apiSecret
            LOGGER.error('check_params: apiSecret not defined in customParams, please add it.  Using {}'.format(
                default_apiSecret))
            self.apiSecret = default_apiSecret
        
        #if  self.apiSecret == default_apiSecret:   
        #   self.Notices['secret'] = 'API SECRET must be configured.'

        self.apiEndpoint = self.Parameters.apiEndpoint
        if self.apiEndpoint is None:
            self.apiEndpoint = default_apiEndpoint
            LOGGER.error('check_params: apiEndpoint not defined in customParams, please add it.  Using {}'.format(
                default_apiEndpoint))
            self.apiRegion = default_apiEndpoint
        
        #if  self.apiRegion == default_apiEndpoint:   
            #self.Notices['apiend'] = 'API ENDPOINT must be configured, make sure you have the right country.'

        self.apiMq = self.Parameters.apiMq
        if self.apiMq is None:
            self.apiMq = default_apiMq
            LOGGER.error('check_params: apiMq not defined in customParams, please add it.  Using {}'.format(
                default_apiMq))
            self.apiMq = default_apiMq
        
        #if  self.apiMq == default_apiMq:   
        #    self.Notices['apimq'] = 'API MQ must be configured, make sure you have the right country.'

        self.apiUid = self.Parameters.apiUid
        if self.apiUid is None:
            self.apiUid = default_apiUid
            LOGGER.error('check_params: apiUid not defined in customParams, please add it.  Using {}'.format(
                default_apiMq))
            self.apiUid = default_apiUid
        
        #if  self.apiUid == default_apiUid:   
        #    self.Notices['apiuid'] = 'API UID must be configured.'

        self.apiRegion = self.Parameters.apiRegion
        if self.apiRegion is None:
            self.apiRegion = default_apiRegion
            LOGGER.error('check_params: apiRegion not defined in customParams, please add it.  Using {}'.format(
                default_apiMq))
            self.apiRegion = default_apiRegion
        
        #if  self.apiRegion == default_apiRegion:   
        #    self.Notices['apiregion'] = 'API REGION must be configured, make sure you have the right country.'
            

    def start(self):
        self.poly.setCustomParamsDoc()
        self.poly.updateProfile()
        time.sleep(2)
        self.createNodes()

    def createNodes(self):
        LOGGER.info("Gathering Devices Please be Patient")
        # Init openapi and connect
        openapi = TuyaOpenAPI(
            self.apiEndpoint, self.apiAccessId, self.apiSecret)
        openapi.connect()
        # Get device information from all devices
        response = openapi.get("/v1.0/users/" + self.apiUid + "/devices")
        # Save polling data sample
        response1 = json.dumps(response, indent=4)  # current, indent=4
        LOGGER.info(response1)
        time.sleep(1)
        self.pulsar()

    def pulsar(self):
        pass
        LOGGER.info("Add Pulsar")
        address = "pulsa_1"
        name = "Pulsar"
        new_id = "pul_1"
        deviceid = "pulse01"
        LOGGER.info('Device Type')
        LOGGER.info("Pulsar")
        LOGGER.info('\n')
        node = tuya_pulsar_node.PullNode(self.poly, self.address, address, name, new_id, deviceid, self.apiAccessId, self.apiSecret, self.apiEndpoint, self.apiMq)
        self.poly.addNode(node)
        self.wait_for_node_done()

    def remove_notices_all(self, command):
        self.Notices.clear()    

    def delete(self):
        LOGGER.info('Delete Tuya Controller.')

    def stop(self):
        self.poly.stop()
        LOGGER.debug('NodeServer stopped.')
        nodes = self.poly.getNodes()
        for node in nodes:
            if node != 'controller':   # but not the controller node
                nodes[node].setDriver('ST', 0, True, True)

    def noop(self, command):
        LOGGER.info('Discover not implemented')

    id = 'tuya'

    commands = {
        'REMOVE_NOTICES_ALL': remove_notices_all,
        'DISCOVER': noop
        }
