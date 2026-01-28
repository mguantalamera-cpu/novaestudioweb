from core.diff import unified_diff


def test_unified_diff():
    original = "a\n"
    updated = "b\n"
    diff = unified_diff(original, updated, "file.txt")
    assert "-a" in diff
    assert "+b" in diff
