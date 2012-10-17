# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

from flaskext.xmlrpc import XMLRPCHandler, Fault
import foam.api.xmlrpc

class AMAPIv2(foam.api.xmlrpc.Dispatcher):
  def __init__ (self, log):
    super(AMAPIv2, self).__init__("GAPIv2", log)


def setup (app):
  gapi2 = XMLRPCHandler('gapi2')
  gapi2.connect(app, '/foam/gapi/2')
  gapi2.register_instance(AMAPIv2(app.logger))
  app.logger.info("[GAPIv2] Loaded.")

