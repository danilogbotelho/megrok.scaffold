import os.path

import transaction
from zope.interface import implementedBy, implements
import zope.event
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent

from grokcore.component import baseclass
from grokcore import formlib
import grokcore.view as view
from grokcore.view import PageTemplateFile

from z3c.table import table
from megrok import layout

from megrok.scaffold import interfaces
from megrok.scaffold.i18n import ScaffoldMessageFactory as _


default_form_template = PageTemplateFile(os.path.join(
    'templates', 'default_edit_form.pt'))
default_form_template.__grok_name__ = 'default_edit_form'
default_display_template = PageTemplateFile(os.path.join(
    'templates', 'default_display_form.pt'))
default_display_template.__grok_name__ = 'default_display_form'
default_list_template = PageTemplateFile(os.path.join(
    'templates', 'default_list_form.pt'))
default_list_template.__grok_name__ = 'default_list_form'


class BaseForm(object):
    
    __form_type__ = '' 
    __iface__ = None
    
    implements(interfaces.IControlledView)
    
    def __init__(self, context, request):
        self.context, self.request = context, request
        self.controller = self.__controller__(context, self)
    
    @property
    def actions(self):
        actions = self.default_actions
        ctrl_actions = getattr(self.controller, 'actions', [])
        ctrl_type_actions = getattr(self.controller, '%s_actions' % self.__form_type__, [])
        return list(actions)+list(ctrl_actions)+list(ctrl_type_actions)
    
    @property
    def form_fields(self):
        ff = getattr(self.controller, '%s_form_fields' % self.__form_type__, None)
        if not ff:
            ff = getattr(self.controller, 'form_fields', None)
        if not ff:
            ff = formlib.AutoFields(self.__iface__)
        return ff
    
    @property
    def label(self):
        label = getattr(self.controller, '%s_label' % self.__form_type__, None)
        if label is None:
            label = getattr(self.controller, 'label', None)
        return label or u''
    
    @property
    def prefix(self):
        prefix = getattr(self.controller, '%s_prefix' % self.__form_type__, None)
        if prefix is None:
            prefix = getattr(self.controller, 'prefix', None)
        return prefix or ''
    
    def update(self):
        super(BaseForm, self).update()
        update = getattr(self.controller, 'update', None)
        if update: update()
    
    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.__view_name__)
        

class BaseAddForm(BaseForm):
    """Our addforms delegate create, add and nextURL methods to the controller"""
    
    __form_type__ = 'add'
    
    template = default_form_template
    
    @formlib.action(_("Add"))
    def handle_add(self, **data):
        self.createAndAdd(data)

    def createAndAdd(self, data):
        ob = self.create(data)
        zope.event.notify(ObjectCreatedEvent(ob))
        return self.add(ob)
    
    def create(self, data):
        return self.controller.create(data)

    def add(self, object):
        ob = self.controller.add(object)
        self._finished_add = True
        return ob
      
    def nextURL(self):
        nextURL = getattr(self.controller, 'nextURL')
        if nextURL:
            return nextURL()
        #same as formlib's
        return self.context.nextURL()
    
    _finished_add = False
    
    def render(self):
        if self._finished_add:
            self.request.response.redirect(self.nextURL())
            return ""
        return formlib.AddForm.render(self)

class AddForm(BaseAddForm, formlib.AddForm):
    
    def __init__(self, context, request):
        formlib.AddForm.__init__(self, context, request)
        BaseAddForm.__init__(self, context, request)
        

class PageAddForm(BaseAddForm, layout.AddForm):
    def __init__(self, context, request):
        layout.AddForm.__init__(self, context, request)
        BaseAddForm.__init__(self, context, request)
    
    def update_form(self):
        super(PageAddForm, self).update_form()
        if self._finished_add:
            self.request.response.redirect(self.nextURL())

class EditForm(BaseForm, formlib.EditForm):
    
    __form_type__ = 'edit'
    
    template = default_form_template
    
    deleteSuccessMessage = _('Data successfully deleted')
    
    def __init__(self, context, request):
        formlib.EditForm.__init__(self, context, request)
        BaseForm.__init__(self, context, request)
    
    default_actions = formlib.EditForm.actions.copy()
    
    @formlib.action(_(u'Delete'), default_actions, condition=lambda form, self:form.controller.allow_delete)
    def delete(self, **data):
        listview = self.controller.getView('list') or 'index'
        nextURL = self.url(self.context.__parent__, listview)
        self.controller.delete(self.context)
        if not self.status:
            self.status = self.deleteSuccessMessage #FIXME? this won't appear since we redirect
        self.redirect(nextURL)

class PageEditForm(EditForm, layout.Form):
    aspage = True
    
class DisplayForm(BaseForm, formlib.DisplayForm):
        
    __form_type__ = 'display'
    
    template = default_display_template
    
    def __init__(self, context, request):
        formlib.DisplayForm.__init__(self, context, request)
        BaseForm.__init__(self, context, request)
    
    @formlib.action(_(u'Edit'), condition=lambda form, self:form.controller.allow_edit)
    def edit(self, **data):
        self.redirect(self.url(self.context, self.controller.getView('edit')))
    
    @formlib.action(_(u'Delete'), condition=lambda form, self:form.controller.allow_delete)
    def delete(self, **data):
        listview = self.controller.getView('list') or 'index'
        nextURL = self.url(self.context.__parent__, listview)
        self.controller.delete(self.context)
        self.redirect(nextURL)    

