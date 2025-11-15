# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About Prism Pipeline

Prism is a Python/Qt-based animation and VFX pipeline management system that automates workflows across multiple DCC (Digital Content Creation) applications. It manages project assets, versions, and publishing for production pipelines.

**Current Version:** 2.0.17
**License:** GNU LGPL-3.0-or-later
**Platform:** Windows-only at this time
**Website:** https://prism-pipeline.com/

## Application Architecture

### Core Entry Points

The application has two primary launchers in `/Prism/`:

- **`prism.bat`** - Main application launcher
  - Runs: `Python311/pythonw.exe Scripts/PrismCore.py`
  - Starts PrismCore with appropriate app plugin (Standalone, Blender, Maya, etc.)

- **`setup.bat`** - Installation wizard
  - Runs: `Python311/python.exe Scripts/PrismInstaller.py`
  - Creates shortcuts and integrates with DCC applications

### Core Architecture (`Prism/Scripts/`)

PrismCore.py is the main orchestrator that initializes and coordinates all subsystems through a manager pattern:

```python
core = PrismCore()
core.plugins          # PluginManager - plugin discovery and loading
core.callbacks        # Callbacks - event/callback system
core.projects         # Projects - project management
core.entities         # ProjectEntities - asset/shot/sequence hierarchy
core.products         # Products - work/publish version management
core.configs          # ConfigManager - JSON/YAML/INI config I/O
core.paths            # PathManager - path manipulation
core.integration      # Integration - DCC tool integration
core.media            # MediaManager - image/video processing
core.mediaProducts    # MediaProducts - media file versioning
core.users            # Users - user preferences and environment
```

All managers follow dependency injection: they receive `core` in `__init__(core)` and access other managers via `self.core.manager_name`.

### Plugin System

Prism uses a two-tier plugin architecture:

#### Application Plugins (`Prism/Plugins/Apps/`)
Each DCC integration (Blender, Maya, Houdini, Nuke, 3dsMax, Cinema4D, Photoshop, PureRef, Standalone) follows this structure:

```
{AppName}/
└── Scripts/
    ├── Prism_{AppName}_init.py              # Main plugin class
    ├── Prism_{AppName}_Variables.py         # Plugin state/properties
    ├── Prism_{AppName}_Functions.py         # Core functionality
    ├── Prism_{AppName}_Integration.py       # DCC integration hooks
    └── Prism_{AppName}_externalAccess_Functions.py  # External API
```

Plugin classes use **multiple inheritance** to combine mixins:
```python
class Prism_Plugin_Blender(
    Prism_Blender_Variables,
    Prism_Blender_externalAccess_Functions,
    Prism_Blender_Functions,
    Prism_Blender_Integration,
):
    def __init__(self, core):
        # Initialize each mixin
        Prism_Blender_Variables.__init__(self, core, self)
        # ...
```

#### Custom Plugins (`Prism/Plugins/Custom/`)
Non-DCC plugins like render farm integrations (Deadline) follow the same structure as App plugins.

#### Plugin Discovery

PluginManager searches for plugins in this order:
1. Default: `Prism/Plugins/Apps/` and `Prism/Plugins/Custom/`
2. Environment variables: `PRISM_PLUGIN_PATHS`, `PRISM_PLUGIN_SEARCH_PATHS`
3. User config: `~/.Prism2/Prism.json` → `PluginPaths` section
4. Project-specific plugins

Loading sequence (PrismUtils/PluginManager.py):
1. Load app-specific plugin first (e.g., Maya)
2. Load remaining custom/support plugins
3. Fire `onPluginsLoaded` callback
4. Call `core.startup()`

### Callback System

The callback system (PrismUtils/Callbacks.py) implements a priority-based pub/sub pattern:

```python
# Register callback
core.callbacks.registerCallback(
    callbackName="postPublish",
    function=my_handler,
    priority=50,  # Higher = earlier execution (0-100)
    plugin=self
)

# Execute callback
results = core.callback("postPublish", args=[data])
```

**Common callbacks:**
- `prePublish`, `postPublish` - before/after publishing
- `preSaveScene`, `postSaveScene` - before/after saving
- `preExport`, `postExport`, `postImport` - import/export operations
- `preRender`, `postRender` - rendering
- `prePlayblast`, `postPlayblast` - preview generation
- `onPluginsLoaded` - after all plugins loaded

