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

Pygame CE is distributed as pygame-ce and imported in Python as pygame.
The requirements.txt file lists all runtime dependencies.


[2.0 INSTALLATION AND STARTUP]
-------------------------------------------------------------------------------
Create and activate a virtual environment from the project root. Then install
dependencies and launch the application.

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


The studio boots immediately into the 1D Oscilloscope viewport. Use Escape
or close the application window to shut down cleanly.


[3.0 PROJECT OVERVIEW]
-------------------------------------------------------------------------------
PySineBlend is an interactive mathematical laboratory designed for synthesizing,
blending, and inspecting procedural terrain waves in real time.

In traditional game development, terrain is frequently treated as a grid of
rigid square tiles. PySineBlend models terrain as a continuous mathematical
elevation field: a smooth surface where every pixel has an exact height value
between zero (deep ocean floor) and one (mountain peaks).

The software provides dual-viewport parity across two spatial dimensions:

    Mode 1: 1D Oscilloscope (Cross-Sectional Signal Interference)
    Mode 2: 2D Spatial Synthesizer (Planar Topographical Elevation Field)

This allows creators to see how pure mathematical formulas, frequency
adjustments, coordinate warping, discrete tile steps, and color palettes
translate from single-line curves into rich continuous 2D landscapes.

All mathematical computations run via high-performance vectorized NumPy
arrays, with hardware-accelerated rendering handled through Pygame-ce.


[4.0 GEOLOGICAL WAVE ROLES]
-------------------------------------------------------------------------------
Natural terrain is simulated by combining three distinct geological wave roles:

    1. Base Detail Wave  : High-frequency local topography (hills, valleys,
                           and ridges). Labeled D(x) in 1D; B in formulas.
    2. Relief Multiplier : The macro envelope deciding where mountains swell
                           versus where valleys and plains flatten out.
                           Labeled M(x) in 1D; R in formulas.
    3. Continental Crust : The low-frequency tectonic floor that lifts land
                           into dry continents or drops it into ocean basins.
                           Labeled C(x) in 1D; C in formulas.

All wave signals are normalized between 0.000 (sea level baseline) and 1.000
(mountain peak ceiling). Configurable starting heights determine initial
wave phase offsets at the screen edge or radial center.

Mathematical Elevation Budgeting (Zero-Clipping Invariant):
To prevent terrain from shearing off against an artificial flat ceiling,
formulas divide available elevation into mathematical budgets (crust share
and relief share). Because their maximum sum cannot exceed 1.000, peaks never
clip flat, and inland valleys remain naturally elevated above sea level on
high continental ground.


[5.0 DUAL-VIEWPORT ARCHITECTURE]
-------------------------------------------------------------------------------
Switch seamlessly between viewports at any time using keys '1' and '2':

MODE 1: 1D OSCILLOSCOPE (Key [1])
-------------------------------------------------------------------------------
Presents four vertically stacked real-time oscilloscope panels:
    - Panel 1: Base Detail wave D(x).
    - Panel 2: Relief Multiplier envelope M(x).
    - Panel 3: Continental Crust tectonic floor C(x).
    - Panel 4: Composite Result from the active mathematical formula.

Panel 4 features dual-mode visualization:
    - Standard Mode: Renders a solid hypsometric color fill under the curve
                     down to the baseline using the active color palette.
    - Net Mode (Key [N]): Replaces the fill with a crisp, multi-colored vector
                     trace line colored according to height.


MODE 2: 2D SPATIAL SYNTHESIZER (Key [2])
-------------------------------------------------------------------------------
Projects the three wave roles across a continuous 2D surface on a 16:9 canvas:
    - Base Detail (B)     : Mapped to Vertical Stripes along X (dense ridges).
    - Relief Multiplier (R): Mapped to Horizontal Bands along Y (valleys).
    - Continental Crust (C): Mapped to Concentric Radial Rings (central dome).

Their natural intersection creates an orthogonal mountain grid lifted by a
central continental dome and falling off into ocean waters at the borders.

