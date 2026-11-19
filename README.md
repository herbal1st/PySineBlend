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
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python main.py

macOS or Linux:
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
adjustments, elevation budget splits, per-layer spatial offsets, coordinate
warping, discrete tile steps, and color palettes translate from single-line
curves into rich continuous 2D landscapes.

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
wave phase offsets at the origin.

Per-Layer Spatial Positioning:
Each wave role maintains its own independent (x, y) spatial offset, allowing
you to pan all layers together or slide individual waves, bands, and circular
centers relative to one another in real time.

Live Dynamic Elevation Budgeting (Zero-Clipping Invariant):
To prevent terrain from shearing off against an artificial flat ceiling,
formulas divide available elevation into live, adjustable budgets: Crust
Budget (CB) and Relief Budget (RB), which strictly sum to 1.00 (for example,
0.40 C / 0.60 R). Shifting more budget to Crust lifts broad continents out of
the ocean; shifting more budget to Relief plunges continents and emphasizes
towering peaks. Because CB + RB always equals 1.00, peaks never clip flat,
and inland valleys remain naturally elevated above sea level on high ground.


[5.0 DUAL-VIEWPORT ARCHITECTURE]
-------------------------------------------------------------------------------
Switch seamlessly between viewports at any time using keys '1' and '2':

MODE 1: 1D OSCILLOSCOPE (Key [1])
-------------------------------------------------------------------------------
Presents four vertically stacked real-time oscilloscope panels:
    - Panel 1: Base Detail wave D(x).
    - Panel 2: Relief Multiplier envelope M(x).
    - Panel 3: Continental Crust tectonic floor C(x).
    - Panel 4: Composite Result from the active formula, displaying the live
               BUDGET: [ 0.40 C / 0.60 R ] readout.

Smart Panel Selection & Live Budget Scrubbing:
Click directly on Panel 1, 2, 3, or 4 with either mouse button (or cycle with
UP/DOWN) to select focus. On 2-layer formulas where Relief is silenced, clicks
on Panel 2 are safely ignored and UP/DOWN skips straight between Panels 1, 3,
and 4. The active panel's top-left title card highlights with a blue frame
and cyan text without shifting its layout. Selecting Panel 4 lets you drag
with RMB or hold LEFT/RIGHT arrows to shift the Crust/Relief elevation budget
in real time, while SHIFT + Right-Drag / Left-Drag adjusts all three wave
layers together.

Panel 4 Dual-Mode Visualization:
    - Standard Mode: Renders a solid hypsometric color fill under the curve
                     down to the baseline using the active color palette.
    - Net Mode (Key [N]): Replaces the fill with a crisp, multi-colored vector
                     trace line colored according to height.

Idle Frame Caching & In-Place Fill:
Mode 1 renders its four panels, fills, and trace lines onto an offscreen
cached surface and only rebuilds when wave frequencies, budgets, offsets,
focus, formulas, stepping, or palettes change. Both the solid fill and the
Net trace paint directly into that cached surface using reusable scratch
buffers with zero temporary surface allocations. While idle, redrawing the
viewport takes a single surface copy.


MODE 2: 2D SPATIAL SYNTHESIZER (Key [2])
-------------------------------------------------------------------------------
Projects wave roles across a continuous 2D surface on a 16:9 canvas:
    - Base Detail (B)      : Mapped to Vertical Stripes along X (dense ridges).
    - Relief Multiplier (R): Mapped to Horizontal Bands along Y (silenced on
                             2-layer formulas).
    - Continental Crust (C): Mapped to Concentric Radial Rings (central dome
                             or pond), or Horizontal Bands along Y when
                             Warped ([P]) is active on a 2-layer formula.

2D Positioning, Consistent Circular Ponds & Proportional Zoom:
Plain Left-Drag pans all wave layers together 1:1 with the cursor. Holding
SHIFT + Left-Drag moves only the selected layer: Base slides vertical
stripes left/right, Relief slides horizontal bands up/down, and Crust moves
the circular dome/pond center anywhere in 2D (even off-screen to sculpt
sweeping coastlines). Because Crust (C) owns the circular dome on both
2-layer and 3-layer formulas, dragging the pond off-center and switching
formulas with TAB keeps the pond in the exact same spot with no jump.

