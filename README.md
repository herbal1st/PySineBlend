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
pygame. The requirements.txt file lists the packages needed by the project.

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


The application opens a window with four stacked wave panels. Use Escape or
the window's close button to exit.

Run main.py from the project root so the application can import config.py and
the wave_inspector package.

[3.0 PROJECT OVERVIEW]
-------------------------------------------------------------------------------
PySineBlend is a standalone application for exploring how mathematical
wave layers combine into a height-like signal.

It displays four horizontal plots:

    1. Base detail wave
    2. Relief multiplier wave
    3. Continental crust wave
    4. Composite result from the selected formula

The first three panels show the input signals. The fourth shows the result of
combining them. This makes it easier to inspect a formula's shape and range
before using similar concepts in a larger procedural generation system.

Wave calculations use NumPy; the plots and interactive window use Pygame.
This is a one-dimensional wave visualization tool. It is not a complete game,
a two-dimensional terrain generator, or a procedural-noise inspector.

[4.0 WHAT THE INSPECTOR SHOWS]
-------------------------------------------------------------------------------
Each component is a smooth, repeating sine wave stretched across the display.
The number of cycles controls how many complete repeats fit from the left edge
to the right edge. More cycles create more frequent peaks and valleys; fewer
cycles create broader shapes.

The component waves are normalized to the range 0.0 to 1.0:

    - The base-detail component is labelled D(x) in its panel.
    - The relief component is labelled R(x).
    - The crust component is labelled C(x).

The formula catalog uses B for base detail, R for relief, and C for crust.
Thus, B in a formula refers to the signal labelled D(x) in the display.

Each component has its own cycle count and starting height. The starting
height sets the wave value at the left edge. The application calculates a
phase offset so the wave begins at that height.

The formula result is clipped to the range 0.0 to 1.0 before it is drawn.
Clipping keeps the displayed composite signal within the normalized range,
even when a formula's raw output goes above or below it.

[5.0 FORMULA CATALOG]
-------------------------------------------------------------------------------
The inspector includes 12 formula presets. Each has a name, a shorthand
expression, and a setting indicating whether it uses the crust component.

Three-layer formulas:

    - Master 3-Layer Budgeting
    - Global Envelope Factor
    - Volcanic Island Override
    - Inverse Crust Bypass
    - Dynamic Lerp / Morph
    - Tectonic Subduction Belt
    - Stepped Mesa Terraces

Two-layer formulas:

    - Factored Virtual Crust
    - Tibetan High Plateau
    - Razor Ridge / Granite Peaks
    - Inverted Canyonlands
    - Soft Natural Saturation

A "layer" is one of the input waves used by a formula. Three-layer formulas
use base, relief, and crust. Two-layer formulas use base and relief only.

The formulas are stored separately from the display code. This keeps the
mathematics easier to read and makes it possible to use or test the formulas
without opening a Pygame window.

[6.0 HOW THE WAVE MATH WORKS]
-------------------------------------------------------------------------------
Each component is calculated across a normalized horizontal coordinate x.
A simplified form of the calculation is:

    wave(x) = 0.5 + 0.5 * sin(2 * pi * cycles * x + phase)

The phase is calculated from the configured starting height. The cycle count
then controls how often the wave repeats across the display.

For each frame, the application:

    1. Builds the base, relief, and crust arrays.
    2. Passes those arrays to the active formula.
    3. Clips the formula output to the range 0.0 to 1.0.
    4. Converts values to pixel positions and draws the four panels.

The calculations operate on whole NumPy arrays rather than using a Python
loop for every horizontal pixel. Pygame draws the resulting plot lines.

[7.0 CONTROLS]
-------------------------------------------------------------------------------
    TAB                 : Select the next formula.
    SHIFT + TAB         : Select the previous formula.
    UP / DOWN           : Focus the next or previous input layer.
    HOLD LEFT           : Reduce the focused layer's cycle count.
    HOLD RIGHT          : Increase the focused layer's cycle count.
    ESCAPE              : Close the inspector.
    WINDOW CLOSE        : Close the inspector.

Left and right adjust the currently focused input component. The composite
panel is not an adjustable input.

