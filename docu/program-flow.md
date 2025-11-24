# MetaMindIQTrain - Simplified Program Flow

## Quick Start

```bash
# Run the application (standalone mode)
python run.py --module symbol_memory

# Run with custom resolution
python run.py --width 1280 --height 720 --module morph_matrix

# List available options
python run.py --help
```

---

## Entry Points

The application has **4 essential entry points**:

| Script | Purpose | Usage |
|--------|---------|-------|
| `run.py` | **Main entry point** - Standalone application | `python run.py --module <module_name>` |
| `run_server.py` | Server for client-server mode | `python run_server.py` |
| `run_client.py` | Client connecting to server | `python run_client.py --host localhost` |
| `run_basic_tests.py` | Run test suite | `python run_basic_tests.py` |

---

## Application Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Entry Point: run.py                       │
│                                                              │
│  1. Parse command line arguments                             │
│  2. Configure logging                                        │
│  3. Import core.app.Application                              │
│  4. Initialize renderer (pygame)                             │
│  5. Start module if specified                                │
│  6. Run main loop                                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  core/app.py - Application                   │
│                                                              │
│  • Manages application lifecycle                             │
│  • Coordinates renderer and module manager                   │
│  • Handles events and main loop                              │
│  • FPS management and performance                            │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  core/renderer  │ │ module_manager  │ │   Event Bus     │
│                 │ │                 │ │                 │
│ • Initialize    │ │ • Load modules  │ │ • Process input │
│   display       │ │ • Start/stop    │ │ • Dispatch to   │
│ • Render frame  │ │ • Update state  │ │   handlers      │
│ • Handle events │ │ • Render        │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               modules/evolve/<module_name>/                  │
│                                                              │
│  MVC Pattern:                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐              │
│  │  Model   │  │   View   │  │  Controller  │              │
│  │          │◄─┤          │◄─┤              │              │
│  │ • State  │  │ • UI     │  │ • Input      │              │
│  │ • Logic  │  │ • Layout │  │ • Actions    │              │
│  │ • Score  │  │ • Theme  │  │ • Events     │              │
│  └──────────┘  └──────────┘  └──────────────┘              │
│                      │                                       │
│                      ▼                                       │
│  ┌────────────────────────────────────┐                     │
│  │      <module>_mvc.py               │                     │
│  │  Integrates M-V-C into BaseModule  │                     │
│  └────────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Module Execution Flow

```
Module Lifecycle:
┌─────────┐    ┌──────────┐    ┌────────┐    ┌──────────┐
│  Load   │───▶│Initialize│───▶│ Active │───▶│ Cleanup  │
└─────────┘    └──────────┘    └────────┘    └──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
             ┌──────────┐                    ┌──────────┐
             │  Update  │◄───────────────────│  Render  │
             │  (dt)    │                    │  (state) │
             └──────────┘                    └──────────┘
                    │                               ▲
                    └───────────────────────────────┘
                           (main loop @ 60fps)
```

---

## Core Components

### 1. Application (`core/app.py`)
- Singleton pattern via `get_application()`
- Coordinates all subsystems
- Main loop with frame rate management

### 2. Module Registry (`module_registry.py`)
- Registers available training modules
- Dynamic module loading
- Module metadata (name, description, category)

### 3. Renderer (`clients/pygame/unified_renderer.py`)
- Surface caching for performance
- Component-based rendering
- Theme system integration

### 4. Training Modules (`modules/evolve/`)
- Each module follows MVC pattern
- Four files per module:
  - `*_model.py` - Game logic
  - `*_view.py` - UI components
  - `*_controller.py` - Input handling
  - `*_mvc.py` - Integration

---

## Directory Structure (Simplified)

```
MetaMindIQTrain/
├── run.py                    # Main entry point
├── run_server.py             # Server mode
├── run_client.py             # Client mode
├── config.py                 # Global configuration
├── module_registry.py        # Module registration
│
├── core/                     # Core framework
│   ├── app.py               # Application class
│   ├── training_module.py   # Base module class
│   ├── components.py        # UI components
│   ├── theme.py             # Theme system
│   └── renderer.py          # Renderer interface
│
├── clients/                  # Client implementations
│   └── pygame/
│       ├── unified_renderer.py  # Main renderer
│       └── render_utils.py      # Rendering utilities
│
├── modules/                  # Training modules
│   └── evolve/              # Active modules (MVC)
│       ├── symbol_memory/
│       ├── morph_matrix/
│       ├── expand_vision/
│       ├── neural_flow/
│       ├── quantum_memory/
│       └── ...
│
└── docu/                     # Documentation
    ├── project-vision.md
    └── program-flow.md
```

---

## Available Modules

| Module | Category | Description |
|--------|----------|-------------|
| `symbol_memory` | Memory | Visual pattern memorization |
| `morph_matrix` | Pattern Recognition | Rotation vs modification detection |
| `expand_vision` | Visual Attention | Peripheral vision training |
| `expand_vision_grid` | Visual Attention | Grid-based peripheral training |
| `neural_flow` | Cognitive Flexibility | Sequential node activation |
| `quantum_memory` | Advanced Memory | Quantum-inspired mechanics |
| `neural_synthesis` | Cross-Modal | Visual-auditory integration |
| `synesthetic_training` | Cross-Modal | Sensory association training |
| `music_theory` | Auditory | Musical pattern recognition |

---

## Configuration

Key configuration in `config.py`:

```python
# Display
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 1024
DEFAULT_FPS = 60

# Layout (percentage-based)
UI_HEADER_HEIGHT_PERCENT = 0.15
UI_FOOTER_HEIGHT_PERCENT = 0.12
UI_CONTENT_HEIGHT_PERCENT = 0.73

# Theme colors
DEFAULT_BG_COLOR = (15, 18, 28)
ACCENT_COLOR_PRIMARY = (80, 120, 200)
```

---

## Performance Optimizations

1. **Surface Caching** - Rendered components cached for reuse
2. **Surface Pooling** - Reuse pygame surfaces to reduce allocations
3. **Batch Rendering** - Group similar draw operations
4. **Delta Encoding** - Only transmit state changes
5. **Dirty Region Tracking** - Partial screen updates

---

## Adding New Modules

1. Create directory: `modules/evolve/<module_name>/`
2. Create MVC files:
   - `<module>_model.py`
   - `<module>_view.py`
   - `<module>_controller.py`
   - `<module>_mvc.py`
3. Register in `module_registry.py`:
   ```python
   {
       'id': 'module_name',
       'name': 'Module Name',
       'description': 'Description',
       'class_path': 'MetaMindIQTrain.modules.evolve.module_name.module_name_mvc.ModuleClass',
       'difficulty': 'Medium',
       'category': 'Category'
   }
   ```
4. Create `README.md` in module directory

---

## Archived Code

Legacy and development files have been archived to:
- `modules/_archive/legacy/` - Old monolithic module implementations
- `_archive/run_scripts/` - Deprecated run scripts

These are kept for reference but are not part of the active codebase.