Zooming also stays visually predictable: linear waves (Base stripes, Relief
bands, and 2-layer Warped Crust bands) zoom around the center of the screen
so patterns do not drift toward a corner, while off-center circular Crust
domes stay anchored on their own circle centers so ripples grow and shrink
right around the pond you placed. When zooming all active layers together, a
shared limit clamp stops scaling at the first layer boundary hit so wave
frequency ratios stay locked at both zoom extremes (hold SHIFT to push an
individual layer to its own min/max limit).

Dual-Row Channel & Budget Card:
Below the top HUD card sits the blue-bordered Channel & Budget card:
    - Top Row (CHANNEL FOCUS): Displays B, R, and C cycle counts. Click any
      active letter or press SHIFT + UP/DOWN to switch between layers; the
      active channel is framed in blue with cyan text. Inactive channels (such
      as R: Silenced on 2-layer formulas) ignore clicks automatically.
    - Bottom Row (BUDGET): Displays [ 0.40 C / 0.60 R ]. Press UP/DOWN (or
      click directly on the budget cell) to jump between the channel row and
      the budget row, framing the budget cell in blue. When focused, dragging
      horizontally with RMB or holding LEFT/RIGHT arrows smoothly shifts the
      tectonic Crust/Relief split using dampened mouse sensitivity so
      movements stay steady even on slower PCs.

Perspective / Projection Geometry (Key [P]):
Pressing [P] toggles between two spatial projection models at runtime:
    - RADIAL : 2-layer formulas pair vertical Base ridges with a circular
               Crust island or pond. 3-layer formulas add horizontal Relief
               bands over that same circular Crust dome.
    - WARPED : The secondary wave layer (Relief on 3-layer formulas, or Crust
               switched to horizontal bands on 2-layer formulas) bends and
               shears Base coordinates (X_warp = X + offset), turning rigid
               stripes into serpentine mountain belts and fault lines.


[6.0 FORMULA CATALOG & PRESETS]
-------------------------------------------------------------------------------
The inspector maintains bi-directional state synchronization between viewports:

MODE 1 CATALOG (11 Composite Formulas):
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

Two-Layer Formulas (Relief Multiplier Silenced):
    - Factored Virtual Crust     : Crust drives both ground floor and peaks.
    - Tibetan High Plateau       : High crust plateau carved with sine valleys.
    - Razor Ridge / Granite Peaks: Squared base ridges sharpened by crust.
    - Inverted Canyonlands       : Inverted crust carving steep ravines.
    - Soft Natural Saturation    : Smooth hyperbolic tangent compression.


MODE 2 CATALOG (14 Total Presets):
-------------------------------------------------------------------------------
Mode 2 allows inspecting isolated wave geometry alongside composite formulas:
    - Presets 1 to 3  : Solo Components (Vertical Base, Horizontal Relief,
                        and Radial Continental Crust).
    - Presets 4 to 9  : 3-Layer Composite Series (Master Budgeting, Global
                        Envelope, Volcanic Island, Inverse Bypass, Dynamic
                        Lerp, and Tectonic Subduction).
    - Presets 10 to 14: 2-Layer Series (Virtual Crust, Tibetan Plateau, Razor
                        Ridge, Inverted Canyonlands, Soft Saturation; toggled
                        via [P] between Radial and Warped views).


[7.0 DISCRETE TILE STEPPING & INTERACTIVE SCRUBBING]
-------------------------------------------------------------------------------
Pressing [SPACE] and [SHIFT + SPACE] cycles the terrain through a power-of-two
tile quantization ring, bounded by minimum and maximum block clamps defined
in config.py:
    OFF -> Smallest Size -> ... -> Largest Size -> OFF

Centroid Grid Anchoring & Color-Before-Expand:
Tile sampling evaluates elevation at the exact center (+0.5 stride) of each
tile block rather than its top-left corner. This ensures radial islands,
concentric rings, and shifted waves align cleanly to the pixel grid without
jittering as patterns move through tiles.

To maximize speed, wave math and color Look-Up Table mapping happen directly
on the tiny coarse grid (e.g., evaluating and coloring only 6,820 points at
16px tile size instead of 1.74 million full-screen pixels). The compact colored
surface is then stretched cleanly onto the display surface via hardware-
accelerated SDL scaling, avoiding large intermediate buffers completely.

