#  coding: utf-8 
import SocketServer
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

RESPONSE_CODE={200:"OK",302:"FOUND",404:"NOT FOUND"}

MIME_TYPE={"html":"text/html","css":"text/css"}

ERROR_PATH=os.path.abspath("error.html")

class MyWebServer(SocketServer.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        method,dir=self.headerhandle(self.data)
        method_func=getattr(self,method)
        method_func(dir)
    
        
    def headerhandle(self, data):
        requestdata=data.split('\r\n')
        header=requestdata[0]
        for line in requestdata:
            #print(line)
            if line.startswith("Host:"):
                self.host=line[5:].strip()
                #print("*************"+self.host)
        #print(header)
        method,dir,version=header.split(' ')
        return method.lower(),dir

    def get(self,dir):
        absdir=os.path.abspath(dir)
        abspath=os.path.abspath("./www"+absdir)
        if os.path.exists(abspath):
            if os.path.isfile(abspath):
                self.response(200,abspath)
            else:
                if dir[-1]==('/'):
                    abspath=os.path.abspath(abspath+"/index.html")
                    self.response(200,abspath)
                else:
                    self.redirect(302,dir)
        else:
            self.response(404,ERROR_PATH)

    def response(self,code,path):
        #print("-----------"+path)
        file = open(path, 'r')
        body = file.read()
        mime_type=MIME_TYPE[path.split('.')[-1].lower()]
        response = "HTTP/1.1 %d %s \r\n" %(code,RESPONSE_CODE[code])
        response += "Content-Length: %d \r\n" % len(body)
        response += "Content-Type: %s \r\n" % mime_type
        response += "Connection: close \r\n\r\n"
        response += body+ "\r\n"
        self.request.sendall(response)
        
    def redirect(self,code,path):
        red_path=path+"/"
        response = "HTTP/1.1 %d %s \r\n" % (code, RESPONSE_CODE[code])
        response += "Location: %s \r\n\r\n" % red_path
        self.request.sendall(response)
        
   
    
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
