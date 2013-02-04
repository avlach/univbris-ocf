#Vasileios: legacy ch_api of optin_manager. This worked with Expedient, 
#so we keep the function calls and modify the internal code
#in order to utilize FOAM functionality

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

#my imports
from foam.app import admin_apih #admin is setup beforehand so handler is perfect for handling slices
from foam.ethzlegacyoptinstuff.api_exp_to_rspecv3.expdatatogeniv3rspec import create_ofv3_rspec,\
    extract_IP_mask_from_IP_range


class AMLegExpAPI(foam.api.xmlrpc.Dispatcher):
  def __init__ (self, log):
    super(AMLegExpAPI, self).__init__("legacyexpedientapi", log)
    self._actionLog = KeyAdapter("expedient", logging.getLogger('legexpapi-actions'))

#modified, checked
@decorator
def check_fv_set(func, *arg, **kwargs):
  if (FV.xmlconn is None):
    raise Exception("No xlmlrpc connection with Flowvisor detected")
  if (FV.jsonconn is None):
    raise Exception("No jsonrpc connection with FlowVisor detected")
  return func(*arg, **kwargs)

#as is
@decorator
def check_user(func, *args, **kwargs):
  '''
  Check that the user is authenticated and known.
  '''
  if "request" not in kwargs:
    raise Exception("Request not available for XML-RPC %s" % \
                      func.func_name)
  meta = kwargs["request"].META
  if not hasattr(kwargs["request"], "user"):
    raise Exception("Authentication Middleware not installed in settings.")
  
  if not kwargs['request'].user.is_authenticated():
    raise Exception("User not authenticated for XML-RPC %s." % func.func_name)
  else:
    kwargs['user'] = kwargs['request'].user
    # Check that the user can actually make the xmlrpc call
    this_user = kwargs['user']
    if not this_user.get_profile().is_clearinghouse_user:
      raise Exception("Remote user %s is not a clearinghouse user" % (this_user.username))     
  return func(*args, **kwargs)

def _same(val):
  return "%s" % val  

#modified, checked
@check_user
@rpcmethod()
def checkFlowVisor( *arg, **kwargs):
  if (FV.xmlconn is None):
		raise Exception("No xlmlrpc connection with Flowvisor detected")
	if (FV.jsonconn is None):
		raise Exception("No jsonrpc connection with FlowVisor detected")
		
	return ""

#as is
class om_ch_translate(object): 
  attr_funcs = {
    # attr_name: (func to turn to str, width)
    "dl_src": (int_to_mac, mac_to_int, 48, "mac_src","dl_src"),
    "dl_dst": (int_to_mac, mac_to_int, 48, "mac_dst","dl_dst"),
    "dl_type": (_same, int, 16, "eth_type","dl_type"),
    "vlan_id": (_same, int, 12, "vlan_id","dl_vlan"),
    "nw_src": (int_to_dotted_ip, dotted_ip_to_int, 32, "ip_src","nw_src"),
    "nw_dst": (int_to_dotted_ip, dotted_ip_to_int, 32, "ip_dst","nw_dst"),
    "nw_proto": (_same, int, 8, "ip_proto","nw_proto"),
    "tp_src": (_same, int, 16, "tp_src","tp_src"),
    "tp_dst": (_same, int, 16, "tp_dst","tp_dst"),
    "port_num": (_same, int, 16, "port_number","in_port"),
    }

#as is
def convert_star(fs):
  temp = fs.copy()
  for ch_name, (to_str, from_str, width, om_name, of_name) in \
  om_ch_translate.attr_funcs.items():
    ch_start = "%s_start" % ch_name
    ch_end = "%s_end" % ch_name
    if ch_start not in fs or fs[ch_start] == "*":
      temp[ch_start] = to_str(0)
    if ch_end not in fs or fs[ch_end] == "*":
      temp[ch_end] = to_str(2**width - 1)
  return temp

