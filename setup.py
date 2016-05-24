# -*- coding: utf-8 -*-

# Import early to make sure things are patched up properly
from setuptools import setup, find_packages

import os
import sys
import platform

if sys.version_info < (2, 7):
    raise Exception('RhodeCode requires Python 2.7 or later')


here = os.path.abspath(os.path.dirname(__file__))


def _get_meta_var(name, data, callback_handler=None):
    import re
    matches = re.compile(r'(?:%s)\s*=\s*(.*)' % name).search(data)
    if matches:
        if not callable(callback_handler):
            callback_handler = lambda v: v

        return callback_handler(eval(matches.groups()[0]))

_meta = open(os.path.join(here, 'rhodecode', '__init__.py'), 'rb')
_metadata = _meta.read()
_meta.close()

callback = lambda V: ('.'.join(map(str, V[:3])) + '.'.join(V[3:]))
__version__ = open(os.path.join('rhodecode', 'VERSION')).read().strip()
__license__ = _get_meta_var('__license__', _metadata)
__author__ = _get_meta_var('__author__', _metadata)
__url__ = _get_meta_var('__url__', _metadata)
# defines current platform
__platform__ = platform.system()

# Cygwin has different platform identifiers, but they all contain the
# term "CYGWIN"
is_windows = __platform__ == 'Windows' or 'CYGWIN' in __platform__

requirements = [
    'Babel',
    'Beaker',
    'FormEncode',
    'Mako',
    'Markdown',
    'MarkupSafe',
    'MySQL-python',
    'Paste',
    'PasteDeploy',
    'PasteScript',
    'Pygments',
    'Pylons',
    'Pyro4',
    'Routes',
    'SQLAlchemy',
    'Tempita',
    'URLObject',
    'WebError',
    'WebHelpers',
    'WebHelpers2',
    'WebOb',
    'WebTest',
    'Whoosh',
    'alembic',
    'amqplib',
    'anyjson',
    'appenlight-client',
    'authomatic',
    'backport_ipaddress',
    'celery',
    'colander',
    'decorator',
    'docutils',
    'infrae.cache',
    'ipython',
    'iso8601',
    'kombu',
    'msgpack-python',
    'packaging',
    'psycopg2',
    'pycrypto',
    'pycurl',
    'pyparsing',
    'pyramid',
    'pyramid-debugtoolbar',
    'pyramid-mako',
    'pyramid-beaker',
    'pysqlite',
    'python-dateutil',
    'python-ldap',
    'python-memcached',
    'python-pam',
    'recaptcha-client',
    'repoze.lru',
    'requests',
    'simplejson',
    'waitress',
    'zope.cachedescriptors',
]

if is_windows:
    pass
else:
    requirements.append('psutil')
    requirements.append('py-bcrypt')

test_requirements = [
    'WebTest',
    'configobj',
    'cssselect',
    'flake8',
    'lxml',
    'mock',
    'pytest',
    'pytest-runner',
]

setup_requirements = [
    'PasteScript',
    'pytest-runner',
]

dependency_links = [
]

classifiers = [
    'Development Status :: 6 - Mature',
    'Environment :: Web Environment',
    'Framework :: Pylons',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
]


# additional files from project that goes somewhere in the filesystem
# relative to sys.prefix
data_files = []

# additional files that goes into package itself
package_data = {'rhodecode': ['i18n/*/LC_MESSAGES/*.mo', ], }

description = ('RhodeCode is a fast and powerful management tool '
               'for Mercurial and GIT with a built in push/pull server, '
               'full text search and code-review.')

keywords = ' '.join([
    'rhodecode', 'rhodiumcode', 'mercurial', 'git', 'code review',
    'repo groups', 'ldap', 'repository management', 'hgweb replacement',
    'hgwebdir', 'gitweb replacement', 'serving hgweb',
])

# long description
README_FILE = 'README.rst'
CHANGELOG_FILE = 'CHANGES.rst'
try:
    long_description = open(README_FILE).read() + '\n\n' + \
        open(CHANGELOG_FILE).read()

except IOError, err:
    sys.stderr.write(
        '[WARNING] Cannot find file specified as long_description (%s)\n or '
        'changelog (%s) skipping that file' % (README_FILE, CHANGELOG_FILE)
    )
    long_description = description

# packages
packages = find_packages()

paster_commands = [
    'make-config=rhodecode.lib.paster_commands.make_config:Command',
    'setup-rhodecode=rhodecode.lib.paster_commands.setup_rhodecode:Command',
    'update-repoinfo=rhodecode.lib.paster_commands.update_repoinfo:Command',
    'cache-keys=rhodecode.lib.paster_commands.cache_keys:Command',
    'ishell=rhodecode.lib.paster_commands.ishell:Command',
    'upgrade-db=rhodecode.lib.dbmigrate:UpgradeDb',
    'celeryd=rhodecode.lib.celerypylons.commands:CeleryDaemonCommand',
]

setup(
    name='rhodecode-enterprise-ce',
    version=__version__,
    description=description,
    long_description=long_description,
    keywords=keywords,
    license=__license__,
    author=__author__,
    author_email='marcin@rhodecode.com',
    dependency_links=dependency_links,
    url=__url__,
    install_requires=requirements,
    tests_require=test_requirements,
    classifiers=classifiers,
    setup_requires=setup_requirements,
    data_files=data_files,
    packages=packages,
    include_package_data=True,
    package_data=package_data,
    message_extractors={
        'rhodecode': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
            ('templates/**.html', 'mako', {'input_encoding': 'utf-8'}),
            ('public/**', 'ignore', None),
        ]
    },
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points={
        'enterprise.plugins1': [
            'crowd=rhodecode.authentication.plugins.auth_crowd:plugin_factory',
            'jasig_cas=rhodecode.authentication.plugins.auth_jasig_cas:plugin_factory',
            'ldap=rhodecode.authentication.plugins.auth_ldap:plugin_factory',
            'pam=rhodecode.authentication.plugins.auth_pam:plugin_factory',
            'rhodecode=rhodecode.authentication.plugins.auth_rhodecode:plugin_factory',
        ],
        'paste.app_factory': [
            'main=rhodecode.config.middleware:make_pyramid_app',
            'pylons=rhodecode.config.middleware:make_app',
        ],
        'paste.app_install': [
            'main=pylons.util:PylonsInstaller',
            'pylons=pylons.util:PylonsInstaller',
        ],
        'paste.global_paster_command': paster_commands,
        'pytest11': [
            'pylons=rhodecode.tests.pylons_plugin',
            'enterprise=rhodecode.tests.plugin',
        ],
        'console_scripts': [
            'rcserver=rhodecode.rcserver:main',
        ],
        'beaker.backends': [
            'memorylru_base=rhodecode.lib.memory_lru_debug:MemoryLRUNamespaceManagerBase',
            'memorylru_debug=rhodecode.lib.memory_lru_debug:MemoryLRUNamespaceManagerDebug'
        ]
    },
)
