#legacy imports
from expedient.common.rpc4django import rpcmethod
from django.contrib.auth.models import User
from pprint import pprint
from foam.ethzlegacyoptinstuff.legacyoptin.xmlrpcmodels import CallBackServerProxy, FVServerProxy
from foam.ethzlegacyoptinstuff.legacyoptin.optsmodels import Experiment, ExperimentFLowSpace,\
    UserOpts, OptsFlowSpace, MatchStruct
from foam.ethzlegacyoptinstuff.legacyoptin.flowspaceutils import dotted_ip_to_int, mac_to_int,\
    int_to_dotted_ip, int_to_mac, parseFVexception
from decorator import decorator
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from foam.legacyoptin.flowspaceutils import int_to_mac, int_to_dotted_ip
from django.contrib.sites.models import Site

#foam general imports
import logging
import zlib
import base64
import xmlrpclib
from xml.parsers.expat import ExpatError
import jsonrpc
from flaskext.xmlrpc import XMLRPCHandler, Fault
from flask import request
import foam.task
import foam.lib
import foam.api.xmlrpc
import foam.version
from foam.creds import CredVerifier, Certificate
from foam.config import AUTO_SLIVER_PRIORITY, GAPI_REPORTFOAMVERSION
from foam.core.configdb import ConfigDB
from foam.core.log import KeyAdapter

#GENI API imports
from foam.geni.db import GeniDB, UnknownSlice, UnknownNode
import foam.geni.approval
import foam.geni.lib
import sfa

#FV import
from foam.flowvisor import Connection as FV

class AMLegExpAPI(foam.api.xmlrpc.Dispatcher):
  def __init__ (self, log):
    super(AMLegExpAPI, self).__init__("legacyexpedientapi", log)
    self._actionLog = KeyAdapter("expedient", logging.getLogger('legexpapi-actions'))

@decorator
def check_fv_set(func, *arg, **kwargs):
  
@decorator
def check_user(func, *args, **kwargs):

def _same(val):
  return "%s" % val  

@check_user
@rpcmethod()
def checkFlowVisor( *arg, **kwargs): 

class om_ch_translate(object): 

def convert_star(fs):

def convert_star_int(fs):

def get_direction(direction):

@check_user
@check_fv_set
@rpcmethod(signature=['struct', # return value
                      'string', 'string', 'string',
                      'string', 'string', 'string',
                      'array', 'array'])
def create_slice(slice_id, project_name, project_description,
                  slice_name, slice_description, controller_url,
                  owner_email, owner_password,
                  switch_slivers, **kwargs):
                  



@check_user
@check_fv_set
@rpcmethod(signature=['string', 'int'])
def delete_slice(sliceid, **kwargs):

@check_user
@check_fv_set
@rpcmethod(signature=['array'])
def get_switches(**kwargs):

@check_user
@check_fv_set
@rpcmethod(signature=['array'])
def get_links(**kwargs):

@check_user
@rpcmethod(signature=['string', 'string', 'string'])
def register_topology_callback(url, cookie, **kwargs):

@check_user
@rpcmethod(signature=['string', 'string'])
def change_password(new_password, **kwargs):
    
@check_user
@rpcmethod(signature=['string', 'string'])
def ping(data, **kwargs):

@check_user
@check_fv_set
@rpcmethod()
def get_granted_flowspace(slice_id, **kwargs):

#@check_user
@check_fv_set
@rpcmethod()
def get_offered_vlans(set=None):
    
def setup (app):
  legexpapi = XMLRPCHandler('legacyexpedientapi')
  legexpapi.connect(app, '/foam/legacyexpedientapi')
  legexpapi.register_instance(AMLegExpAPI(app.logger))
  app.logger.info("[LegacyExpedientAPI] Loaded.")


