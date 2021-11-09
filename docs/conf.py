import os
import sys

sys.path.insert(0, os.path.abspath('..'))

project = 'rsx'
copyright = '2021, Giorgos Stamatelatos'
author = 'Giorgos Stamatelatos'

import rsx

version = rsx.__version__
release = version

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'sphinx.ext.intersphinx',
    'sphinx_copybutton'
]

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True
}

autoclass_content = 'both'
mathjax_path = "https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"
html_show_sphinx = False
html_theme = "furo"
html_title = "rsx " + release
modindex_common_prefix = ["rsx."]
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# html_logo = "logo.svg"
# html_theme_options = {
#     "sidebar_hide_name": True,
#     "light_logo": "logo.svg",
#     "dark_logo": "logo.svg",
# }
