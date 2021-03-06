from wsgiref import simple_server
import mimetypes
import os, os.path
import re
import hashlib
import cgi

ROOT_REDIRECT_URL = 'http://github.com/engie/webpaste'
#Image from http://www.openclipart.org/detail/32347
FAVICON = 'paste.png'
UPLOADS_DIR = 'uploads'

BASIC_UPLOAD_FORM = """<html>
<head>
<title>Web Paste Uploader</title>
</head>
<body>
<h1>Web Paste Uploader</h1>
<p>Share a file by uploading it to the server.</p>
<form method="POST" enctype="multipart/form-data">
<p><input type="file" name="file"/></br>
<input type="submit"></p>
</form>
<p>See <a href="%s">%s</a> for more information.</p>
</body>
</html>""" % (ROOT_REDIRECT_URL, ROOT_REDIRECT_URL)

def getSuccessPage( filename ):
    return """<html>
    <head>
    <title>Wab Paste Uploader</title>
    </head>
    <body>
    <h1>File Successfully Uploaded</h1>
    <p><a href="%s">%s</a></p>
    <p><a href="/">Upload Another</a></p>
    </body>
    </html>""" % (filename, filename)

EXTENSION_FILTER = re.compile('^\.[a-zA-Z0-9]{1,20}$')
ERROR_404 = '404 File Not Found'
DEFAULT_EXTENSION = ''
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

def saveFile( filename, data ):
    if filename != None:
        extension = os.path.splitext( filename )[1]
        if EXTENSION_FILTER.match( extension ) == None:
            extension = DEFAULT_EXTENSION
    else:
        extension = DEFAULT_EXTENSION

    sha = hashlib.sha256()
    sha.update( data )
    
    #Turn the hash into a hex string
    hash = "".join([hex(ord(x))[2:] for x in sha.digest()])

    new_file_name = hash + extension
    new_file_path = os.path.join( UPLOADS_DIR, new_file_name )
    
    open( new_file_path, "wb" ).write( data )
    return new_file_name

def paste( environ, start_response ):
    global stderr
    stderr = environ['wsgi.errors']

    #Get uploaded files
    method = environ["REQUEST_METHOD"]
    if method == "GET":
        path = environ["PATH_INFO"][1:]
        #Show a html upload form for basic browser access
        if path == "" or path == "index.html" or path == "index.htm":
            start_response( '200 OK', [('Content-type', "text/html")] )
            return [ BASIC_UPLOAD_FORM ]
        #Serve up a favicon
        elif path == "favicon.ico":
            try:
                icon = open(FAVICON, "rb").read()
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
                data = open( fullpath, "rb" ).read()
                start_response( '200 OK', [('Content-type', getContentType( fullpath ))] )
                return [ data ]
            else:
                start_response( ERROR_404, [] )
                return []
    elif method == "POST":
        post = cgi.FieldStorage( fp = environ['wsgi.input'],
                                environ = environ,
                                keep_blank_values = True )
        fileitem = post["file"]
        if fileitem == None or fileitem.file == None:
            raise Exception("Upload not found in form.")

        filename = saveFile( fileitem.filename, fileitem.file.read() )
        start_response( '200 OK', [('Content-Type', "text/html"),
                                   ('X-File-URL', filename)] )
        return [ getSuccessPage( filename ) ]
    else:
        start_response( ERROR_404, [] )
        return []

if __name__ == '__main__':
    httpd = simple_server.make_server( '', 8080, paste )
    httpd.serve_forever()
