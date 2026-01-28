from core.rules.python_rules import get_python_rules
from core.rules.js_rules import get_js_rules


def get_builtin_rules():
    return get_python_rules() + get_js_rules()
