```
 ____           ____                        ____    ___                      __   
/\  _`\        /\  _`\   __                /\  _`\ /\_ \                    /\ \  
\ \ \L\ \__  __\ \,\L\_\/\_\    ___      __\ \ \L\ \//\ \      __    ___    \_\ \ 
 \ \ ,__/\ \/\ \\/_\__ \\/\ \ /' _ `\  /'__`\ \  _ <'\ \ \   /'__`\/' _ `\  /'_` \
  \ \ \/\ \ \_\ \ /\ \L\ \ \ \/\ \/\ \/\  __/\ \ \L\ \\_\ \_/\  __//\ \/\ \/\ \L\ \
   \ \_\ \/`____ \\ `\____\ \_\ \_\ \_\ \____\\ \____//\____\ \____\ \_\ \_\ \___,_\
    \/_/  `/___/> \\/_____/\/_/\/_/\/_/\/____/ \/___/ \/____/\/____/\/_/\/_/\/__,_ /
             /\___/                                                               
             \/__/                                                                
===============================================================================
                 PYSINEBLEND - SYSTEM SPECIFICATIONS & GUIDE
===============================================================================

[1.0 REQUIREMENTS]
-------------------------------------------------------------------------------
    - Python 3.10 or newer
    - NumPy 1.24 or newer
    - Pygame CE 2.5 or newer

Pygame CE is installed as pygame-ce and imported in the application as
pygame. The requirements.txt file lists all runtime dependencies.


[2.0 INSTALLATION AND STARTUP]
-------------------------------------------------------------------------------
Create and activate a virtual environment from the project root. Then install
the requirements and start the application.

Windows PowerShell:
bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py


macOS or Linux:
bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py


The application boots immediately into the 1D Oscilloscope viewport. Use
Escape or the window's close button to exit.


[3.0 PROJECT OVERVIEW]
-------------------------------------------------------------------------------
PySineBlend is an interactive mathematical laboratory for synthesizing,
blending, and inspecting procedural heightfield waves in real time.

Unlike simple signal plotters, PySineBlend provides seamless dual-viewport
parity across two dimensions:

    Mode 1: 1D Oscilloscope (Cross-Sectional Signal Interference)
    Mode 2: 2D Spatial Synthesizer (Planar Topographical Elevation Field)

The tool allows designers and developers to see how mathematical equations,
layer budgeting, frequency scaling, discrete tile stepping, and color ramps
translate from single-line curves into full continuous 2D landscapes.

Wave mathematics execute in vectorized C-speed NumPy arrays, while hardware-
accelerated rendering is handled via Pygame-ce.


[4.0 WHAT THE INSPECTOR SHOWS]
-------------------------------------------------------------------------------
The application models terrain through three fundamental geological roles:

    1. Base Detail Wave  : Dense local hills, valleys, and ridges.
                           Labelled D(x) in 1D; B in formulas.
    2. Relief Multiplier : The macro envelope deciding where mountains swell
                           versus where valleys and plains flatten out.
                           Labelled M(x) in 1D; R in formulas.
    3. Continental Crust : The tectonic ground floor that lifts land into dry
                           continents or drops it into ocean trenches.
                           Labelled C(x) in 1D; C in formulas.

All wave signals are normalized between 0.000 (abyssal sea floor) and 1.000
(mountain peak ceiling). Starting heights determine the wave phase offset at
the left edge or radial center.


[5.0 DUAL-VIEWPORT ARCHITECTURE]
-------------------------------------------------------------------------------
Switch seamlessly between both viewports at any time using keys '1' and '2':

MODE 1: 1D OSCILLOSCOPE (Key [1])
-------------------------------------------------------------------------------
Presents four vertically stacked real-time oscilloscope panels:
    - Panel 1: Base Detail wave D(x).
    - Panel 2: Relief Multiplier envelope M(x).
    - Panel 3: Continental Crust tectonic floor C(x).
    - Panel 4: Composite Result from the active mathematical formula.

Panel 4 features optional Hypsometric Fill: pressing [N] paints vertical
color ribbons under the curve down to the baseline using the active color
palette, giving immediate visual intuition of elevation bands.


MODE 2: 2D SPATIAL SYNTHESIZER (Key [2])
-------------------------------------------------------------------------------
Projects the three wave roles across a continuous 2D surface on a 16:9 screen:
    - Base Detail (B)     : Mapped to Vertical Stripes along X (dense ridges).
    - Relief Multiplier (R): Mapped to Horizontal Bands along Y (valleys).
    - Continental Crust (C): Mapped to Concentric Radial Rings (central dome).

Their intersection naturally forms an orthogonal mountain grid lifted by a
central continental dome and falling into ocean waters at the borders.