Visual Representation Across Viewports:
    - In 1D: Smooth sine curves break into crisp, horizontal step-pyramid
             staircases, illustrating discrete elevation plateaus.
    - In 2D: Smooth gradients transform into retro pixel blocks or macro-
             biome chunks (similar to a classic 16-bit overworld map).

Interactive Smooth Scrubbing & Settle-Debounce (Mode 2):
When Tile Stepping is OFF and you tune frequencies, scrub the elevation
budget, or drag positions in Mode 2 (via Right-Drag, Left-Drag, SHIFT+Drag,
or LEFT/RIGHT keys), the engine temporarily shifts into a lighter scrubbing
preview instead of recalculating all 1.74 million pixels every frame:
    - Endpoint-Aligned (N + 1) Grid: Evaluates a precomputed sub-sampled mesh
      (SCRUB_SUB_SAMPLE_FACTOR, default 4x smaller) whose outer edges align
      exactly with the full-resolution screen corners so terrain never shifts.
    - Smooth Upscaling: In standard color mode, the compact preview grid is
      colored first and stretched smoothly onto the screen using bilinear
      scaling. In Relief Net mode, the same coarse grid feeds a smart
      cell-culled contour pass (detailed in Section 8.0) so contour lines
      stay razor-sharp while moving.
    - Instant Mouse Release & Keyboard Settle: Releasing a mouse drag settles
      scrubbing immediately back to full 1760x990 clarity; keyboard scrubbing
      settles automatically after a brief pause (SCRUB_SETTLE_DELAY). One-shot
      toggles (palettes, formulas, perspectives, resets) render crisply right
      away.


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
Both normal and inverted 1,024-entry LUTs are pre-baked once at startup.
Pressing [I] swaps the active table instantaneously with zero runtime
re-baking or array copying. In Greyscale, this creates an X-ray/film-negative
effect; in thermal palettes, it inverts peak-versus-valley visual polarity.

Topographical Relief Net / Isoline Mode (Key [N]):
Pressing [N] turns the visualization into a topographical contour map:
    - In 1D: Toggles between solid hypsometric scanline fill and a colored
             vector line trace painted in one vectorized NumPy pass.
    - In 2D: Replaces the continuous raster surface with a dark blueprint
             contour map, tracing elevation slices across the field.

Triple Evaluation Mechanics:
    - Continuous Mode (Settled — Single-Pass Direct Paint): Instead of testing
      every elevation band in a separate loop, the engine measures how close
      each pixel is to its nearest contour interval in one vectorized math
      pass using reusable scratch memory. It clears the canvas to the dark
      blueprint color and paints only the ~3-5% active contour pixels straight
      into display memory, skipping empty background writes altogether.
    - Interactive Scrubbing Net Mode (Coarse-Cell Culling): While dragging or
      zooming with Net ON (and Tile Stepping OFF), Mode 2 evaluates the shared
      4x coarse wave grid and checks the minimum and maximum height of each
      cell's four corners. Cells sitting entirely between contour lines
      (typically 80-90% of the screen) are skipped immediately; only the
      remaining active cells are smoothly interpolated up to native 1760x990
      pixel precision, keeping contour lines crisp and 1-pixel thin mid-motion
      with zero blur before snapping to full-resolution math on settle.
    - Discrete Tile Mode (Net + Tiles): Instead of scaling up thick blocks or
      scanning 1.74 million pixels, Mode 2 checks horizontal and vertical tile
      boundaries directly on the compact tile grid and stamps strictly
      1-pixel-thick colored outlines along tile seams via zero-copy strided
      surface slices.


