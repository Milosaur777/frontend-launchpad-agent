---
name: 3d-pie-chart
description: |
  Build production-ready 3D extruded donut/pie charts using React Three Fiber,
  @react-three/drei, and @react-three/postprocessing.
---

# 3D Pie/Donut Chart — Agent Guide

A step-by-step recipe for building a 3D extruded donut chart like the one in
the Rudis DAO project. Covers geometry, materials, animation, mobile perf, and
anti-patterns.

## Architecture Overview

| Layer | Technology | Role |
|---|---|---|
| 3D engine | `three` (>=0.160) | Geometry, materials, renderer |
| React bindings | `@react-three/fiber` (>=9) | Canvas, hooks, JSX composability |
| Helpers | `@react-three/drei` (>=10) | OrbitControls, Environment, ContactShadows |
| Post-processing | `@react-three/postprocessing` | Bloom, tone mapping |
| Entry | `next/dynamic` with `ssr: false` | Client-only mount in Next.js |

**The key insight**: Do NOT use SVG extrusion libraries (`3dsvg`, Three.js SVGLoader
with extrude) for multi-segment pie charts — they merge all paths into a single
geometry with one material. Build each segment as its own `THREE.Shape` +
`THREE.ExtrudeGeometry` instead.

## Step-by-Step Implementation

### Step 1 — Shape Generation

Each donut segment is a `THREE.Shape` drawn as an arc with an inner/outer
radius, then closed back:

```ts
const segs = 32  // arc smoothness
const shape = new THREE.Shape()

// Outer arc: startAngle → endAngle
for (let i = 0; i <= segs; i++) {
  const t = startAngle + (endAngle - startAngle) * (i / segs)
  const x = outerRadius * Math.cos(t)
  const y = outerRadius * Math.sin(t)
  if (i === 0) shape.moveTo(x, y)
  else shape.lineTo(x, y)
}

// Inner arc: endAngle → startAngle (reverse direction)
for (let i = segs; i >= 0; i--) {
  const t = startAngle + (endAngle - startAngle) * (i / segs)
  const x = innerRadius * Math.cos(t)
  const y = innerRadius * Math.sin(t)
  shape.lineTo(x, y)
}
shape.closePath()
```

**Padding between segments**: reduce each segment's angular span by `PADDING`
(≈0.06 rad) on both sides so gaps appear between slices.

### Step 2 — Extrusion

Use `ExtrudeGeometry` with bevels for the 3D look:

```ts
new THREE.ExtrudeGeometry(shape, {
  depth,                        // extrusion height per segment
  bevelEnabled: true,
  bevelThickness: depth * 0.08, // proportional to depth
  bevelSize: depth * 0.08,
  bevelSegments: 8,             // high = smoother edge (desktop)
  curveSegments: 48,            // high = smoother arc (desktop)
})
```

**Vary depth per segment** to make each slice a different height — visually
emphasizes individual segments. For example, map depth proportional to value:
`depth = 0.2 + (value / maxValue) * 0.7`.

### Step 3 — Materials

Use `meshPhysicalMaterial` for the best PBR result:

| Property | Value | Effect |
|---|---|---|
| `metalness` | 0.95 | Mirror-like gold reflections |
| `roughness` | 0.15 | Slight surface micro-texture |
| `transparent` | true | Enable opacity |
| `opacity` | 0.88 | Slightly see-through |
| `transmission` | 0.2 | Glass-like refraction (omit on mobile) |
| `clearcoat` | 0.5 | Glossy clear layer |
| `envMapIntensity` | 3 | Strong environment reflections |
| `emissive` | segment color | Warm self-glow |
| `emissiveIntensity` | 0.2 (idle) / 0.6 (hover) | Subtle to strong glow |
| `side` | `THREE.DoubleSide` | Visible from all angles |

### Step 4 — Growth Reveal Animation

Use a **clipping plane** that rotates from the segment's start edge to its end
edge. This reveals the segment as if it's being drawn from nothing.

**Setup** (in `useEffect`):
```ts
clipPlane.current.normal.set(
  -Math.sin(startAngle), Math.cos(startAngle), 0
)
clipPlane.current.normal.normalize()
clipPlane.current.constant = 0
material.clippingPlanes = [clipPlane.current]
material.localClippingEnabled = true
material.clipShadows = true
material.needsUpdate = true
```

**Animate** (in `useFrame`):
```ts
const elapsed = state.clock.elapsedTime - index * STAGGER
const progress = Math.min(1, elapsed / DURATION)
const eased = 1 - Math.pow(1 - progress, 3)  // cubic ease-out
const angle = paddedStart + (paddedEnd - paddedStart) * eased
clipPlane.current.normal.set(-Math.sin(angle), Math.cos(angle), 0)
clipPlane.current.normal.normalize()
clipPlane.current.constant = 0
```

**Stagger**: each segment starts `STAGGER` seconds after the previous one
(e.g. 0.35s).

**Stop after done**: track the total animation time (`(n-1) * STAGGER + DURATION +
buffer`) and set a `doneRef = true` to skip all `useFrame` work. This is critical
for mobile performance.

### Step 5 — Dynamic Import (Next.js)

Wrap the Canvas scene in `next/dynamic` with `ssr: false`:

