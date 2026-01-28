import importlib.util
from pathlib import Path
from dataclasses import dataclass


@dataclass
class PluginSpec:
    name: str
    rules: list
    fixers: dict


def load_plugins():
    plugins_dir = Path(__file__).resolve().parent.parent / "plugins"
    if not plugins_dir.exists():
        return []
    plugins = []
    for plugin_path in plugins_dir.glob("*/plugin.py"):
        spec = importlib.util.spec_from_file_location(plugin_path.stem, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "PLUGIN"):
            plugins.append(module.PLUGIN)
    return plugins
