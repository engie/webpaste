import os
import tempfile
import httplib
import webbrowser

URL = "tiamat:8000"
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

def pixbufToImage( pixbuf ):
    handle, tmp_file_name = tempfile.mkstemp()
    try:
        pixbuf.save( tmp_file_name, "png" )
        data = open(tmp_file_name, "rb").read()
        return data
    finally:
        os.unlink(tmp_file_name)

def getGTKClipboardContents():
    import gtk
    clipboard = gtk.Clipboard()
    targets = clipboard.wait_for_targets()
    if 'image/png' in targets:
        pixbuf = clipboard.wait_for_image()
        return "clipboard.png", "image/png", pixbufToImage( pixbuf ) 

    elif 'text/plain' in targets:
        text = clipboard.wait_for_text()
        return "clipboard.txt", "text/text", text

    raise Exception( "Could not decode clipboard contents" )

def getWin32ClipboardContents():
    """
    With thanks to http://mail.python.org/pipermail/python-list/2003-August/840896.html
    """
    import win32clipboard
    import win32con
    import types
    
    win32clipboard.OpenClipboard()
    types = {} 
    for name, val in win32con.__dict__.items():
        if name[:3] == "CF_" and name != "CF_SCREENFONTS":
            types[val] = name

    targets = []
    enum = 0
    while 1:
        enum = win32clipboard.EnumClipboardFormats( enum )
        if enum == 0:
            break
        if win32clipboard.IsClipboardFormatAvailable( enum ) == False:
            continue

        if not enum in types:
            name = win32clipboard.GetClipboardFormatName( enum )
            types[enum] = name
        targets.append( types[enum] )

    if "CF_BITMAP" in targets:
        import Image
        import ImageGrab
        im = ImageGrab.grabclipboard()

        import StringIO
        output = StringIO.StringIO()
        im.save(output, "PNG")

        return "clipboard.png", "image/png", output.getvalue()

    if "CF_TEXT" in targets:
        data = win32clipboard.GetClipboardData( win32con.CF_TEXT )
        return "clipboard.txt", "text/text", data

def getClipboardContents():
    try:
        import win32clipboard
        return getWin32ClipboardContents()
    except ImportError:
        pass

    try:
        import pygtk
        return getGTKClipboardContents()
    except ImportError:
        pass

if __name__ == "__main__":
    file_name, mime_type, data = getClipboardContents()
    print file_name, mime_type, data
    #webbrowser.open( "http://" + URL + "/" + result )
