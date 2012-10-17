# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University
# Copyright (c) 2012  Barnstormer Softworks

import logging
import logging.handlers
import os.path

from flask import Flask, request_started, request, request_tearing_down

from foam.config import FOAMLOG, LOGLEVEL, LOGFORMAT, LOGDIR

##############################################################
### We have to set up logging before child modules can use it
app = Flask("foam")

lhandle = logging.handlers.RotatingFileHandler('%s' % (FOAMLOG),
                                               maxBytes = 1000000, backupCount = 10)
lhandle.setLevel(LOGLEVEL)
lhandle.setFormatter(logging.Formatter(LOGFORMAT))
app.logger.addHandler(lhandle)
app.logger.setLevel(LOGLEVEL)

pl = logging.getLogger("perf")
plh = logging.handlers.RotatingFileHandler(os.path.normpath("%s/perf.log" % (LOGDIR)),
                                           maxBytes = 1000000, backupCount = 10)
plh.setLevel(logging.DEBUG)
plh.setFormatter(logging.Formatter("%(created)f [%(levelname)s] %(message)s"))
pl.addHandler(plh)
pl.setLevel(logging.DEBUG)

app.logger.info("[FOAM] Application Startup")
##############################################################

from foam.core.configdb import ConfigDB
from foam.geni.db import GeniDB

#request_tearing_down.connect(ConfigDB.close, app)
#request_tearing_down.connect(GeniDB.close, app)

from foam.api import auth
auth.setup(app)

from foam.api import gapi1
gapi1.setup(app)

from foam.api import gapi2
gapi2.setup(app)

from foam.api import debug
debug.setup(app)

from foam.api import auto
auto.setup(app)

from foam.api import admin
admin.setup(app)

from foam.api import geni
geni.setup(app)

ConfigDB.commit()
GeniDB.commit()

def init (pm):
  pass
  #  for plugin in pm.getByInterface("foam.interface.rpc"):
  #  plugin.connect(app)

@request_started.connect_via(app)
def log_request (sender):
  app.logger.info("[REQUEST] [%s] <%s>" % (request.remote_addr, request.url))