Dual Projections for Two-Layer Formulas:
Because formulas without tectonic crust only take two inputs (Base and Relief),
simple orthogonal grids can look like an artificial checkerboard. PySineBlend
provides two specialized 2D projection models for two-layer recipes:
    - [Radial] : The Relief envelope forms a circular continental dome,
                 dissolving ridges into flat ocean plains at the edges.
    - [Warped] : The Relief layer organically shears and bends the Base
                 coordinates, turning rigid vertical stripes into serpentine,
                 folded mountain belts and river valleys.


[6.0 FORMULA CATALOG & PRESETS]
-------------------------------------------------------------------------------
The inspector maintains full bi-directional state synchronization between
viewports:

MODE 1 CATALOG (12 Composite Formulas):
-------------------------------------------------------------------------------
Mode 1 cycles strictly through composite formulas so Panel 4 never renders a
redundant copy of an upper component:

Three-Layer Formulas:
    - Master 3-Layer Budgeting   : Additive tectonic crust + modulated relief.
    - Global Envelope Factor     : Overall relief scaling of crust and base.
    - Volcanic Island Override   : Heavy crust dome with dual-stage detail.
    - Inverse Crust Bypass       : Shoreline bypass preserving low relief.
    - Dynamic Lerp / Morph       : Smooth linear blend between crust and base.
    - Tectonic Subduction Belt   : Squared crust basin with ridge clamping.
    - Stepped Mesa Terraces      : Multi-tier terrace quantization with crust.

Two-Layer Formulas (Continental Crust Silenced):
    - Factored Virtual Crust     : Macro envelope drives floor and peaks.
    - Tibetan High Plateau       : High plateau floor with sine-wave valleys.
    - Razor Ridge / Granite Peaks: Squared base ridges sharpened by relief.
    - Inverted Canyonlands       : Inverted relief carving steep ravines.
    - Soft Natural Saturation    : Hyperbolic tangent organic compression.


MODE 2 CATALOG (20 Total Presets):
-------------------------------------------------------------------------------
Mode 2 allows inspecting isolated wave geometry alongside composite formulas:
    - Presets 1 to 3   : Solo Components (Vertical Base, Horizontal Relief,
                         and Radial Continental Crust).
    - Presets 4 to 8   : 3-Layer Composite Series.
    - Presets 9 to 18  : 2-Layer Series Dual Projections (each 2-layer formula
                         features both [Radial] and [Warped] variants).
    - Presets 19 to 20 : Advanced 3-Layer Hybrids.


[7.0 DISCRETE TILE STEPPING (QUANTIZATION)]
-------------------------------------------------------------------------------
Pressing [SPACE] and [SHIFT + SPACE] cycles the terrain through a power-of-two
tile quantization ring, bounded by minimum and maximum block clamps defined
in config.py:
    OFF -> Smallest Size -> ... -> Largest Size -> OFF

Centroid Grid Anchoring:
Tile sampling evaluates elevation at the exact centroid (+0.5 stride) of
each tile block rather than its top-left edge. This ensures radial islands,
concentric rings, and diagonal ridges remain mathematically centered and
symmetrical across all four quadrants without shifting the visual screen grid.

Visual Representation Across Viewports:
    - In 1D: Smooth sine curves break into crisp, horizontal step-pyramid
             staircases, illustrating discrete elevation plateaus.
    - In 2D: Smooth gradients transform into retro pixel blocks or macro-
             biome chunks (similar to a classic 16-bit overworld map).

To maximize performance, quantized coordinate matrices and radial distance
fields are pre-cached in memory, ensuring that frequency zooming during tile
mode performs zero redundant square-root calculations.


[8.0 DIAGNOSTIC COLOR SUITE, INVERSION & RELIEF NET]
-------------------------------------------------------------------------------
PySineBlend includes pre-baked 1,024-entry Look-Up Tables (LUTs) that map
continuous elevation to color in under 0.1 milliseconds:

    - GREYSCALE : Linear monochrome baseline.
    - MAGMA     : Perceptually uniform high-contrast sequential (black to
                  dark purple, fiery red, yellow, and white).
    - TURBO     : Spectral rainbow curve exposing subtle harmonic creases.
    - VIRIDIS   : Perceptually uniform standard blue-to-yellow colormap.

Color Inversion (Key [I]):
Pressing [I] reverses the active color ramp along its elevation axis in real
time. In Greyscale, this creates an X-ray/film-negative effect; in thermal
palettes, it inverts peak-versus-valley visual polarity.

