from zope.interface import Interface, Attribute
import z3c.table.interfaces

class IController(Interface):
    """A controller"""
    
    view = Attribute("""A reference to the View being accessed""")
    
    form_fields = Attribute(
        """The form's form field definitions
    
        Optional. Only used if a specific TYPE_form_fields is not defined. 
        """)
    
    add_form_fields = Attribute("""The add form's form field definitions""")
    
    display_form_fields = Attribute("""The display form's form field definitions""")
    
    edit_form_fields = Attribute("""The edit form's form field definitions""")
    
    list_form_fields = Attribute("""The list form's form field definitions""")
    
    label = Attribute(
        """A label to display at the top of a form
        
        Optional. Only used if a specific TYPE_label is not defined.
        """)
    
    add_label = Attribute("""A label to display at the top of an add form""")
    
    display_label = Attribute("""A label to display at the top of a display form""")
    
    edit_label = Attribute("""A label to display at the top of an edit form""")
    
    list_label = Attribute("""A label to display at the top of a list form""")
    
    factory = Attribute(
        """The callable used to instantiate model (used by the add form)
    
        If not specified the view's __iface__ will be tried.
        """)
    
    modelname = Attribute("""The name of the model (used in views)""")
    
    request = Attribute("""The request""")
    
    context = Attribute("""The view's context """)
    
    allow_edit = Attribute("""Flag to determine whether an Edit action is available in the form""")
    
    allow_delete = Attribute("""Flag to determine whether a Delete action is available in the form""")
    
    actions = Attribute("""Action collection for ALL forms (class level)""")
    
    add_actions = Attribute("""Action collection for edit forms (class level)""")
    
    display_actions = Attribute("""Action collection for display forms (class level)""")
    
    edit_actions = Attribute("""Action collection for edit forms (class level)""")
    
    list_actions = Attribute("""Action collection for list forms (class level)""")
    
    link_columns = Attribute("""Names of the fields which will link to content in a list form""")
    
    start_batching_at = Attribute("""Number of rows after wich list form will start paginating at""")
    
    batch_size = Attribute("""Amount of rows per page in a list form""")
    
    def getView(type):
        """Return the name of the view registered for type
        
        Type may be one of list, display, add or edit
        
        """
    
    def create(data):
        """If the add view has been registered this is called to create the 
        object
        
        """
    
    def add(obj):
        """If the add view has been registered this is called to store the 
        created object
        
        """
    
    def nextURL():
        """If the add view has been registered this is called to determine 
        the url the client will be redirected to after object creation"""
    
    def list():
        """If the list view has been registered this is called to determine the
        objects to display."""
    
    def delete(item):
        """This method is called to remove item from its container"""
    
    def update():
        """Form update hook"""

class IControlledView(Interface):
    """A view that is attached to a controller"""
    
    __form_type__ = Attribute("""A string to identify the kind of form, like 'add', 'edit' etc.""")
    
    __iface__ = Attribute("""A reference to the model or interface being scaffolded""")
    
    __controller__ = Attribute("""A reference to the controller factory""")
    
    controller = Attribute("""A reference to the controller instance attached to this view""")

#===============================================================================
# Form Table (borrowed from z3c.tabular and megrok.z3cform.tabular)
#===============================================================================

class ITemplateTable(z3c.table.interfaces.ITable):
    """Template aware table."""

class IFormTable(ITemplateTable):
    """Table including a form setup."""

class IDeleteFormTable(IFormTable):
    """Delete button aware table including a form setup."""
    
        