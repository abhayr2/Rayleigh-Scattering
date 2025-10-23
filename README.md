# Rayleigh Scattering Simulation

A real-time physics simulation demonstrating Rayleigh scattering of light through an atmospheric medium using Pygame.

## Overview

This program visualizes how light from the sun scatters when passing through a particle-filled atmosphere before reaching Earth. It demonstrates the physical principles behind why the sky appears blue and sunsets appear red.

## Features

- **Real-time ray propagation**: 30 initial white light rays emanating from a sun source
- **Particle scattering**: 200 atmospheric particles (atoms) that cause light to scatter
- **Color-based physics**: 
  - White rays represent initial sunlight
  - Blue rays represent scattered short-wavelength light
  - Red rays represent transmitted long-wavelength light (non-scattering)
- **Multi-generation scattering**: Up to 2 generations of scattering events
- **Segmented Earth visualization**: Inner circle divided into 8 labeled wedges (a-h)
- **Real-time statistics**: Displays count of white, red, and blue rays hitting each Earth segment

## Requirements

- Python 3.x
- Pygame

## Installation

```bash
pip install pygame
```

## Usage

```bash
python rayleigh_scattering.py
```

The simulation runs in fullscreen mode. Press the window close button or use system shortcuts to exit.

## Simulation Parameters

- **Sun position**: Left edge of screen, vertically centered
- **Earth (inner blue circle)**: Radius of 200 pixels, centered in right two-thirds of screen
- **Atmosphere (annulus)**: Region between inner circle (radius 200) and outer circle (radius 400)
- **Atoms**: 200 particles of radius 10, randomly distributed in the atmospheric annulus
- **Ray speed**: 5 pixels per frame at 60 FPS
- **Maximum scattering generations**: 2

## Physics Model

### Scattering Behavior

When a white ray collides with an atom:
- Spawns 1 red ray (continues forward, no further scattering)
- Spawns 8 blue rays (scattered at angles: ±0.5, ±0.35, ±0.2, ±0.05 radians)

When a blue ray collides with an atom:
- Spawns 8 additional blue rays (same angular distribution)

Red rays do not scatter upon collision.

### Ray Termination

Rays stop extending when they:
- Reach the right edge of the screen
- Hit the inner blue circle (Earth's surface)
- Collide with an atom (if scattering is enabled)

## Display Elements

- **Yellow circle**: The sun (left edge)
- **Grey circles**: Atmospheric particles
- **Light blue filled circle**: Earth's surface
- **Dark blue circle outline**: Atmosphere boundary
- **Dark blue radial lines**: Earth surface segments (a-h)
- **Brown line**: Right edge boundary
- **White text**: Ray counts per segment (W: white, R: red, B: blue)

## Code Structure

### Main Components

- `RaySegment` class: Manages individual light ray behavior, collision detection, and propagation
- `spawn_scatter()`: Generates new rays when scattering occurs
- `clamp_endpoint()`: Ensures rays don't exceed screen boundaries
- Main loop: Handles rendering, updates, and statistics

### Key Variables

- `MAX_GENERATION`: Limits scattering depth (set to 2)
- `atom_radius`: Size of scattering particles (10 pixels)
- `blue_radius`: Earth radius (200 pixels)
- `outer_blue_radius`: Atmosphere outer boundary (400 pixels)

## Scientific Interpretation

This simulation models Rayleigh scattering, the phenomenon responsible for:
- Blue sky during daytime (short wavelength light scatters more)
- Red sunsets (long wavelength light penetrates atmosphere)
- Diffuse illumination on Earth's surface

The color-coded rays represent:
- **White**: Direct sunlight (all wavelengths)
- **Blue**: Scattered short-wavelength light (violet/blue spectrum)
- **Red**: Transmitted long-wavelength light (red/orange spectrum)

