# liquid-glass (glass.samasante.com)

Open-source React component for an Apple-style "liquid glass" material.

- Package: `@samasante/liquid-glass` (npm, MIT, v0.1.1 at index time)
- Repo: https://github.com/samasante/liquid-glass
- Demo and docs: https://glass.samasante.com
- Peer deps: `react` and `react-dom` 18 or later. No runtime dependencies.

## Install

```bash
npm i @samasante/liquid-glass
```

## How it works (summary in our words)

The component wraps a styled box. The box becomes a glass layer: it frosts and
tints what is behind it and gets a bright edge. The `children` stay sharp on top.

Browser support has one limit:

| Mode | Chrome / Edge | Safari / Firefox |
|---|---|---|
| Plain wrap (bends the live page) | bends + frosts | frosts and tints only, no bend |
| In-place lens (`size` + `center`, bends its own `children`) | yes | yes |
| `refract={node}` (bends a copy of a node you give it) | yes | yes |
| `src` / `draw` + `lenses` (video or canvas, on the GPU) | yes | yes |

Rule of thumb: if the bend must show in Safari and Firefox, give the lens a copy
to bend (`refract`, in-place geometry, or `src`). If frost and tint are enough,
a plain wrap is the cheapest option.

## Minimal use

```tsx
import { Glass } from "@samasante/liquid-glass";

export function SaveButton() {
  return (
    <Glass style={{ background: "rgba(59,130,246,0.35)", borderRadius: 14, padding: "12px 22px" }}>
      Save
    </Glass>
  );
}
```

Read the repo README for the full prop list (`optics`, `refract`, `behind`,
`lenses`) before you use the advanced modes. The repo has two example files:
`examples/GlassNotification.tsx` and `examples/GlassVideoControls.tsx`.
