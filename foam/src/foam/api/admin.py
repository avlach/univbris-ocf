# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

import traceback
import hashlib

from flask import request

from foam.flowvisor import Connection as FV
from foam.core.json import jsonify, jsonValidate, JSONValidationError
from foam.api.jsonrpc import Dispatcher, route
from foam import types
import foam.task
import foam.lib
import foam.geni.lib
from foam.geni.db import GeniDB
from foam.core.configdb import ConfigDB

class AdminAPIv1(Dispatcher):
  def __init__ (self, app):
    super(AdminAPIv1, self).__init__("Admin v1", app.logger, app)
    self._log.info("Loaded")

  def validate (self, rjson, types):
    return jsonValidate(rjson, types, self._log)

  @route('/core/admin/get-fv-slice-name', methods=["POST"])
  def getFVSliceName (self):
    if not request.json:
      return
    try:
      self.validate(request.json, [("slice_urn", (unicode,str))])
      name = GeniDB.getFlowvisorSliceName(request.json["slice_urn"])
      return jsonify({"name" : name})
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/list-slivers', methods=["POST", "GET"])
  def listSlivers (self):
    try:
      deleted = False
      status = 0

      if request.method == "POST":
        if not request.json:
          return ""
        if request.json.has_key("deleted"):
          deleted = request.json["deleted"]
        if request.json.has_key("status"):
          st = request.json["status"].lower()
          if st == "approved":
            status = True
          elif st == "rejected":
            status = False
          elif st == "pending":
            status = None

      slivers = GeniDB.getSliverList(deleted, status)
      return jsonify({"slivers" : slivers})
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg = traceback.format_exc())

  @route('/core/admin/approve-sliver', methods=["POST"])
  def approveSliver (self):
    if not request.json:
      return
    return foam.geni.lib.approveSliver(request, self._log)

  @route('/core/admin/reject-sliver', methods=["POST"])
  def rejectSliver (self):
    if not request.json:
      return
    try:
      self.validate(request.json, [("sliver_urn", (unicode,str))])
      slice_name = GeniDB.getFlowvisorSliceName(sliver_urn=request.json["sliver_urn"])
      sobj = GeniDB.getSliverObj(request.json["sliver_urn"])

      data = GeniDB.getSliverData(sobj.getURN(), True)

      GeniDB.setSliverStatus(request.json["sliver_urn"], False)
      if FV.sliceExists(slice_name):
        FV.deleteSlice(slice_name)

      foam.task.emailRejectSliver(data)

      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/disable-sliver', methods=["POST"])
  def disableSliver (self):
    if not request.json:
      return
    try:
      self.validate(request.json, [("sliver_urn", (unicode,str))])
      slice_name = GeniDB.getFlowvisorSliceName(sliver_urn=request.json["sliver_urn"])
      sobj = GeniDB.getSliverObj(request.json["sliver_urn"])

      data = GeniDB.getSliverData(sobj.getURN(), True)

      GeniDB.setSliverStatus(request.json["sliver_urn"], None)
      GeniDB.commit()

      if FV.sliceExists(slice_name):
        FV.deleteSlice(slice_name)

      foam.task.emailDisableSliver(data)

      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/delete-sliver', methods=["POST"])
  def deleteSliver (self):
    if not request.json:
      return
    try:
      self.validate(request.json, [("sliver_urn", (unicode,str))])

      data = GeniDB.getSliverData(request.json["sliver_urn"], True)

      foam.geni.lib.deleteSliver(sliver_urn=request.json["sliver_urn"])

      foam.task.emailJSONDeleteSliver(data)

      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())
      
  @route('/core/admin/show-sliver', methods=["POST"])
  def showSliver (self):
#    from foam.core.tracer import Tracer
#    Tracer.enable()

    if not request.json:
      return

    try:
      return_obj = {}

      self.validate(request.json, [("sliver_urn", (unicode,str))])

      sobj = GeniDB.getSliverObj(request.json["sliver_urn"])
      return_obj["sliver"] = sobj

      if request.json.has_key("flowspace") and request.json["flowspace"]:
        return_obj["flowspace"] = sobj.generateFlowEntries()

      if request.json.has_key("flowspec") and request.json["flowspec"]:
        return_obj["flowspec"] = sobj.json_flowspec()

      if request.json.has_key("rspec") and request.json["rspec"]:
        return_obj["rspec"] = GeniDB.getRspec(request.json["sliver_urn"])

