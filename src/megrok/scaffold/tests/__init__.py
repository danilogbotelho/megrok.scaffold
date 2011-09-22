from zope.component.testlayer import ZCMLFileLayer
from zope.app.wsgi.testlayer import BrowserLayer

class MegrokScaffoldLayer(BrowserLayer, ZCMLFileLayer):
    pass