Dual Projections for 2-Layer Formulas:
Because 2-layer formulas only have two inputs (Base and Relief), simple
orthogonal grids can look like an artificial checkerboard. PySineBlend gives
every 2-layer formula two selectable 2D projection modes:
    - [Radial] : The Relief envelope forms a circular continental dome,
                 dissolving ridges into flat ocean plains at the edges.
    - [Warped] : The Relief layer organically shears and bends the Base
                 coordinates, turning rigid vertical stripes into serpentine,
                 folded mountain belts and river valleys.


[6.0 FORMULA CATALOG & PRESETS]
-------------------------------------------------------------------------------
The inspector maintains complete bi-directional state synchronization between
both viewports:

MODE 1 CATALOG (12 Composite Formulas):
-------------------------------------------------------------------------------
Mode 1 excludes solo components so Panel 4 never renders a redundant duplicate
of an upper panel. It cycles strictly through the 12 composite recipes:

Three-Layer Formulas:
    - Master 3-Layer Budgeting   : Standard additive tectonic crust + relief.
    - Global Envelope Factor     : Overall relief scaling of crust and base.
    - Volcanic Island Override   : Heavy crust dome with dual-stage detail.
    - Inverse Crust Bypass       : Shoreline bypass preserving low relief.
    - Dynamic Lerp / Morph       : Smooth morph between crust and base.
    - Tectonic Subduction Belt   : Squared crust basin with ridge clamping.
    - Stepped Mesa Terraces      : 4-tier terrace quantization with crust.

Two-Layer Formulas (Continental Crust Silenced):
    - Factored Virtual Crust     : Macro envelope drives both floor and peaks.
    - Tibetan High Plateau       : High plateau floor with sine-wave valleys.
    - Razor Ridge / Granite Peaks: Squared base ridges sharpened by relief.
    - Inverted Canyonlands       : Inverted relief carving steep ravines.
    - Soft Natural Saturation    : Hyperbolic tangent organic compression.


MODE 2 CATALOG (20 Total Presets):
-------------------------------------------------------------------------------
Mode 2 allows inspecting isolated wave geometry alongside composite math:
    - Presets 1 to 3   : Solo Components (Vertical Base, Horizontal Relief,
                         and Radial Continental Crust).
    - Presets 4 to 8   : 3-Layer Composite Series.
    - Presets 9 to 18  : 2-Layer Series Dual Projections (each 2-layer formula
                         features both [Radial] and [Warped] variants).
    - Presets 19 to 20 : Advanced 3-Layer Hybrids.


[7.0 DISCRETE TILE STEPPING (QUANTIZATION)]
-------------------------------------------------------------------------------
Pressing [SPACE] and [SHIFT + SPACE] cycles the terrain through a power-of-two
tile quantization ring:
    OFF -> 8px -> 16px -> 32px -> OFF

Centroid Grid Anchoring:
Tile sampling evaluates elevation at the exact centroid (+0.5 stride) of
each tile block rather than its top-left edge. This ensures radial islands,
concentric rings, and diagonal ridges remain mathematically centered and
symmetrical across all four quadrants without shifting the visual screen grid.

Visual Representation Across Viewports:
    - In 1D: Smooth sine curves break into crisp, horizontal step-pyramid
             staircases, illustrating discrete elevation hold plateaus.
    - In 2D: Smooth raster gradients turn into retro pixel blocks or macro-
             biome chunks (similar to a classic 16-bit RPG overworld).

Stepping past 64px (or below 4px with Shift) deactivates tile mode cleanly.


[8.0 DIAGNOSTIC COLOR SUITE, INVERSION & RELIEF NET]
-------------------------------------------------------------------------------
PySineBlend includes pre-baked 1,024-entry Look-Up Tables (LUTs) for mapping
elevation directly to color in under 0.1 milliseconds:

    - GREYSCALE : Linear monochrome baseline.
    - MAGMA     : Perceptually uniform high-contrast sequential (black to
                  dark purple, fiery red, yellow, and white).
    - TURBO     : Spectral rainbow curve exposing subtle harmonic creases.
    - VIRIDIS   : Perceptually uniform blue-to-yellow standard colormap.

Color Inversion (Key [I]):
Pressing [I] reverses the active color ramp along its elevation axis. In
Greyscale, this creates a film-negative/X-ray effect; in thermal heatmaps,
it inverts peak-versus-valley polarity.

Topographical Relief Net / Isoline Mode (Key [N]):
Pressing [N] turns the visualization into a topographical isoline net:
    - In 1D: Toggles vertical hypsometric scanline fill under Panel 4.
    - In 2D: Replaces the continuous raster surface with a dark blueprint
             vector contour net (levels: 0.00, 0.25, 0.50, 0.75, 1.00).