```ts
const Scene3D = dynamic(
  () => import("./scene-file").then((m) => m.SceneComponent),
  { ssr: false, loading: () => <Spinner /> }
)
```

This prevents WebGL code from running during SSR/static generation.

### Step 6 — Layout & Camera

The chart lays **flat** — rotate the group `-PI/2` around X to switch
extrusion axis from Z to Y.

```ts
<group ref={spinGroup} position={[0, 0.2, 0]}>
  <group rotation={[-Math.PI / 2, 0, 0]}>
    <DonutSegments />
  </group>
</group>
```

**Nested groups**: the outer group spins on world Y (turntable effect), the
inner group lays the donut flat. Without nesting, Y rotation becomes Z rotation
due to the X rotation.

Camera: `position={[0, 5, 7], fov: 40}` — slightly above and to the side.

**Size guide**: outer radius ≈2.55, inner radius ≈1.275 gives a ~5-unit-wide
donut that fills a 320×420px container nicely.

### Step 7 — Hover Interaction

Track hovered segment index via `useState`. On `onPointerOver`/`onPointerOut`,
scale the mesh and boost emissive intensity:

```ts
scale={hovered ? 1.06 : 1}
emissiveIntensity={hovered ? 0.6 : 0.2}
```

### Step 8 — Lighting & Environment

```ts
<ambientLight intensity={0.3} />
<directionalLight position={[5, 10, 5]} intensity={2} />
<directionalLight position={[-3, 6, -3]} intensity={0.8} />
<pointLight position={[0, 8, 0]} intensity={0.6} color="#FFD700" />
<hemisphereLight args={["#b1e1ff", "#b97a20", 0.5]} />
<Environment preset="sunset" background={false} />
```

The 3-point + hemisphere + HDR environment combo gives the gold/glass material
its rich reflections.

### Step 9 — Orbital Controls

```ts
<OrbitControls
  enablePan={false}
  enableZoom={false}
  autoRotate={false}
  maxPolarAngle={Math.PI / 2.2}
  minPolarAngle={Math.PI / 8}
  target={[0, 0.2, 0]}
/>
```

### Step 10 — Continuous Spin (useFrame location)

**Critical**: `useFrame` must be inside a child of `<Canvas>`, not in the same
component that renders `<Canvas>`. Create a `SceneContent` wrapper component
for all R3F hooks.

```ts
// ❌ WRONG — useFrame outside Canvas context
function Tokenomics3DScene() {
  useFrame(...) // crashes at runtime
  return <Canvas>...</Canvas>
}

// ✅ CORRECT
function SceneContent() {
  useFrame(...) // inside Canvas context
  return <>{/* lights, meshes, controls */}</>
}
function Tokenomics3DScene() {
  return <Canvas><SceneContent /></Canvas>
}
```

## Mobile Optimization

| Feature | Desktop | Mobile (<768px) |
|---|---|---|
| Arc segments | 32 | 12 |
| `curveSegments` | 48 | 16 |
| `bevelSegments` | 8 | 3 |
| `transmission` / `clearcoat` | yes | no |
| Bloom | yes | no |
| ContactShadows | yes | no |

Detect mobile with `window.matchMedia("(max-width: 767px)")` in a `useEffect`.

## Dependencies

```json
{
  "three": ">=0.160",
  "@react-three/fiber": ">=9",
  "@react-three/drei": ">=10",
  "@react-three/postprocessing": "*"
}
```

## Do's and Don'ts

### Do
- Build each segment as an individual `THREE.Shape` + `ExtrudeGeometry`
- Use `next/dynamic` with `ssr: false` for Next.js projects
- Nest groups: outer for Y-rotation, inner for flattening rotation
- Stop `useFrame` hooks after animation completion (set a `doneRef`)
- Scale down geometry quality on mobile
- Use `ErrorBoundary` to catch WebGL failures gracefully

### Don't
- Don't use `3dsvg` or SVG-based extrusion for multi-segment pie charts
  (they merge all paths into one geometry/color)
- Don't call `useFrame` in the same component that renders `<Canvas>`
- Don't set `material.needsUpdate = true` every frame (causes shader
  recompilation)
- Don't use pure black (`#000`) backgrounds — use `#0a0a0a`
- Don't use bounce/spring easing for UI — smooth ease-out only

## File Structure

```
components/
├── tokenomics-3d-scene.tsx   # Canvas + SceneContent (all 3D logic)
├── tokenomics-3d-chart.tsx   # Dynamic import + error boundary wrapper
└── tokenomics.tsx             # Page section, imports Tokenomics3DChart
```

## Quick Reference — Key Constants

```ts
const PADDING = 0.06      // gap between segments
const STAGGER = 0.35      // seconds between segment reveals
const DURATION = 1.2      // seconds per segment reveal animation
const OUTER_RADIUS = 2.55  // desktop, scale proportionally
const INNER_RADIUS = 1.275 // desktop, half of outer
```

## Flow Summary

1. Compute segment angles from data
2. For each: create `THREE.Shape` arc → `ExtrudeGeometry` with bevels
3. Mount each segment as a `<mesh>` with `<meshPhysicalMaterial>`
4. Clip-plane animation reveals segments sequentially
5. `useFrame` on outer group spins the whole donut
6. OrbitControls allows user interaction
7. Error boundary catches WebGL failures
8. Mobile gets simplified geometry + no post-processing
