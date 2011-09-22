import unittest
import doctest
from grokcore.component.testing import grok_component
from grokcore.content import Model, Container

import megrok.scaffold.tests

FunctionalLayer = megrok.scaffold.tests.MegrokScaffoldLayer(megrok.scaffold.tests)

def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    getRootFolder = FunctionalLayer.getRootFolder
    globs = {
             'grok_component': grok_component, 
             '__name__': 'megrok.scaffold',
             'Model': Model,
             'Container': Container,
             'getRootFolder': getRootFolder
    }
    suite = unittest.TestSuite()
    
    readme = doctest.DocFileSuite(
            '../README.txt',
            optionflags=optionflags,
            globs=globs)
    readme.layer = FunctionalLayer
    suite.addTest(readme)
    
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')