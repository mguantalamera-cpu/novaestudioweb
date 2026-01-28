from core.fixers.python_fixers import get_python_fixers
from core.fixers.js_fixers import get_js_fixers


def get_all_fixers():
    fixers = {}
    fixers.update(get_python_fixers())
    fixers.update(get_js_fixers())
    return fixers
