Introduction
============

Scaffolding allows you to auto-generate forms for models. The goal is to create 
commonly used forms without much boilerplate while still allowing for deeper 
customizations.

.. contents::

Before we can start using scaffolding, we must create the content to work with:

Models
------

  >>> import grokcore.component as grok
  >>> from zope.interface import Interface
  >>> from zope import schema

  >>> class IMammoth(Interface):
  ...    name = schema.TextLine(title=u"Name")
  ...    age = schema.Int(title=u"Age")

  >>> class Mammoth(Model):
  ...    grok.implements(IMammoth)
  ...    name = schema.fieldproperty.FieldProperty(IMammoth['name'])
  ...    age = schema.fieldproperty.FieldProperty(IMammoth['age'])

  >>> class HerdContainer(Container):
  ...    pass

Now all we have to do is create a controller:

Whole application in a few lines
--------------------------------

  >>> from megrok.scaffold import Controller, scaffold
  
  >>> class MammothController(Controller):
  ...     grok.context(HerdContainer)
  ...
  ...     scaffold(Mammoth)

That's it. And we have an add form, an edit form, display 'form' and a list 
view. With deletion enabled.

Let's verify that.

Grokking and querying
---------------------

We let Grok register the component::

  >>> grok_component('mammothcontroller', MammothController)
  True

Now, we can query it normally::

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> herd = HerdContainer()
  >>> getRootFolder()['herd'] = herd
  >>> manfred = Mammoth()
  >>> herd['manfred'] = manfred

  >>> from zope.component import getMultiAdapter
  >>> editform = getMultiAdapter((manfred, request), name="edit")

  >>> editform
  <EditForm 'edit'>
  >>> print editform()
  <html xmlns="http://www.w3.org/1999/xhtml">
  <body>
  <div id="edit-mammoth" class="scaffold-edit">
  <form action="http://127.0.0.1" method="post"
      class="edit-form" enctype="multipart/form-data">
  ...

  >>> displayform = getMultiAdapter((manfred, request), name="index")
  >>> displayform
  <DisplayForm 'index'>

  >>> addform = getMultiAdapter((herd, request), name="addmammoth")
  >>> addform
  <AddForm 'addmammoth'>

  >>> listform = getMultiAdapter((herd, request), name="listmammoth")
  >>> listform
  <ListForm 'listmammoth'>

Layout integration
------------------

First, let's unregister the previous forms to start it anew::

 >>> from zope.component import getGlobalSiteManager
 >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
 >>> from zope.interface import implementedBy
 >>> sm = getGlobalSiteManager()
 >>> def unregister_views():
 ...     done = sm.unregisterAdapter(None, (implementedBy(Mammoth), 
 ...         IDefaultBrowserLayer), Interface, 'edit')
 ...     done = done and sm.unregisterAdapter(None, (implementedBy(Mammoth), 
 ...         IDefaultBrowserLayer), Interface, 'index')
 ...     done = done and sm.unregisterAdapter(None, (implementedBy(HerdContainer), 
 ...         IDefaultBrowserLayer), Interface, 'addmammoth')
 ...     done = done and sm.unregisterAdapter(None, (implementedBy(HerdContainer), 
 ...         IDefaultBrowserLayer), Interface, 'listmammoth')
 ...     return done
 >>> unregister_views()
 True

Now, simply define the layout as usual::

  >>> from megrok.layout import Layout
  >>> class MyLayout(Layout):
  ...     grok.name('mylayout')
  ...     grok.context(Interface)
  ...
  ...     def render(self):
  ...         return u"A simple layout\n%s" % self.view.content()
  >>> grok_component('MyLayout', MyLayout)
  True

And tell the scaffolding grokker to register the forms as layout pages::

  >>> class MammothController(Controller):
  ...     grok.context(HerdContainer)
  ...
  ...     scaffold(Mammoth, aspage=True)
  
  >>> grok_component('mammothcontroller', MammothController)
  True
  >>> editform = getMultiAdapter((manfred, request), name="edit")
  >>> print editform()
  A simple layout
  <div id="edit-mammoth" class="scaffold-edit">
  <form action="http://127.0.0.1" method="post"
      class="edit-form" enctype="multipart/form-data">
  ...

Customization
=============

The names of the views can be configured using parameters passed to the scaffold directive, e.g.::

  >>> class MammothController(Controller):
  ...     grok.context(HerdContainer)
  ...
  ...     scaffold(Mammoth, addname='add', editname='edit', displayname='index', listname='index')

Besides this, the interfaces used for each form can be set as well::

  >>> class IListMammoth(Interface):
  ...     name = schema.TextLine(title=u"Mammoth's name")

  >>> class MammothController(Controller):
  ...     grok.context(HerdContainer)
  ...
  ...     scaffold(add=Mammoth, edit=IMammoth, list=IListMammoth, display=IMammoth)

One can easily disable the automatic registering of views::

  >>> class MammothController(Controller):
  ...     grok.context(HerdContainer)
  ...
  ...     scaffold(Mammoth, list=False)

Putting it all together::

  >>> class MammothController(Controller):
  ...     grok.context(HerdContainer)
  ...
  ...     scaffold(Mammoth, list=IListMammoth, listname='index', edit=False, aspage=True)

The latter will register::
  
- an add form named after the model's name ('addmammoth')
- a display form named 'index'
- a list view named 'index' displaying the fields defined in IListMammoth
- no edit form

  >>> unregister_views()
  True
  >>> grok_component('mammothcontroller', MammothController)
  True
  >>> getMultiAdapter((herd, request), name="index")
  <ListForm 'index'>
  >>> editform = getMultiAdapter((manfred, request), name="edit")
  Traceback (most recent call last):
    ...
  ComponentLookupError:

Actions
-------

Each form have a subset of these common actions: 'add', 'edit', 'apply', 'delete'.
 Some can be activated or deactivated using attributes like 'allow_edit' and 'allow_delete'.

Your own custom actions can be created using formlib's action decorator::

  >>> from grokcore.formlib import action

  >>> class MammothController(Controller):
  ...     grok.context(HerdContainer)
  ...
  ...     scaffold(Mammoth, listname='index')
  ...
  ...     allow_delete = False
  ...
  ...     @action('Cancel')
  ...     def cancel(self, **data):
  ...         pass
  ...
  ...     list_actions = Controller.list_actions.copy()
  ...
  ...     @action('Import', list_actions)
  ...     def do_import(self, **data):
  ...         self.redirect(self.url(self.context, 'import_view'))

  >>> unregister_views()
  True
  >>> grok_component('mammothcontroller', MammothController)
  True
  >>> listform = getMultiAdapter((herd, request), name="index")
  >>> html = listform()
  >>> print listform() # doctest: +NORMALIZE_WHITESPACE
  1
  <input type="submit" class="button" value="Import" name="actions.import" id="actions.import">

Security
========

By default the views registered have no permissions set. To change that use the
 megrok.scaffold's 'require' directive::

  >>> from megrok.scaffold import require as scaffold_require 
  
  >>> class MammothController(Controller):
  ...     grok.context(HerdContainer)
  ...
  ...     scaffold(Mammoth)
  ...     scaffold_require(add='zope.ManageContent', edit='zope.ManageContent')

API
===

See interfaces.py module.