Frequency changes are time-scaled. While a key is held, the cycle count is
multiplied or divided by a factor based on the elapsed time for that frame.
This avoids fixed per-key increments and makes the adjustment rate broadly
consistent across different frame rates.

When a formula does not use crust, the crust panel remains visible but is
muted. Focus skips that panel until a three-layer formula is selected.

[8.0 CONFIGURATION]
-------------------------------------------------------------------------------
Runtime and tuning settings are collected in the root config.py file.

Window settings:

    APP_TITLE        : Window caption.
    SCREEN_WIDTH     : Window width in pixels.
    SCREEN_HEIGHT    : Window height in pixels.
    FPS              : Target frame rate.
    BACKGROUND_COLOR : Window background RGB color.

Initial wave settings:

    DEFAULT_BASE_CYCLES   : Starting base-detail cycles across the width.
    DEFAULT_RELIEF_CYCLES : Starting relief cycles across the width.
    DEFAULT_CRUST_CYCLES  : Starting crust cycles across the width.

    BASE_START   : Base-detail value at the left edge.
    RELIEF_START : Relief value at the left edge.
    CRUST_START  : Crust value at the left edge.

Formula parameters:

    CRUST_BUDGET      : Crust contribution in formulas that use a crust
                        budget.
    RELIEF_BUDGET     : Relief contribution in formulas that use a relief
                        budget.
    MIN_RELIEF_FACTOR : Minimum relief contribution in the master formula.

Frequency controls:

    CYCLE_ZOOM_RATE : Rate used by the held-key multiplier.
    BASE_MIN_CYCLES : Lowest allowed base-detail cycle count.
    BASE_MAX_CYCLES : Highest allowed base-detail cycle count.
    RELIEF_MIN_CYCLES: Lowest allowed relief cycle count.
    RELIEF_MAX_CYCLES: Highest allowed relief cycle count.
    CRUST_MIN_CYCLES: Lowest allowed crust cycle count.
    CRUST_MAX_CYCLES: Highest allowed crust cycle count.

The current configured cycle zoom rate is 0.75 per second. At a target of
60 FPS, this produces about a 1.25% increase per frame while Right is held.
The rate and each component's lower and upper bounds can be changed
independently in config.py.

Drawing colors and panel layout values are also configurable there. Adjust
those values to change the appearance without changing the wave calculations.

[9.0 PROJECT STRUCTURE]
-------------------------------------------------------------------------------
└── project-root/
    ├── main.py
    ├── config.py
    ├── requirements.txt
    ├── README.md
    ├── LICENSE
    └── wave_inspector/
        ├── __init__.py
        ├── app.py
        ├── formulas.py
        ├── renderer.py
        ├── state.py
        └── wave_model.py

Module responsibilities:

    main.py
        Application entry point.

    config.py
        Window settings, initial wave values, formula parameters, cycle
        adjustment rate, cycle limits, and drawing settings.

    wave_inspector/app.py
        Pygame window lifecycle, keyboard input, frame timing, and
        coordination between the model and renderer.

    wave_inspector/formulas.py
        Formula preset model and the 12 formula implementations.

    wave_inspector/wave_model.py
        Phase calculation, component wave generation, and composite math.
        This module does not depend on Pygame.

    wave_inspector/state.py
        Selected formula, focused component, and current cycle counts.

    wave_inspector/renderer.py
        Four-panel plots, grids, titles, selection border, and composite
        range display.

[10.0 PROJECT SCOPE]
-------------------------------------------------------------------------------
The application includes:

    - One-dimensional sine-wave components.
    - A catalog of 12 two-layer and three-layer formulas.
    - Interactive formula and component selection.
    - Time-scaled cycle adjustment with separate configurable bounds.
    - A four-panel Pygame visualization.
    - NumPy-based wave calculations separated from Pygame rendering.

[11.0 LICENSE]
-------------------------------------------------------------------------------
This project is licensed under the MIT License. See the root LICENSE file
for the complete terms.

===============================================================================
                 END OF PYSINEBLEND SPECIFICATIONS & GUIDE
===============================================================================