**Project Hooks:** Python scripts in `{ProjectPath}/.prism/hooks/` are dynamically imported and executed via `core.callbacks.callHook()`.

### State Manager

Located: `Prism/Scripts/ProjectScripts/StateManager.py`

The State Manager is Prism's workflow engine. Each **state** represents a processing step in the pipeline:

- **Import** - Import reference files
- **Export** - Export work files
- **Playblast** - Create preview playback
- **Render** - Execute render passes
- **Publish** - Finalize and version products
- **Dependency** - Declare upstream dependencies

State implementations are in `ProjectScripts/StateManagerNodes/{type}/` with their own UI definitions.

### Error Handling

All functions should use the `@err_catcher` decorator (PrismUtils/Decorators.py):

```python
from PrismUtils.Decorators import err_catcher

@err_catcher(name=__name__)
def some_function(self):
    # Automatically wrapped with try/except
    # Logs full traceback on exception
    # Shows user-friendly error dialog
    pass
```

This is critical - missing decorators can cause silent failures.

### Configuration Management

Configuration hierarchy (managed by PrismUtils/ConfigManager.py):

```
User Config: ~/.Prism2/Prism.json (or .yml/.ini)
├── globals - UI scale, debug mode, plugin paths
├── user - current user, permissions
└── PluginPaths - custom plugin directories

Project Config: {ProjectPath}/.prism/Prism.json
├── project - name, root, path format
├── entities - asset types, department mappings
├── products - work/publish type definitions
└── plugins - project-specific plugin config
```

Features:
- Automatic JSON/YAML/INI conversion
- File caching for performance
- Lockfile-based concurrent access
- Backward compatibility with deprecated INI format

Access configs via:
```python
value = core.getConfig(key="some.nested.key", config="user")
core.setConfig(key="some.nested.key", value=data, config="user")
```

### UI Architecture

Built with **qtpy** (abstraction over PyQt5/PySide2/PySide6) for cross-version compatibility.

Main UI components:
- **PrismSettings.py** - User/project/plugin preferences
- **ProjectScripts/ProjectBrowser.py** - Project/asset browser
- **ProjectScripts/SceneBrowser.py** - Scene file browser
- **ProjectScripts/StateManager.py** - Workflow state management
- **ProjectScripts/ProductBrowser.py** - Published product browser

UI files: `Prism/Scripts/UserInterfacesPrism/`
- `*.ui` - Qt Designer files
- `*_ui.py` - Generated Python code (do not edit manually)
- `stylesheets/` - Dark mode themes (blue_moon, qdarkstyle)

Custom widgets: `PrismUtils/PrismWidgets.py`

## Development Workflow

### Dependencies

**Required:** Download Prism dependencies from website (separate download):
- Python 3.7/3.9/3.10/3.11 runtimes (`Prism/Python{version}/`)
- Cross-platform libraries (`Prism/PythonLibs/CrossPlatform/`)
- Version-specific libraries (`Prism/PythonLibs/Python{version}/`)

Extract dependencies into the `/Prism/` folder alongside `Scripts/`, `Plugins/`, etc.

Set `PRISM_LIBS` environment variable if dependencies are in a different location.

### Python Path Setup

PrismCore.py automatically configures sys.path based on Python version:
1. Adds `Prism/Scripts/` for core modules
2. Adds `Prism/PythonLibs/CrossPlatform/`
3. Adds `Prism/PythonLibs/Python{version}/` based on `sys.version_info.minor`
4. On Windows: Adds pywin32 paths

If you see import errors, verify dependencies are installed and PRISM_LIBS is set correctly.

### Running Prism

**Windows:**
```bash
cd Prism
setup.bat          # Run installer wizard (first time)
prism.bat          # Launch standalone application
```

**Running with specific DCC:**
Prism integrates into each DCC's startup scripts. After installation via `setup.bat`, launch Prism from within the DCC application's menu.

**Debug mode:**
Set environment variable before launching:
```bash
set PRISM_DEBUG=1
prism.bat
```

### Documentation

Located: `/doc/` (Sphinx-based)

