#
import sys

from zope import interface, component
from zope.publisher.interfaces.browser import IDefaultBrowserLayer, IBrowserPage, IBrowserPublisher
from zope.publisher.interfaces.http import IHTTPRequest 

import martian
import grokcore.component
import grokcore.view
import grokcore.security
from grokcore.security.util import protect_getattr

from megrok.scaffold import components, directive, forms

def default_controller_name(component, module=None, **data):
    return component.__name__.lower()

class ControllerGrokker(martian.ClassGrokker):
    martian.component(components.Controller)
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name, get_default=default_controller_name)
    martian.directive(directive.scaffold)
    martian.directive(directive.require, name='permissions', default={})

    def execute(self, factory, config, context, name, layer, scaffold, permissions):
        
        ret_code = False
        for action in ['add', 'edit', 'display', 'list']:
            if scaffold.get(action, False):
                executer = getattr(self, 'exec_%s' % action)
                ret = executer(factory, config, context,
                    layer, scaffold.get('%sname' % action, None), 
                    scaffold[action], scaffold['aspage'], permissions.get(action, None))
                ret_code = ret_code or ret

        return ret_code

    def exec_add(self, factory, config, context, layer, name, iface, aspage, permission):
        if not name:
            name = 'add%s' % getattr(iface, '__name__', str(iface)).lower()
        
        factory.__views__['add'] = name
        
        BaseForm = forms.PageAddForm if aspage else forms.AddForm
        
        class AddForm(BaseForm):
            __view_name__ = name #needed to support IAbsoluteURL on views
            __iface__ = iface
            __controller__ = factory
        
        form = AddForm
        adapts = (context, layer)

        config.action(
            discriminator=('adapter', adapts, interface.Interface, name),
            callable=component.provideAdapter,
            args=(form, adapts, interface.Interface, name),
            )
        
        for method_name in IBrowserPage:
            config.action(
                discriminator=('protectName', form, method_name),
                callable=protect_getattr,
                args=(form, method_name, permission),
                )
        
        return True
    
    def exec_list(self, factory, config, context, layer, name, iface, aspage, permission):
        if not name:
            name = 'list%s' % getattr(iface, '__name__', str(iface)).lower()
        
        factory.__views__['list'] = name
        
        BaseForm = forms.PageListForm if aspage else forms.ListForm
        
        class ListForm(BaseForm):
            __view_name__ = name
            __iface__ = iface
            __controller__ = factory
        
        form = ListForm
        adapts = (context, layer)
        
        config.action(
            discriminator=('adapter', adapts, interface.Interface, name),
            callable=component.provideAdapter,
            args=(form, adapts, interface.Interface, name),
            )
        
        for method_name in IBrowserPage:
            config.action(
                discriminator=('protectName', form, method_name),
                callable=protect_getattr,
                args=(form, method_name, permission),
                )
        return True
    
    def exec_edit(self, factory, config, context, layer, name, iface, aspage, permission):
        if not name:
            name = 'edit'
        
        factory.__views__['edit'] = name
        
        BaseForm = forms.PageEditForm if aspage else forms.EditForm
        
        class EditForm(BaseForm):
            __view_name__ = name
            __iface__ = iface
            __controller__ = factory
        
        form = EditForm
        adapts = (iface, layer)
        
        config.action(
            discriminator=('adapter', adapts, interface.Interface, name),
            callable=component.provideAdapter,
            args=(form, adapts, interface.Interface, name),
            )
        
        for method_name in IBrowserPage:
            config.action(
                discriminator=('protectName', form, method_name),
                callable=protect_getattr,
                args=(form, method_name, permission),
                )
        
        return True
    
    def exec_display(self, factory, config, context, layer, name, iface, aspage, permission):
        if not name:
            name = 'index'
        
        factory.__views__['display'] = name
        
        BaseForm = forms.PageDisplayForm if aspage else forms.DisplayForm
        
        class DisplayForm(BaseForm):
            __view_name__ = name
            __iface__ = iface
            __controller__ = factory
        
        form = DisplayForm
        adapts = (iface, layer)
        
        config.action(
            discriminator=('adapter', adapts, interface.Interface, name),
            callable=component.provideAdapter,
            args=(form, adapts, interface.Interface, name),
            )
        
        for method_name in IBrowserPage:
            config.action(
                discriminator=('protectName', form, method_name),
                callable=protect_getattr,
                args=(form, method_name, permission),
                )
        
        return True
        