#      path = Tracer.disable()
#      self._log.debug("Tracer path: %s" % (path))

      return jsonify(return_obj)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/get-config', methods=["POST"])
  def getConfig (self):
    if not request.json:
      return

    try:
      objs = self.validate(request.json, [("key", (unicode,str))])
      u = ConfigDB.getUser(request.environ["USER"])
      # Don't look here - stupidity to get around the fact that we don't
      # have output processors
      if objs["key"] == "geni.max-lease":
        val = ConfigDB.getConfigItemByKey("geni.max-lease").getValue(u)
        return jsonify({"value" : str(val)})
      else:
        return jsonify({"value" : ConfigDB.getConfigItemByKey(request.json["key"]).getValue(u)})
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except TypeError, e:
      return jsonify(None, 3, msg = "Unknown key (%s)" % (objs["key"]))
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg = traceback.format_exc())

  @route('/core/admin/set-config', methods=["POST"])
  def setConfig (self):
    if not request.json:
      return
    try:
      objs = self.validate(request.json, [("key", (unicode,str)), ("value", (dict, int, unicode, str))])
      u = ConfigDB.getUser(request.environ["USER"])
      key = request.json["key"]
      ConfigDB.getConfigItemByKey(request.json["key"]).write(request.json["value"], u)
      return jsonify({"status" : "success"})
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())


  @route('/core/admin/get-sliver-flowspace', methods=["POST"])
  def getSliverFlowspace (self):
    if not request.json:
      return
    try:
      self.validate(request.json, [("sliver_urn", (unicode,str))])
      sobj = GeniDB.getSliverObj(request.json["sliver_urn"])
      return jsonify({"flowspace" : sobj.generateFlowEntries()})
    except JSONValidationError, e:
      return jsonify(e.__json__())
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/get-version', methods=["GET"])
  def jsonGetVersion (self):
    try:
      import foam.version
      return jsonify({"version" : foam.version.VERSION})
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/set-location', methods=["POST"])
  def setLocation (self):
    if not request.json:
      return
    try:
      self.validate(request.json, [("lat", float), ("long", float), ("dpid", (unicode,str)), ("country", (unicode,str))])
      GeniDB.setLocation(request.json["dpid"], request.json["country"], request.json["lat"], request.json["long"])
      return jsonify({"status" : "success"})
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/add-datapath', methods=["POST"])
  def addDatapath (self):
    if not request.json:
      return

    try:
      self.validate(request.json, [("dpid", (unicode,str))])
      GeniDB.addDatapath(request.json["dpid"])
      return jsonify({"status" : "success"})
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/remove-datapath', methods=["POST"])
  def removeDatapath (self):
    if not request.json:
      return

    try:
      self.validate(request.json, [("dpid", (unicode,str))])
      GeniDB.removeDatapath(request.json["dpid"])
      return jsonify({"status" : "success"})
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/set-trigger', methods=["POST"])
  def setTrigger (self):
    if not request.json:
      return
    try:
      obj = self.validate(request.json, [("type", types.TriggerType), ("start", (str,unicode)),
                              ("end", (str,unicode)), ("event", types.EventType),
                              ("action", None)])
      GeniDB.addTrigger(obj["type"], obj["start"], obj["end"], obj["event"], obj["action"])
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/set-sliver-expiration', methods=["POST"])
  def adminSetSliverExpiration (self):
    if not request.json:
      return
    try:
      objs = self.validate(request.json, [("datetime", types.DateTime), ("urn", types.SliverURN)])
      GeniDB.updateSliverExpiration(objs["urn"], objs["datetime"])
      return jsonify({"status" : "success"})
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/rebuild-flowvisor-cache', methods=["GET"])
  def adminRebuildFlowvisorCache (self):
    try:
      FV.rebuildCache()
      return jsonify(None)
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/begin-import', methods=["GET"])
  def adminBeginImport (self):
    try:
      ConfigDB.importing = True
      return jsonify(None)
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/finish-import', methods=["GET"])
  def adminFinishImport (self):
    try:
      ConfigDB.importing = False
      return jsonify(None)
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

  @route('/core/admin/import-sliver', methods=["POST"])
  def adminImportSliver (self):
    if not request.json:
      return
    try:
      objs = self.validate(request.json, [("slice_urn", (str, unicode)), 
                                          ("sliver_urn", (str, unicode)),
                                          ("fvslicename", (str, unicode)),
                                          ("req_rspec", (str, unicode)),
                                          ("manifest_rspec", (str, unicode)),
                                          ("exp", (types.DateTime)),
                                          ("priority", (int)),
                                          ("status", (bool)),
                                          ("deleted", (bool))])
      self._log.info("Importing sliver %s" % (objs["sliver_urn"]))
      obj = foam.geni.lib.importSliver(objs)
      return jsonify(None)
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg  = traceback.format_exc())

	#Vasileios's code for listing free vlans
	@route('/core/admin/list-free-vlans', methods=["POST"])
	def adminListFreeVLANs (self):
		try:
			if not request.json:
						return ""
					
			globalvlanlist = {}
			for i in range(4095):
				globalvlanlist[i] = "free"
			
			slivers = GeniDB.getSliverList(False, True, True)
			for sliv in slivers:
				fspecs = sliv.getFlowspecs()
				for fs in fspecs:
					for vlanid in fs.getVLANs():
						globalvlanlist[i] == "occupied"
			
			freevlanlist = []
			for i in globalvlanlist.iterkeys():
				if globalvlanlist[i] == "free":
				freevlanlist.append(i)	
				
			occupiedvlanlist = []
			for i in globalvlanlist.iterkeys():
				if globalvlanlist[i] == "occupied":
				occupiedvlanlist.append(i)	
			
			return jsonify({"free-vlans" : freevlanlist})
			
    except JSONValidationError, e:
      jd = e.__json__()
      return jsonify(jd, code = 1, msg = jd["exception"])
    except Exception, e:
      self._log.exception("Exception")
      return jsonify(None, code = 2, msg = traceback.format_exc())
	

def setup (app):
  api = AdminAPIv1(app)
  return api

