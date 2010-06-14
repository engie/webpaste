from wsgiref import simple_server
import mimetypes
import os
import cgi

ROOT_REDIRECT_URL = 'http://github.com/engie/webpaste'
#Image from http://www.openclipart.org/detail/32347
FAVICON = 'paste.png'
UPLOADS_DIR = 'uploads'

ERROR_404 = '404 File Not Found'

stderr = None

def getFileList():
    try:
        return os.listdir( UPLOADS_DIR )
    except:
        stderr.write("Could not enumerate uploads directory")
        return []

def getContentType( filename ):
    file_type, file_encoding = mimetypes.guess_type( filename )
    if file_type != None:
        return file_type
    else:
        return 'application/octet-stream'

def paste( environ, start_response ):
    global stderr
    stderr = environ['wsgi.errors']

    #Get uploaded files
    if environ["REQUEST_METHOD"] == "GET":
        path = environ["PATH_INFO"][1:]
        #Redirect root requests to some useful info
        if path == "" or path == "index.html" or path == "index.htm":
            start_response( '303 See Other', [('Location', ROOT_REDIRECT_URL)] )
            return []
        #Serve up a favicon
        elif path == "favicon.ico":
            try:
                icon = open(FAVICON).read()
                start_response( '200 OK', [('Content-type', 'image/png')] )
                return [icon]
            except IOError:
                start_response( ERROR_404, [] )
                return []
        else:
            #Look for file
            filename = environ["PATH_INFO"][1:]
            if filename in getFileList():
                fullpath = os.path.join( UPLOADS_DIR, filename )
                data = open( fullpath ).read()
                start_response( '200 OK', [('Content-type', getContentType( fullpath )),
                                           ('Content-Length', str(len(data)))] )
                return [ data ]
            else:
                start_response( ERROR_404, [] )
                return []
    else:
        post = cgi.FieldStorage( fp = environ['wsgi.input'],
                                environ = environ,
                                keep_blank_values = True )
        start_response( '200 OK', [('Content-type', 'application/json')] )
        return ['Hi there']

if __name__ == '__main__':
    httpd = simple_server.make_server( '', 8080, paste )
    httpd.serve_forever()
