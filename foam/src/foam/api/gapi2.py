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


#Vasileios: additional class to handle geni am return codes as in 
#https://openflow.stanford.edu/display/FOAM/GENI+-+AM+return+code+proposal
#see ListResources exceptions to check how I use it (code, desc, etc.)
class AdditionalException(Exception):
	pass
	

class AMAPIv2(foam.api.xmlrpc.Dispatcher):
	def __init__ (self, log):
		super(AMAPIv2, self).__init__("GAPIv2", log)
	
	def recordAction (self, action, credentials = [], urn = None):
		cred_ids = []
		self._actionLog.info("Sliver: %s  GAPIv2 Action: %s" % (urn, action))
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
		#try verifying creds and privs and produce rspec as in gapi1
		try:
			CredVerifier.checkValid(credentials, [])
			available = options.get("geni_available", False) #isn't currently handled
			compressed = options.get("geni_compressed", False) #handled
			urn = options.get("geni_slice_urn", None) #handled
			rspec_version = options.get("geni_rspec_version", None) #working on it
			
			#handle rspec_version properly, need to test if my code is right
			if rspec_version is None:
				# This is a required option, so error out with bad arguments.
				#self._log.error("No geni_rspec_version supplied to ListResources.")
				addEx = AdditionalException("BADARGS")
				addEx.code = 1 
				addEx.desc = "Bad Arguments: option geni_rspec_version was not supplied."
				raise addEx
			
			type = rspec_version.get("type", None)
			if type is None:
				#self._log.error("ListResources: geni_rspec_version does not contain a type field.")
				addEx = AdditionalException("BADARGS")
				addEx.code = 1 
				addEx.desc = "Bad Arguments: option geni_rspec_version does not have a type field."
				raise addEx
        
			ver = rspec_version.get("version", None)
			if ver is None:
				#self._log.error("ListResources: geni_rspec_version does not contain a version field.")
				addEx = AdditionalException("BADARGS")
				addEx.code = 1 
				addEx.desc = "Bad Arguments: option geni_rspec_version does not have a version field."
				raise addEx
			
			#check if rspec version requested by client is compatible
			#with the one supported by our foam AM
			#working on it currently.....................
			#............................................
			
		
			if urn:
				CredVerifier.checkValid(credentials, "getsliceresources", urn)
				self.recordAction("listresources", credentials, urn)
				sliver_urn = GeniDB.getSliverURN(urn)
				if sliver_urn is None:
					raise Fault("ListResources", "Sliver for slice URN (%s) does not exist" % (urn))
				rspec = GeniDB.getManifest(sliver_urn)
			else:
				self.recordAction("listresources", credentials)
				rspec = foam.geni.lib.getAdvertisement()
			if compressed:
				zrspec = zlib.compress(rspec)
				rspec = base64.b64encode(zrspec)

			return rspec
		except ExpatError, e:
			self._log.error("Error parsing credential strings")
			e._foam_logged = True
			raise e
		except UnknownSlice, x:
			x.log(self._log, "Attempt to list resources on sliver for unknown slice %s" % (urn),
						logging.INFO)
			x._foam_logged = True
			raise x
		except xmlrpclib.Fault, x:
			# Something thrown via GCF, we'll presume it was something related to credentials
			self._log.info("GCF credential check failure.")
			self._log.debug(x, exc_info=True)
			x._foam_logged = True
			raise x
		except AdditionalException, e:
			self._log.error(str(e.code) + ":" + e.desc)
			e._foam_logged = True
			raise e
		except Exception, e:
			self._log.exception("Exception")
			raise e

	def pub_CreateSliver(self, slice_urn, credentials, rspec, users, options):	
	
	
	def pub_DeleteSliver(self, slice_urn, credentials, options):
	
	
	def pub_SliverStatus(self, slice_urn, credentials, options):
	
	
	def pub_RenewSliver(self, slice_urn, credentials, expiration_time, options):

	
	def pub_Shutdown(self, slice_urn, credentials, options):
	
	
#setup same as gapi1 (change version nums of course)
def setup (app):
	gapi2 = XMLRPCHandler('gapi2')
	gapi2.connect(app, '/foam/gapi/2')
	gapi2.register_instance(AMAPIv2(app.logger))
	app.logger.info("[GAPIv2] Loaded.")