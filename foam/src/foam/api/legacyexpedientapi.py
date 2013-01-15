from expedient.common.rpc4django import rpcmethod
from django.contrib.auth.models import User
from pprint import pprint
from foam.legacyoptin.xmlrpcmodels import CallBackServerProxy, FVServerProxy
from foam.legacyoptin.optsmodels import Experiment, ExperimentFLowSpace,\
    UserOpts, OptsFlowSpace, MatchStruct
from foam.legacyoptin.flowspaceutils import dotted_ip_to_int, mac_to_int,\
    int_to_dotted_ip, int_to_mac, parseFVexception
from decorator import decorator
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from foam.legacyoptin.flowspaceutils import int_to_mac, int_to_dotted_ip
from django.contrib.sites.models import Site

import xmlrpclib
import jsonrpc
import logging
from foam.flowvisor import Connection as FV