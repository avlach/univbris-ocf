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

#further imports that may be needed
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

    self._actionLog.info("Sliver: %s  Action: %s" % (urn, action))

    for cred in credentials:
      self._actionLog.info("Credential: %s" % (cred))
			


#same as gapi1
def setup (app):
  gapi2 = XMLRPCHandler('gapi2')
  gapi2.connect(app, '/foam/gapi/2')
  gapi2.register_instance(AMAPIv2(app.logger))
  app.logger.info("[GAPIv2] Loaded.")