#as is  
def convert_star_int(fs):
  temp = fs.copy()
  for ch_name, (to_str, from_str, width, om_name, of_name) in \
  om_ch_translate.attr_funcs.items():
    ch_start = "%s_start" % ch_name
    ch_end = "%s_end" % ch_name
    if ch_start not in fs or fs[ch_start] == "*":
      temp[ch_start] = 0
    else:
      temp[ch_start] = from_str(fs[ch_start])    
    if ch_end not in fs or fs[ch_end] == "*":
      temp[ch_end] = 2**width - 1
    else:
      temp[ch_end] = from_str(fs[ch_end])   
                    
  return temp

#as is
def get_direction(direction):
  if (direction == 'ingress'):
    return 0
  if (direction == 'egress'):
    return 1
  if (direction == 'bidirectional'):
    return 2
  return 2

#to be coded-----------------------------------------------------------------------
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
                  
  '''
  Create an OpenFlow slice. 
  
  The C{switch_sliver} list contains a dict for each switch to be added to the
  slice's topology. Each such dict has the following items:
  
  - C{datapath_id}: the switch's datapath id
  - C{flowspace}: an array of dicts describing the switch's flowspace
  Each such dict has the following keys:
      - C{id}: integer. Per clearinghouse unique identifier for the rule.
      - C{port_num_start}, C{port_num_end}: string. the port range for this 
      flowspace
      - C{dl_src_start}, C{dl_src_end}: string. link layer address range in
      "xx:xx:xx:xx:xx:xx" format or '*' for wildcard
      - C{dl_dst_start}, C{dl_dst_end}: string. link layer address range in
      "xx:xx:xx:xx:xx:xx" format or '*' for wildcard
      - C{vlan_id_start}, C{vlan_id_end}: string. vlan id range or
      "*" for wildcard
      - C{nw_src_start}, C{nw_src_end}: string. network address range in 
      "x.x.x.x" format or '*' for wildcard
      - C{nw_dst_start}, C{nw_dst_end}: string. network address range in
      "x.x.x.x" format or '*' for wildcard
      - C{nw_proto_start}, C{nw_proto_end}: string. network protocol range or
      "*" for wildcard
      - C{tp_src_start}, C{tp_src_end}: string. transport port range or "*"
      for wildcard
      - C{tp_dst_start}, C{tp_dst_end}: string. transport port range or "*"
      for wildcard

  The call returns a dict with the following items:
  - C{error_msg}: a summary error message or "" if no errors occurred.
  - C{switches}: a list of dicts with the following items:
      - C{datapath_id}: id of the switch that caused the error
      - C{error}: optional error msg for the switch
      - all other fields of the C{switch_sliver} dicts mentioned above
      (port_num, direction, ...). The values for these items are the error
      messages associated with each field.

  @param slice_id: a string that uniquely identifies the slice at the 
      clearinghouse.
  @type slice_id: int
  
  @param project_name: a name for the project under which this slice 
      is created
  @type project_name: string
  
  @param project_description: text describing the project
  @type project_description: string
  
  @param slice_name: Name for the slice
  @type slice_name: string
  
  @param slice_description: text describing the slice/experiment
  @type slice_description: string
  
  @param controller_url: The URL for the slice's OpenFlow controller specified
      as <transport>:<hostname>[:<port>], where:
          - tranport is 'tcp' ('ssl' will be added later)
          - hostname is the controller's hostname
          - port is the port on which the controller listens to openflow
          messages (defaults to 6633).
  @type controller_url: string
  
  @param owner_email: email of the person responsible for the slice
  @type owner_email: string
  
  @param owner_password: initial password the user can use to login to the
      FlowVisor Web interface. Will need to be changed on initial login.
  @type owner_password: string
  
  @param switch_slivers: description of the topology and flowspace for slice
  @type switch_slivers: list of dicts
  
  @param kwargs: will contain additional useful information about the request.
      Of most use are the items in the C{kwargs['request'].META} dict. These
      include 'REMOTE_USER' which is the username of the user connecting or
      if using x509 certs then the domain name. Additionally, kwargs has the
      user using the 'user' key.
  
  @return: switches and links that have caused errors
  @rtype: dict
  '''
  
  print "Legacy Expedient API: create_slice got the following:"
  print "    slice_id: %s" % slice_id
  print "    project_name: %s" % project_name
  print "    project_desc: %s" % project_description
  print "    slice_name: %s" % slice_name
  print "    slice_desc: %s" % slice_description
  print "    controller: %s" % controller_url
  print "    owner_email: %s" % owner_email
  print "    owner_pass: %s" % owner_password
  print "    switch_slivers"
  pprint(switch_slivers, indent=8)
  
  

