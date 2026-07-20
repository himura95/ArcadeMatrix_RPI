🇬🇧 [English](0004-rendering-responsibilities.md) | 🇫🇷 [Français](0004-rendering-responsibilities_FR.md) | 🇪🇸 Español

# ADR-0004: separación de responsabilidades de renderizado

## Status
Accepted

## Context
A medida que añadíamos más estilos visuales (Flip Clock, True Matrix, Cyberpunk), nuestros `ClockEngine` y `DateEngine` se fueron llenando de lógica de dibujo. La lógica de negocio (calcular la hora, gestionar las duraciones de rotación) estaba muy mezclada con la lógica de renderizado (dibujar rectángulos que se encogen, calcular bounding boxes, parsear matrices de píxeles). 
Esta estructura monolítica hacía que los engines fueran difíciles de probar, complicados de leer e imposibles de reutilizar animaciones (como la animación Flip) para otros tipos de texto.

## Decision
Implementamos una separación estricta de responsabilidades a través de un **Rendering Pipeline**:
`Data -> Engine -> Animation -> Renderer -> Matrix`

### 1. Por qué los Engines ya no dibujan
Los Engines (p. ej. `ClockEngine`) son responsables únicamente de la gestión del estado y la lógica de negocio. Saben *qué* hora es, *en qué* formato debe estar y *cuándo* ha llegado el momento de ceder a la siguiente rotación. No saben qué es un píxel. Este aislamiento hace que sean 100 % testeables usando mocks estándar de Python sin necesidad de una pantalla física.

### 2. Por qué los Renderers no conocen la lógica de negocio
Los Renderers (p. ej. `CyberpunkRenderer`) son conductos tontos. Toman cadenas en bruto, coordenadas y temas, y devuelven una imagen renderizada (o manipulan el canvas del hardware para animaciones complejas frame a frame). A un `FlipRenderer` no le importa si está animando una Clock o una Date; simplemente voltea caracteres.

### 3. Animaciones reutilizables y escalado de fuentes
Como el renderizado está aislado, podemos implementar efectos globales. Por ejemplo, el «Font Scaling» (para ampliar con nitidez fuentes BDF) ahora es responsabilidad de la capa de renderizado. Todos los relojes especializados y los renderers se benefician de este factor de escala sin inflar la lógica de los engines.

## Consequences
- **Pros**: 
  - Reducción masiva de duplicación de código.
  - Componentes muy testeables.
  - Extremadamente fácil añadir nuevos temas o animaciones.
- **Cons**: 
  - Ligera sobrecarga al pasar parámetros de configuración a lo largo del pipeline.
