from setuptools import setup, find_packages
import os

version = '0.2'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

install_requires = [
    'setuptools',
    'martian',
    'grokcore.component',
    'grokcore.security',
    'grokcore.view >= 1.12',
    'grokcore.formlib',
    'z3c.table >= 0.8',
]

test_requires = install_requires + [
    'zope.browserpage',
    'zope.configuration',
    'zope.container',
    'zope.interface',
    'zope.security',
    'zope.publisher',
    'zope.traversing',
    'zope.testing',
    'zope.securitypolicy',
    'zope.principalregistry',
    'zope.app.wsgi',
    'grokcore.content',
    'megrok.layout',
    ]

setup(name='megrok.scaffold',
      version=version,
      description="Auto-generate CRUD forms for a given domain class.",
      long_description=(
        read('src', 'megrok', 'scaffold', 'README.txt')
        + '\n\n' + 
        read('HISTORY.txt')
      ),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'
        ],
      keywords='CRUD form auto model scaffold',
      author='Danilo G. Botelho',
      author_email='danilogbotelho@yahoo.com',
      url='http://pypi.python.org/pypi/megrok.scaffold',
      license='GPL',
      packages=find_packages('src'),
      namespace_packages=['megrok'],
      include_package_data=True,
      package_dir={'': 'src'},
      zip_safe=False,
      install_requires=install_requires,
      extras_require={'test': test_requires},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