#to be coded-----------------------------------------------------------------------
@check_user
@check_fv_set
@rpcmethod(signature=['string', 'int'])
def delete_slice(sliceid, **kwargs):

#modified, to be checked
@check_user
@check_fv_set
@rpcmethod(signature=['array'])
def get_switches(**kwargs):
  '''
  Return the switches that the FlowVisor gives. Change to CH format.
  '''
  complete_list = []
  try:
    dpids = FV.getDeviceList()
    for d in dpids:
      FV.log.debug("XMLRPC:getDeviceInfo (%s)" % (d))
    infos = [FV.xmlcall("getDeviceInfo", d) for d in dpids] #need to make it prettier :)
    switches = zip(dpids, infos)
  except Exception,e:
    import traceback
    traceback.print_exc()
    raise e 
  complete_list.extend(switches) 
  return complete_list
  
#modified, to be checked
@check_user
@check_fv_set
@rpcmethod(signature=['array'])
def get_links(**kwargs):
  '''
  Return the links that the FlowVisor gives. Change to CH format.
  '''
  complete_list = []
  try:
    links = [(l.pop("srcDPID"),
              l.pop("srcPort"),
              l.pop("dstDPID"),
              l.pop("dstPort"),
              l) for l in FV.getLinkList()]
  except Exception,e:
    import traceback
    traceback.print_exc()
    raise e 
  complete_list.extend(links) 
  return complete_list

#to be coded-----------------------------------------------------------------------  
@check_user
@rpcmethod(signature=['string', 'string', 'string'])
def register_topology_callback(url, cookie, **kwargs):
  
#as is, probably needs changes because of DB refs  
@check_user
@rpcmethod(signature=['string', 'string'])
def change_password(new_password, **kwargs):
  '''
  Change the current password used for the clearinghouse to 'new_password'.
  
  @param new_password: the new password to use for authentication.
  @type new_password: random string of 1024 characters
  @param kwargs: will contain additional useful information about the request.
      Of most use are the items in the C{kwargs['request'].META} dict. These
      include 'REMOTE_USER' which is the username of the user connecting or
      if using x509 certs then the domain name.
  @return: Error message if there is any.
  @rtype: string
  '''
  user = kwargs['user']
  user.set_password(new_password)
  user.save()
    
  return ""

#modified, to be checked    
@check_user
@rpcmethod(signature=['string', 'string'])
def ping(data, **kwargs):
  try:
    FV.log.debug("XMLRPC:ping (%s)" % ())
    return FV.xmlcall("ping" + " " + 

#to be coded-----------------------------------------------------------------------      
@check_user
@check_fv_set
@rpcmethod()
def get_granted_flowspace(slice_id, **kwargs):

#modified, to be checked
#@check_user
@check_fv_set
@rpcmethod()
def get_offered_vlans(set=None):
  return admin.adminOfferVlanTags(set, False)

#setup our legacy API  
def setup (app):
  legexpapi = XMLRPCHandler('legacyexpedientapi')
  legexpapi.connect(app, '/foam/legacyexpedientapi')
  legexpapi.register_instance(AMLegExpAPI(app.logger))
  app.logger.info("[LegacyExpedientAPI] Loaded.")


