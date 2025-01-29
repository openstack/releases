# -*- coding: utf-8 -*-

import datetime
import os
import sys

from sphinx.util import logging

LOG = logging.getLogger(__name__)

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.join(os.path.abspath('.'), '_exts'))

# -- General configuration ----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'deliverables',
    'sphinxcontrib.datatemplates',
    'ics',
    'reviewinbox',
]

config_generator_config_file = 'config-generator.conf'

# autodoc generation is a bit aggressive and a nuisance when doing heavy
# text edit cycles.
# execute "export SPHINX_DEBUG=1" in your terminal to disable

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'releases'
copyright = '2015, OpenStack Foundation'

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'native'

# -- Options for HTML output --------------------------------------------------

# The theme to use for HTML and HTML Help pages.  Major themes that come with
# Sphinx are currently 'default' and 'sphinxdoc'.
html_theme = 'releases'
html_theme_path = ['_themes']
html_static_path = ['static']

# Output file base name for HTML help builder.
htmlhelp_basename = '%sdoc' % project

git_cmd = "git log --pretty=format:'%ad, commit %h' --date=local -n1"
html_last_updated_fmt = os.popen(git_cmd).read()

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto/manual]).
latex_documents = [
    ('index',
     '%s.tex' % project,
     '%s Documentation' % project,
     'OpenStack Foundation', 'manual'),
]


def format_date(s, fmt='%b %d'):
    # This function is used in schedule_table.tmpl
    if isinstance(s, (datetime.date, datetime.datetime)):
        d = s
    else:
        d = datetime.datetime.strptime(s, '%Y-%m-%d')
    return d.strftime(fmt)


def builder_inited(app):
    # Make format_date visible in the template context.
    app.builder.templates.environment.globals['format_date'] = format_date


def setup(app):
    LOG.info('initializing from conf.py')
    app.connect('builder-inited', builder_inited)
