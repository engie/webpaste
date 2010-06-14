webpaste - Single button sharing
================================
Webpaste is a pair of client/server scripts for easily sharing the contents of your clipboard on the web. If paste.py is available on a server, running upload.py will upload the contents of your clipboard. You will then be shown the uploaded info in your web browser and you can share the link over email / im / etc.

Works So Far
------------
* Basic server that accepts uploads, serves a basic upload form and serves uploaded files
* Basic client for Gnome based systems that uploads the current clipboard contents

TODO
----
* Create clients for other OS's (Win32, KDE, OSX)
* Make the clients run as background / system tray tasks that respond to a hotkey
* Delete files from the server after a period of time or if storage requirements get too high

WontFix
-------
* Access control - this is a headache better managed at the server layer
