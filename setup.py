from distutils.core import setup
import py2exe

setup(console=['upload.py'],
      options = { "py2exe" : { "excludes" : ["pygtk", "gtk"] } })