Topographical Relief Net / Isoline Mode (Key [N]):
Pressing [N] turns the visualization into a topographical isoline net:
    - In 1D: Toggles between solid hypsometric scanline fill and a colored
             vector line trace for the composite curve.
    - In 2D: Replaces the continuous raster surface with a dark blueprint
             vector contour net, evaluating elevation slices across the field.

Dual Evaluation Mechanics:
    - Continuous Mode : Evaluates contour lines using a narrow tolerance
                        bandwidth, creating smooth sub-pixel curves.
    - Discrete Tile Mode: Automatically shifts to geometric cardinal cell-
                        crossing (h_min <= Level <= h_max). Testing whether
                        a level passes through a tile's elevation span
                        guarantees unbroken, strictly 1-tile-thick perimeter
                        outlines with zero gaps on steep cliffs and zero
                        blobs on flat plateaus.


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

    SPACE               : Step tile size coarser (or toggle on).
    SHIFT + SPACE       : Step tile size finer (or toggle off).

    C                   : Cycle active color palette forward.
    SHIFT + C           : Cycle active color palette backward.

    I                   : Toggle palette color inversion on/off.
    N                   : Toggle Topographical Relief Net / 1D Fill mode.

    R                   : Reset active focused channel cycles to default.
    SHIFT + R           : Reset all channels to default configuration.

    ESCAPE / CLOSE      : Clean application shutdown.


[10.0 CONFIGURATION]
-------------------------------------------------------------------------------
All global defaults, display parameters, and balance metrics reside in
config.py:

    SCREEN_WIDTH / HEIGHT     : Desktop window resolution in pixels.
    FPS                       : Display refresh rate target cap (Hz).
    DEFAULT_VIEW_MODE         : Boot viewport mode (Mode 1 or Mode 2).

    DEFAULT_TILE_SIZE         : Starting tile step size in pixels.
    MIN / MAX_TILE_SIZE       : Power-of-two quantization boundary clamps.
    WARP_FACTOR               : Domain warping shear intensity in 2D.

    DEFAULT_NET_ENABLED       : Starting toggle state of the isoline net.
    DEFAULT_NET_INTERVALS     : Number of elevation intervals between 0 and 1.
    DEFAULT_NET_BANDWIDTH     : Tolerance band thickness for contour lines.
    COLOR_NET_BACKGROUND      : Background RGB color for 2D net mode.

    DEFAULT_*_CYCLES          : Starting cycle counts across the screen.
    *_MIN / MAX_CYCLES        : Frequency tuning bounds preventing artifacts.
    CYCLE_ZOOM_RATE           : Continuous exponential zoom multiplier rate.

    CRUST / RELIEF_BUDGET     : Mathematical elevation budget shares.
    MIN_RELIEF_FACTOR         : Minimum relief floor preserving low ripples.


[11.0 PROJECT STRUCTURE]
-------------------------------------------------------------------------------
pysineblend/
│
├── main.py                    # Root bootstrap entry point
├── config.py                  # Central runtime settings and layout constants
├── requirements.txt           # Minimal dependencies (numpy, pygame-ce)
├── README.md                  # System specification and documentation
│
└── wave_inspector/            # Pure Wave Inspector Package
    ├── app.py                 # Application lifecycle, loop, and mesh cache
    ├── formulas.py            # Master formula catalog, math, and 2D specs
    ├── heatmaps.py            # 1,024-slot LUT bakes and array inversion
    ├── input_handler.py       # Event routing and held-key frequency zoom
    ├── state.py               # Shared mutable state machine and sync logic
    ├── wave_model.py          # Pure NumPy 1D and 2D wave synthesis engine
    └── renderers/             # Viewport Renderers
        ├── base_renderer.py   # Typography and dynamic HUD card drawer
        ├── renderer_1d.py     # 4-panel oscilloscope and hypsometric fill
        └── renderer_2d.py     # 2D surface baking and isoline net generator


[12.0 LICENSE]
-------------------------------------------------------------------------------
This project is licensed under the MIT License. See the root LICENSE file
for complete terms.

===============================================================================
                 END OF PYSINEBLEND SPECIFICATIONS & GUIDE
===============================================================================