import martian
from martian import util
from martian.error import GrokError
from martian.util import scan_for_classes
from grokcore.security import components


#actions don't need validation now since:
#1. fields may be provided by controller's TYPE_form_fields attribute
#2. factory may be provided by controller's factory attribute (for add form)
#3. context may be adapted (like (object, form_fields interface) in edit form)
#def validate(component):
#    if isinstance(component, InterfaceClass): return
#    ifaces = list(implementedBy(component))
#    if len(ifaces) < 1:
#        raise


SCAFFOLD_ACTIONS = 'add', 'edit', 'display', 'list'
SCAFFOLD_VIEWS = 'addname', 'editname', 'displayname', 'listname'
SCAFFOLD_OPTS = SCAFFOLD_ACTIONS + SCAFFOLD_VIEWS + ('aspage', )

class scaffold(martian.Directive):
    """
        scaffold(False)
        scaffold(IInterface)
        scaffold(IInterface, add=IAddInterface)
        scaffold(add=IAddInterface)
        scaffold(IInterface, edit=False)
        scaffold(add=IAddInterface, edit=IEditInterface)
        scaffold(ModelClass)
    """
    scope = martian.CLASS
    store = martian.ONCE
    
    def factory(self, all=None, **kw):
        values = {}
        
        for k in kw:
            if k not in SCAFFOLD_OPTS:
                raise TypeError("scaffold: Unexpected keyword argument '%s'" % k)
        
        values['add'] = all
        values['edit'] = all
        values['display'] = all
        values['list'] = all
        
        values['aspage'] = kw.get('aspage', False)
        
        for n, action in enumerate(SCAFFOLD_ACTIONS):
            if action in kw:
                act = kw[action]
                if not act:
                    del values[action]
                else:
                    if act != True:
                        values[action] = act
                    #validate(values[action])
            actionname =  SCAFFOLD_VIEWS[n]
            if actionname in kw:
                if values.get(action, None) is None:
                    raise
                values[actionname] = kw[actionname] 
        
        actions = [x for x in SCAFFOLD_ACTIONS if x in values]
        if all is None and not actions:
            raise ValueError("scaffold: Either False or component (interface or factory) must be provided")
        if all == False and actions:
            raise ValueError("scaffold arguments conflict")
        
        return values
    
    @classmethod
    def get_default(cls, component, module=None, **data):
        components = list(scan_for_classes(module, IContext))
        if len(components) == 0:
            raise GrokError(
                "No module-level model for %r, please use the 'scaffold' "
                "directive." % (component), component)
        elif len(components) == 1:
            component = components[0]
        else:
            raise GrokError(
                "Multiple possible models for %r, please use the 'scaffold' "
                "directive."
                % (component), component)
        return dict.fromkeys(SCAFFOLD_ACTIONS, component)
                 
class require(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE

    def validate(self, all=None, **kw):
        items = list(kw.items())
        if all is not None:
            items += [('all', all)]
        for action, value in kw.items():
            if util.check_subclass(value, components.Permission):
                continue
            if util.not_unicode_or_ascii(value):
                raise GrokImportError(
                    "You can only pass unicode, ASCII, or a subclass "
                    "of grok.Permission to the '%s' directive." % self.name)

    def factory(self, all=None, **kw):
        values = {}
        
        if all is not None:
            if util.check_subclass(all, components.Permission):
                all = grokcore.component.name.bind().get(all)
            for action in SCAFFOLD_ACTIONS:
                values[action] = all
                
        for action, value in kw.items():
            if util.check_subclass(value, components.Permission):
                value = grokcore.component.name.bind().get(value)
            values[action] = value
        return values
        
            