**Build documentation:**
```bash
cd doc
# Install Sphinx if needed: pip install sphinx sphinx-book-theme
sphinx-build -b html . _build
```

Configuration: `doc/conf.py`
- Uses `sphinx.ext.autodoc` for API documentation
- Theme: `sphinx_book_theme`
- Auto-imports modules from `Prism/Scripts/` and plugin directories

## Plugin Development

### Creating a New App Plugin

Use the template at `Prism/Plugins/Apps/PluginEmpty/` as a starting point.

Required files in `Scripts/`:
```
Prism_{AppName}_init.py              # Main plugin class
Prism_{AppName}_Variables.py         # Properties: pluginName, version, platforms
Prism_{AppName}_Functions.py         # Core functionality
Prism_{AppName}_Integration.py       # DCC integration methods
Prism_{AppName}_externalAccess_Functions.py  # External API
```

Minimal plugin class:
```python
class Prism_Plugin_{AppName}(
    Prism_{AppName}_Variables,
    Prism_{AppName}_Functions,
    # ... other mixins
):
    def __init__(self, core):
        Prism_{AppName}_Variables.__init__(self, core, self)
        # Initialize other mixins

    @err_catcher(name=__name__)
    def startup(self):
        # Called after all plugins loaded
        pass
```

**Integration files:** Place DCC-specific startup scripts in `Integration/` folder. These are copied to the DCC's scripts directory during installation.

### Creating a Custom Plugin

Use the template at `Prism/Plugins/Custom/PluginEmpty/`.

Custom plugins follow the same structure as App plugins but don't require Integration files.

### Registering Callbacks in Plugins

```python
@err_catcher(name=__name__)
def __init__(self, core):
    # ... initialization

    core.callbacks.registerCallback(
        callbackName="postPublish",
        function=self.onPublish,
        priority=50,
        plugin=self
    )

@err_catcher(name=__name__)
def onPublish(self, *args, **kwargs):
    # Handle publish event
    pass
```

## Code Conventions

### Import Style

Always use absolute imports from Prism root:
```python
from PrismUtils.Decorators import err_catcher
from PrismUtils import PluginManager
```

For Qt imports, always use qtpy abstraction:
```python
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
```

### Error Handling

**Always** decorate functions with `@err_catcher`:
```python
@err_catcher(name=__name__)
def myFunction(self):
    pass
```

### Logging

Use Python's logging module (already configured):
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Accessing Core Functionality

From plugins or managers:
```python
# Access other managers
self.core.projects.getCurrentProject()
self.core.entities.getAssets()
self.core.products.getVersions()

# Fire callbacks
self.core.callback("customEvent", args=[data])

# Show popup messages
self.core.popup("Message to user")
```

## File Locations Reference

**Core application:**
- Main scripts: `Prism/Scripts/PrismCore.py`, `PrismSettings.py`, etc.
- Utility modules: `Prism/Scripts/PrismUtils/*.py`
- Project scripts: `Prism/Scripts/ProjectScripts/*.py`
- UI files: `Prism/Scripts/UserInterfacesPrism/*.ui`

**Plugins:**
- App plugins: `Prism/Plugins/Apps/{AppName}/Scripts/`
- Custom plugins: `Prism/Plugins/Custom/{PluginName}/Scripts/`

**Configuration:**
- User config: `~/.Prism2/Prism.json` (Windows: `%USERPROFILE%/.Prism2/`)
- Project config: `{ProjectPath}/.prism/Prism.json`
- Project hooks: `{ProjectPath}/.prism/hooks/*.py`

**Documentation:**
- Source: `doc/*.rst`, `doc/conf.py`
- Built HTML: `doc/_build/` (after running Sphinx)

## Important Notes

- **No test suite exists** - This is production code without unit tests. Manual testing is required.
- **Windows-only** - Linux/macOS support is not currently available.
- **Python version handling** - Code supports Python 3.7, 3.9, 3.10, 3.11. Be mindful of version-specific features.
- **Qt version abstraction** - Always use `qtpy` imports, never import PySide2/PySide6/PyQt5 directly.
- **Plugin loading order matters** - App plugin loads first, then custom plugins. Use callback priorities to control execution order.
- **Configuration caching** - ConfigManager caches file reads. Use `core.getConfig()` / `core.setConfig()` instead of direct file I/O.
