import pygtk
import gtk
import os
import tempfile
import httplib
import webbrowser

URL = "localhost:8080"
PAGE = "/"

BOUNDARY = '----------hfoidahfhfodas_$'
CRLF = "\r\n"

def upload( data, filename, mime_type ):
    body  = '--' + BOUNDARY + CRLF
    body += 'Content-Disposition: form-data; name="file"; filename="%s"' % filename + CRLF
    body += 'Content-Type: %s' % mime_type + CRLF
    body += CRLF
    body += data + CRLF
    body += '--' + BOUNDARY + '--' + CRLF
    body += CRLF

    h = httplib.HTTPConnection( URL )
    h.putrequest( "POST", PAGE )
    h.putheader( "Content-Type", 'multipart/form-data; boundary=%s' % BOUNDARY )
    h.putheader( "Content-Length", str(len(body)) )
    h.endheaders()
    h.send(body)
    response = h.getresponse()
    if response.status == 200:
        return response.getheader( "X-File-URL" )
    
    raise Exception( "Upload failed" )

def pixbufToFile( pixbuf ):
    handle, tmp_file_name = tempfile.mkstemp()
    try:
        pixbuf.save( tmp_file_name, "png" )
        data = open(tmp_file_name, "rb").read()
        return data
    finally:
        os.unlink(tmp_file_name)

if __name__ == "__main__":
    clipboard = gtk.Clipboard()
    targets = clipboard.wait_for_targets()

    result = ""
    if 'image/png' in targets:
        pixbuf = clipboard.wait_for_image()
        result = upload( pixbufToFile( pixbuf ), "clipboard.png", "image/png" )
    elif 'text/plain' in targets:
        text = clipboard.wait_for_text()
        result = upload( text, "clipboard.txt", "text/text" )
    else:
        raise Exception( "Could not decode clipboard contents" )

    webbrowser.open( "http://" + URL + "/" + result )
