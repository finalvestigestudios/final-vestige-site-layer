# Color Contrast Spot Check — Proposed Token Pairings

Calculated by applying WCAG relative luminance and contrast-ratio formula to the exact proposed opaque hex values in `design-tokens.css`. **Not** a complete audit of rendered text over photographs, gradients, translucency, anti-aliasing, font weight or interactive states.

| Foreground | Background | Contrast ratio | Assessment for normal text |
|---|---|---:|---|
| Parchment #F4EFE6 | Ink #090A0A | 17.31:1 | Meets AA 4.5:1 |
| Muted #B8B1A6 | Ink #090A0A | 9.32:1 | Meets AA |
| Antique gold #B8955E | Ink #090A0A | 7.08:1 | Meets AA |
| Highlight gold #C7A66C | Ink #090A0A | 8.59:1 | Meets AA |
| Parchment #F4EFE6 | Raised #171715 | 15.67:1 | Meets AA |
| Antique gold #B8955E | Raised #171715 | 6.41:1 | Meets AA |
| Ink #090A0A | Paper #E9E0D1 | 15.15:1 | Meets AA |
| **Antique gold #B8955E** | **Paper #E9E0D1** | **2.14:1** | **Fails AA for normal text** |
| Muted #B8B1A6 | Raised #171715 | 8.44:1 | Meets AA |

**Design decision:** Do not place thin gold catalogue text on warm evidence paper. Use near-black ink labels on paper; reserve gold for lines, foil marks or non-text decoration there. Re-test actual blended surfaces and focus-state borders during implementation.