class PageDisplayForm(DisplayForm, layout.Form):
    aspage = True

class FormTable(table.Table, formlib.Form):
    
    baseclass()
    
    implements(interfaces.IFormTable)
    template = default_list_template
    
    # table defaults
    cssClasses = {'table': 'contents'}
    cssClassEven = u'even'
    cssClassOdd = u'odd'
    cssClassSelected = u'selected'
    
    status = None # The Tabular stuff checks if the status is None
    
    # internal defaults
    supportsDelete = False
    supportsEdit = False

    deleteErrorMessage = _('Could not delete the selected items')
    deleteNoItemsMessage = _('No items selected for delete')
    deleteSuccessMessage = _('Data successfully deleted')
    
    editTooManyItemsMessage = _("Select only one item for edit") 
    editNoItemsMessage = _("No item selected for edit")

    allowDelete = True
    allowEdit = True
    
    def __init__(self, context, request):
        formlib.Form.__init__(self, context, request)
        table.Table.__init__(self, context, request)
    
    def update(self):
        self.setupConditions()
        super(FormTable, self).update()
    
    def updateAfterActionExecution(self):
        self.setupConditions()
        table.Table.update(self)
    
    def render(self):
        return self._render_template()

    render.base_method = True
    renderFormTable = render
    
    def executeDelete(self, item):
        raise NotImplementedError('Subclass must implement executeDelete')

    def setupConditions(self):
        self.hasContent = bool(self.values) #instead of rows so we can call this before setupRows
        if self.allowDelete:
            self.supportsDelete = self.hasContent
        if self.allowEdit:
            self.supportsEdit = self.hasContent

    def doDelete(self, **data):
        if not len(self.selectedItems):
            self.status = self.deleteNoItemsMessage
            return
        try:
            for item in self.selectedItems:
                self.executeDelete(item)
            self.updateAfterActionExecution()
            self.status = self.deleteSuccessMessage
        except KeyError:
            self.status = self.deleteErrorMessage
            transaction.doom()
    
    def getEditURL(self, item):
        return self.url(item, self.controller.getView('edit'))
    
    @formlib.action(_('Edit'), condition=lambda form, self:form.supportsEdit)
    def edit(self, **data):
        if not len(self.selectedItems):
            self.status = self.editNoItemsMessage
            return
        if len(self.selectedItems) > 1:
            self.status = self.editTooManyItemsMessage
            return
        self.redirect(self.getEditURL(self.selectedItems[0]))
    
    @formlib.action(_('Delete'), name='delete',
                             condition=lambda form, self:form.supportsDelete)
    def handleDelete(self, **data):
        self.doDelete(**data)

class CheckBoxColumn(table.column.CheckBoxColumn):
    cssClasses = {'th': 'xcol'}
    
    def renderCell(self, item):
        selected = u''
        if item in self.selectedItems:
            selected='checked="checked"'
        return u'<input type="checkbox" class="%s" name="%s" value="%s" %s />' \
            %('checkbox-widget xcol', self.getItemKey(item), self.getItemValue(item),
            selected)

class GetAttrLinkColumn(table.column.LinkColumn, table.column.GetAttrColumn):
    
    def updateLinks(self, item):
        self.linkContent = self.getValue(item)
        self.linkName = self.table.controller.getView('display') 
    
    def renderCell(self, item):
        self.updateLinks(item)
        return table.column.LinkColumn.renderCell(self, item)

class ListForm(BaseForm, FormTable):
    
    baseclass()
    
    __form_type__ = 'list'
    
    default_actions = FormTable.actions.copy()
    
    def __init__(self, context, request):
        FormTable.__init__(self, context, request)
        BaseForm.__init__(self, context, request)
        
        self.batchSize = self.controller.batch_size
        self.startBatchingAt = self.controller.start_batching_at
    
    @property
    def values(self):
        return self.controller.list()
        
    def render(self):
        return self.renderFormTable()
    
    @property
    def link_columns(self):
        return self.controller.link_columns
    
    def setUpColumns(self):
        cols = []
        if self.availableActions():
            cols.append(table.column.addColumn(self, CheckBoxColumn, u'item', weight=-1))
        for field in self.form_fields:
            field_name = field.__name__
            if field_name in self.link_columns:
                BaseColumn = GetAttrLinkColumn
            else:
                BaseColumn = table.column.GetAttrColumn
            class GetFieldColumn(BaseColumn):
                attrName = field_name
            cols.append(table.column.addColumn(self, GetFieldColumn, field_name, header=field_name.capitalize()))        
        return cols
    
    @property
    def allowDelete(self):
        return self.controller.allow_delete
    
    @property
    def allowEdit(self):
        return self.controller.allow_edit
    
    def executeDelete(self, item):
        self.controller.delete(item)
    
    def getEditURL(self, item):
        return self.url(item, self.controller.getView('edit'))

class PageListForm(ListForm, layout.Form):
    aspage = True
    