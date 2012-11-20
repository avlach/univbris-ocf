# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University
# extended on OFELIA's behalf from Vasileios Kotronis based on gapi1 foam implementation from Nick Bastin
# and of course http://groups.geni.net/geni/wiki/GAPI_AM_API_V2 , where gapi2 is specified
# also used OMNI implementation (gcf-2.1) as reference

#imports same as gapi1
import logging
import zlib
import base64
import xmlrpclib
from xml.parsers.expat import ExpatError

from flaskext.xmlrpc import XMLRPCHandler, Fault
from flask import request

import foam.task
import foam.lib
import foam.api.xmlrpc
import foam.version
import foam.geni.approval
from foam.creds import CredVerifier, Certificate
from foam.config import AUTO_SLIVER_PRIORITY, GAPI_REPORTFOAMVERSION
from foam.core.configdb import ConfigDB
from foam.core.log import KeyAdapter
from foam.geni.db import GeniDB, UnknownSlice, UnknownNode

import foam.geni.lib

import sfa

#further imports that may be needed (see OMNI)
import datetime
import dateutil.parser
import os
import uuid
import xml.dom.minidom as minidom



class AMAPIv2(foam.api.xmlrpc.Dispatcher):
  def __init__ (self, log):
    super(AMAPIv2, self).__init__("GAPIv2", log)
	
	def recordAction (self, action, credentials = [], urn = None):
		cred_ids = []
		self._actionLog.info("Sliver: %s  Gapi2 Action: %s" % (urn, action))
    for cred in credentials:
      self._actionLog.info("Credential: %s" % (cred))
		
	def pub_GetVersion  (self):
		self.recordAction("getversion")
		d ={"geni_api" : 2,
				"geni_api_versions" : {
						'1' : 'https://localhost:3626/core/gapi1/',
						'2' : 'https://localhost:3626/core/gapi2/'
				}
				"geni_request_rspec_versions" : [
            { 'type': 'GENI',
              'version': '3',
							'schema': 'http://www.geni.net/resources/rspec/3/request.xsd',
						  'namespace': 'http://www.geni.net/resources/rspec/3',
							'extensions': [ 'http://www.geni.net/resources/rspec/ext/openflow/3',
                              'http://www.geni.net/resources/rspec/ext/openflow/4',
                              'http://www.geni.net/resources/rspec/ext/flowvisor/1', ]}
            ],
        "geni_ad_rspec_versions" : [
            { 'type': 'GENI',
							'version': '3',
							'schema': 'http://www.geni.net/resources/rspec/3/ad.xsd',
							'namespace': 'http://www.geni.net/resources/rspec/3',
							'extensions': [ 'http://www.geni.net/resources/rspec/ext/openflow/3' ]}
            ],
				"options" : {
						'site_info' : self.generateSiteInfo
				}
       }
		#legacy, accumulated to options		
		#d["site_info"] = self.generateSiteInfo()
		
		return d
	
	def generateSiteInfo (self):
    dmap = [("site.admin.name", "admin-name"),
            ("site.admin.email", "admin-email"),
            ("site.admin.phone", "admin-phone"),
            ("site.location.address", "org-address"),
            ("site.location.organization", "org-name"),
            ("site.description", "description")]
    sinfo = {}
    for ckey, vkey in dmap:
      val = ConfigDB.getConfigItemByKey(ckey).getValue()
      if val is not None:
        sinfo[vkey] = val

    return sinfo
		
	def pub_ListResources (self, credentials, options):
		try:

		
		
#setup same as gapi1 (change version nums of course)
def setup (app):
  gapi2 = XMLRPCHandler('gapi2')
  gapi2.connect(app, '/foam/gapi/2')
  gapi2.register_instance(AMAPIv2(app.logger))
  app.logger.info("[GAPIv2] Loaded.")

