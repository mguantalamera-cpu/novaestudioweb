from core.fixers.python_fixers import YamlSafeLoadFixer, RequestsVerifyFixer, SubprocessShellFixer
from core.fixers.js_fixers import InnerHtmlToTextContentFixer


def test_yaml_safe_load():
    text = "import yaml\nconfig = yaml.load(data)\n"
    fixer = YamlSafeLoadFixer()
    result = fixer.apply("x.py", text)
    assert result
    assert "yaml.safe_load" in result.updated_text


def test_requests_verify():
    text = "requests.get(url, verify=False)\n"
    fixer = RequestsVerifyFixer()
    result = fixer.apply("x.py", text)
    assert result
    assert "verify=True" in result.updated_text


def test_subprocess_shell_false():
    text = "subprocess.run([\"ls\"], shell=True)\n"
    fixer = SubprocessShellFixer()
    result = fixer.apply("x.py", text)
    assert result
    assert "shell=False" in result.updated_text


def test_inner_html_fix():
    text = "el.innerHTML = \"hello\"\n"
    fixer = InnerHtmlToTextContentFixer()
    result = fixer.apply("x.js", text)
    assert result
    assert "textContent" in result.updated_text
