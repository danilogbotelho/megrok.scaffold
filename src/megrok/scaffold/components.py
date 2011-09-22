import string

from zope.interface import implements
from zope.interface.interfaces import IInterface

import martian

from zope.formlib.form import Actions

from megrok.scaffold.interfaces import IController
from megrok.scaffold.i18n import ScaffoldMessageFactory as _ 

class Controller(object):
    implements(IController)
    
    view = None
    prefix = ''
    
    __views__ = {}
    
    batch_size = 25
    start_batching_at = 25
    
    allow_edit = True
    allow_delete = True
    allow_cancel = True
    
    add_actions = Actions()
    list_actions = Actions()
    edit_actions = Actions()
    display_actions = Actions()
    
    def __init__(self, context, view):
        super(Controller, self).__init__()
        self.context = context
        self.view = view
    
    def __repr__(self):
        return "<Controller model='%r'>" % self.view.__iface__
    
    @property
    def request(self):
        return self.view.request
    
    @property
    def modelname(self):
        name = ''
        try:
            name = self.getFactory().__name__
        except:
            name = self.view.__iface__.__name__
            if name.startswith('I'): name = name[1:]
        new_name = []
        for c in name:
            if c in string.ascii_uppercase:
                new_name.append(' ')
            new_name.append(c)
        return "".join(new_name).strip()
    
    @property
    def add_label(self):
        return _('Add %s' % self.modelname)
    
    @property
    def display_label(self):
        return _('Display %s' % self.modelname)
    
    @property
    def edit_label(self):
        return _('Edit %s' % self.modelname)
    
    @property
    def list_label(self):
        return _('%s List' % self.modelname)
    
    def getView(self, type):
        return self.__views__.get(type, None)
    
    def getFactory(self):
        component = getattr(self, 'factory', None)
        if not component:
            component = self.view.__iface__
            if not martian.util.isclass(component):
                raise NotImplementedError("No factory provided for %r" % self.view.__iface__)
        return component
    
    def create(self, data):
        factory = self.getFactory()
        try:
            obj = factory()
            self.view.applyData(obj, **data)
        except TypeError:
            obj = factory(**data)
        return obj
    
    def add(self, item):
        add = getattr(self.context, 'add', None)
        if add:
            ob = add(item)
        else:
            n = 1
            while True:
                try:
                    self.context[str(n)] = item
                    break
                except:
                    n+=1
        ob = self.context[str(n)]
        self._nextURL = self.view.url(ob)
    
    def nextURL(self):
        return self._nextURL
    
    def list(self):
        if martian.util.isclass(self.view.__iface__):
            return self.context.values()
        else:
            return [x for x in self.context.values() if self.view.__iface__.providedBy(x)]
    
    @property
    def link_columns(self):
        for field in self.view.form_fields:
            return [field.__name__]
    
    def delete(self, item):
        del item.__parent__[item.__name__]