[9.0 CONTROLS & KEYBOARD / MOUSE SHORTCUTS]
-------------------------------------------------------------------------------
Universal Rule: Unmodified inputs operate globally across ALL layers together;
holding [SHIFT] acts as a "layer magnifier/selector" isolating only the active
selected layer.

    1 / 2               : Switch to Mode 1 (1D Oscilloscope) or Mode 2 (2D).

    TAB / SHIFT + TAB   : Cycle to next / previous formula preset.

    UP / DOWN           : - Mode 1: Switch panel focus (Panel 1 -> Panel 2 ->
                            Panel 3 -> Panel 4). Automatically skips silenced
                            Panel 2 on 2-layer formulas.
                          - Mode 2: Toggle vertical focus between the Channel
                            Focus row and the Elevation Budget row.

    SHIFT + UP / DOWN   : Mode 2 only: Cycle horizontal channel focus across
                          active wave layers (Base -> Relief -> Crust).

    CLICK PANEL (MODE 1): Click any active Panel 1-4 (LMB or RMB) to focus it
                          immediately; silenced Panel 2 clicks are ignored.
    CLICK CARD (MODE 2) : Click B, R, C, or the BUDGET cell inside the
                          blue-bordered card to select it immediately.

    LEFT DRAG           : Pan all wave layers together 1:1 with the cursor.
    SHIFT + LEFT DRAG   : Move ONLY the currently selected layer (or all when
                          Panel 4 / Budget is selected).

    RIGHT DRAG          : - On Wave Layers: Proportionally zoom ALL active
                            wave channels together, preserving frequency ratios
                            (drag right to zoom IN / wider features; drag left
                            to zoom OUT / denser features).
                          - On Panel 4 (Mode 1) or Budget Row (Mode 2):
                            Smoothly scrub the Crust/Relief elevation budget
                            with gentle, dampened mouse sensitivity.
    SHIFT + RIGHT DRAG  : Zoom ONLY the currently selected wave layer.

    HOLD RIGHT / LEFT   : Keyboard mirror of Right-Drag:
                          - On Wave Layers: Proportionally zoom ALL active
                            channels together (Right = zoom IN / wider waves;
                            Left = zoom OUT / denser waves).
                          - On Panel 4 (Mode 1) or Budget Row (Mode 2):
                            Continuously shift the Crust/Relief budget split.
    SHIFT + RIGHT / LEFT: Zoom ONLY the currently selected wave layer.

    SPACE               : Step tile size coarser (or toggle on).
    SHIFT + SPACE       : Step tile size finer (or toggle off).

    C / SHIFT + C       : Cycle active color palette forward / backward.

    I                   : Toggle palette color inversion on/off.
    P                   : Toggle spatial perspective (Mode 2 only: Radial/Warped).
    N                   : Toggle Topographical Relief Net / 1D Fill mode.

    R                   : Reset ALL channels' frequencies, spatial offsets, and
                          the Crust/Relief elevation budget to defaults.
    SHIFT + R           : Reset ONLY the currently selected channel's frequency
                          and offset (in Mode 1 with Panel 4 selected, resets
                          all 3 channels and the budget).

    ESCAPE / CLOSE      : Clean application shutdown.


[10.0 PROJECT STRUCTURE]
-------------------------------------------------------------------------------
pysineblend/
│
├── main.py                    # Root bootstrap entry point
├── config.py                  # Central runtime settings
├── requirements.txt           # Minimal dependencies (numpy, pygame-ce)
├── MANUAL.txt                 # Complete config.py variable guide & metrics
├── README.md                  # System specification and documentation
│
└── wave_inspector/            # Pure Wave Inspector Package
    ├── app.py                 # Lifecycle, timers & dynamic config-driven meshes
    ├── contour_net.py         # Single-pass isolines, cell culling & tile edges
    ├── formulas.py            # Master formula catalog, math, and 2D specs
    ├── heatmaps.py            # Pre-baked normal & inverted 1,024-slot LUTs
    ├── input_handler.py       # Smart click focus, mouse drags & SHIFT routing
    ├── state.py               # Shared state machine, offsets, hitboxes & scrub
    ├── wave_model.py          # Pure NumPy 1D/2D waves, dynamic centers & mesh
    └── renderers/             # Viewport Renderers
        ├── base_renderer.py   # Typography, cached alpha cards & HUD drawer
        ├── renderer_1d.py     # 4-panel oscilloscope & vectorized Net trace
        └── renderer_2d.py     # Color-before-expand 2D baking, hitboxes & net


[11.0 LICENSE]
-------------------------------------------------------------------------------
This project is licensed under the MIT License. See the root LICENSE file
for complete terms.

===============================================================================
                 END OF PYSINEBLEND SPECIFICATIONS & GUIDE
===============================================================================