🇬🇧 English | 🇫🇷 [Français](0004-rendering-responsibilities_FR.md) | 🇪🇸 [Español](0004-rendering-responsibilities_ES.md)

# ADR-0004: Separation of Rendering Responsibilities

## Status
Accepted

## Context
As we added more visual styles (Flip Clock, True Matrix, Cyberpunk), our `ClockEngine` and `DateEngine` became bloated with drawing logic. Business logic (calculating time, managing rotation durations) was heavily mixed with rendering logic (drawing shrinking rectangles, calculating bounding boxes, parsing pixel matrices). 
This monolithic structure made the engines difficult to test, hard to read, and impossible to reuse animations (like the Flip animation) for other types of text.

## Decision
We implemented a strict separation of responsibilities through a **Rendering Pipeline**:
`Data -> Engine -> Animation -> Renderer -> Matrix`

### 1. Why Engines no longer draw
Engines (e.g. `ClockEngine`) are solely responsible for state management and business logic. They know *what* time it is, *what* format it should be in, and *when* it is time to yield to the next rotation. They do not know what a pixel is. This isolation makes them 100% testable using standard Python mocks without needing a physical screen.

### 2. Why Renderers do not know business logic
Renderers (e.g. `CyberpunkRenderer`) are dumb pipes. They take raw strings, coordinates, and themes, and return a rendered image (or manipulate the hardware canvas for complex frame-by-frame animations). A `FlipRenderer` doesn't care if it's animating a Clock or a Date, it just flips characters.

### 3. Reusable Animations and Font Scaling
Because the rendering is isolated, we can implement global effects. For example, "Font Scaling" (for crisp BDF font enlargement) is now a responsibility of the rendering layer. All specialized clocks and renderers benefit from this scale factor without bloating the engine logic.

## Consequences
- **Pros**: 
  - Massive reduction in code duplication.
  - Highly testable components.
  - Extremely easy to add new themes or animations.
- **Cons**: 
  - Slight overhead in passing configuration parameters down the pipeline.