Dual Evaluation Mechanics:
    - Continuous Mode : Evaluates contour lines using a narrow tolerance
                        bandwidth (+/- 0.015), creating smooth 1-pixel curves.
    - Discrete Tile Mode: Automatically shifts to geometric cardinal cell-
                        crossing (h_min <= L <= h_max). Testing whether a
                        level passes through a tile's spatial span guarantees
                        unbroken, strictly 1-tile-thick perimeter outlines
                        with zero gaps on steep slopes and zero blobs on
                        flat plateaus.


[9.0 CONTROLS & KEYBOARD SHORTCUTS]
-------------------------------------------------------------------------------
    1                   : Switch to Mode 1 (1D Oscilloscope Viewport).
    2                   : Switch to Mode 2 (2D Spatial Synthesizer Viewport).

    TAB                 : Cycle to next formula preset.
    SHIFT + TAB         : Cycle to previous formula preset.

    UP / DOWN           : Switch channel focus (Base -> Relief -> Crust).
                          (Automatically skips Crust on 2-layer formulas).

    HOLD RIGHT          : Continuously zoom in (increase frequency/cycles).
    HOLD LEFT           : Continuously zoom out (decrease frequency/cycles).

    SPACE               : Step tile size coarser (OFF -> 4 -> 8 -> ... -> 64).
    SHIFT + SPACE       : Step tile size finer (64 -> ... -> 4 -> OFF).

    C                   : Cycle active color palette forward.
    SHIFT + C           : Cycle active color palette backward.

    I                   : Toggle palette color inversion on/off.
    N                   : Toggle Topographical Relief Net / 1D Fill mode.

    R                   : Reset active focused channel cycles to default.
    SHIFT + R           : Reset all channels to default configuration.

    ESCAPE / CLOSE      : Clean application shutdown.


[10.0 CONFIGURATION]
-------------------------------------------------------------------------------
Global defaults and hardware parameters reside in config.py:

    SCREEN_WIDTH / HEIGHT     : Desktop window resolution in pixels.
    FPS                       : Display refresh rate target (60 Hz).
    DEFAULT_VIEW_MODE         : Boot viewport mode (1 or 2).

    DEFAULT_TILE_SIZE         : Starting tile step size in pixels (8px).
    MIN / MAX_TILE_SIZE       : Power-of-two quantization clamps (4px to 64px).
    WARP_FACTOR               : Domain warping shear intensity in 2D (0.15).

    DEFAULT_NET_ENABLED       : Starting state of the relief isoline net.
    DEFAULT_NET_INTERVALS     : Number of elevation intervals (4.0 -> 5 steps).
    DEFAULT_NET_BANDWIDTH     : Thickness of contour tolerance lines (0.015).
    COLOR_NET_BACKGROUND      : Background color for 2D net mode (10, 12, 18).

    DEFAULT_BASE_CYCLES       : Initial Base Detail cycle count across screen.
    DEFAULT_RELIEF_CYCLES     : Initial Relief Multiplier cycle count.
    DEFAULT_CRUST_CYCLES      : Initial Continental Crust cycle count.

    CYCLE_ZOOM_RATE           : Continuous exponential zoom multiplier rate.
    CRUST / RELIEF_BUDGET     : Mathematical elevation budget shares (0.35/0.65).


[11.0 PROJECT STRUCTURE]
-------------------------------------------------------------------------------
└── pysineblend/
    ├── main.py                # Root bootstrap entry point
    ├── config.py              # Central runtime settings and layout constants
    ├── requirements.txt       # Minimal dependencies (numpy, pygame-ce)
    ├── README.md              # System specification and documentation
    └── wave_inspector/
        ├── __init__.py        # Namespace package marker
        ├── app.py             # Main application lifecycle and loop coordinator
        ├── formulas.py        # 15-preset catalog, math functions, 2D specs
        ├── heatmaps.py        # 1,024-slot LUT bakes and array inversion
        ├── input_handler.py   # Isolated event routing and held-key polling
        ├── state.py           # Shared mutable state machine and sync logic
        ├── wave_model.py      # Pure NumPy 1D and 2D wave synthesis engine
        └── renderers/
            ├── __init__.py    # Namespace package marker
            ├── base_renderer.py # Dynamic typography and HUD card drawer
            ├── renderer_1d.py # 4-panel oscilloscope rendering and fill
            └── renderer_2d.py # 2D surface baking and isoline net generator


[12.0 LICENSE]
-------------------------------------------------------------------------------
This project is licensed under the MIT License. See the root LICENSE file
for complete terms.

===============================================================================
                 END OF PYSINEBLEND SPECIFICATIONS & GUIDE
===============================================================================