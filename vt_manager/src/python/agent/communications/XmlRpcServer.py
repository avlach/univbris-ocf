"""SecureXMLRPCServer.py - simple XML RPC server supporting SSL.

Based on this article: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81549

For windows users: http://webcleaner.sourceforge.net/pyOpenSSL-0.6.win32-py2.4.exe

Imported from http://code.activestate.com/recipes/496786-simple-xml-rpc-server-over-https/ 
"""
import SocketServer
import BaseHTTPServer
import SimpleHTTPServer
import SimpleXMLRPCServer

import socket, os
from OpenSSL import SSL

from settings import XMLRPC_SERVER_LISTEN_HOST,XMLRPC_SERVER_LISTEN_PORT,XMLRPC_SERVER_KEYFILE,XMLRPC_SERVER_CERTFILE,XMLRPC_SERVER_PASSWORD

class SecureXMLRPCServer(BaseHTTPServer.HTTPServer,SimpleXMLRPCServer.SimpleXMLRPCDispatcher):

    def __init__(self, server_address, HandlerClass, logRequests=True):
        """Secure XML-RPC server.

        It it very similar to SimpleXMLRPCServer but it uses HTTPS for transporting XML data.
        """
        self.logRequests = logRequests

        SimpleXMLRPCServer.SimpleXMLRPCDispatcher.__init__(self)
        SocketServer.BaseServer.__init__(self, server_address, HandlerClass)
        ctx = SSL.Context(SSL.SSLv23_METHOD)

        ctx.use_privatekey_file (XMLRPC_SERVER_KEYFILE)
        ctx.use_certificate_file(XMLRPC_SERVER_CERTFILE)
        self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
                                                        self.socket_type))
        self.server_bind()
        self.server_activate()

class SecureXMLRpcRequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
    """Secure XML-RPC request handler class.

    It it very similar to SimpleXMLRPCRequestHandler but it uses HTTPS for transporting XML data.
    """
    def setup(self):
        self.connection = self.request
        self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
        self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)
        
    def do_POST(self):
        """Handles the HTTPS POST request.

        It was copied out from SimpleXMLRPCServer.py and modified to shutdown the socket cleanly.
        """

        try:
            # get arguments
            data = self.rfile.read(int(self.headers["content-length"]))
            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and dispatch
            # using that method if present.
            response = self.server._marshaled_dispatch(
                    data, getattr(self, '_dispatch', None)
                )
        except: # This should only happen if the module is buggy
            # internal error, report as HTTP server error
            self.send_response(500)
            self.end_headers()
        else:
            # got a valid XML RPC response
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

            # shut down the connection
            self.wfile.flush()
            self.connection.shutdown() # Modified here!
    
class XmlRpcServer():
	@staticmethod
	def createInstanceAndEngage(callBackFunction,HandlerClass = SecureXMLRpcRequestHandler,ServerClass = SecureXMLRPCServer):
	    """Test xml rpc over https server"""
	    class xmlrpc_wrappers:
        	def __init__(self):
	            import string
        	    self.python_string = string
            
		def send(self, callBackUrl,amId,password,xml):
		    #FIXME: XXX: use certificates instead of password based authentication
		    if password != XMRPC_SERVER_PASSWORD:
			raise Exception("Password mismatch")

    		    callBackFunction(callBackUrl,xml)
		    return ""
        
		def ping(self, challenge): 
            	    return challenge
        
	    server_address = (XMLRPC_SERVER_LISTEN_HOST, XMLRPC_SERVER_LISTEN_PORT) # (address, port)
	    server = ServerClass(server_address, HandlerClass)    
	    server.register_instance(xmlrpc_wrappers())    
	    sa = server.socket.getsockname()
	    print "Serving HTTPS on", sa[0], "port", sa[1]
	    server.serve_forever()

