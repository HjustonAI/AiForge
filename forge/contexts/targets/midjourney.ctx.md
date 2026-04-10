<!-- @meta
  name: midjourney
  tags: image-generation, diffusion, photorealism, typography, v8-alpha
  priority: 7
  category: generative
  last_validated: 2026-04-03
-->

## Mental Model

V8 Alpha is a **literal executor**, not an artistic interpreter. This is the defining cognitive shift. V7 resolved prompt ambiguity with automatic aesthetic polish — dramatic lighting, painterly coherence, cinematic drama appeared without being asked for. V8 stripped that away entirely. When you leave something unspecified, V8 defaults to a neutral, clinical, flat photorealism. Not bad. Not wrong. Just empty.

Every sentence in a V8 prompt is a physics directive. The model reads natural language and builds a spatial map from syntactic relationships — which surfaces catch which light, where subjects stand relative to each other, what texture a material has. Because of this architecture, keyword salads fracture the spatial model. "Portrait, woman, neon, cyberpunk, highly detailed" gives the model six disconnected facts with no spatial relationships. The result is a subject floating in a vibe.

The corollary: V8 is deeply responsive to specificity. Explicit light source + angle + quality triggers the full atmospheric pipeline. Explicit lens characteristics activate photographic realism. Explicit medium declaration unlocks illustration mode. The model rewards telling it *exactly* what to render because it will render *exactly* what you tell it.

Write to V8 as if briefing a supremely skilled photographer who has never seen your subject before and will not guess.

## Prompt Architecture [OVERRIDE]

**V8 prompt structure — in order:**

1. **Subject** — natural language sentence describing the primary subject with physical attributes. No comma lists.
2. **Action + Environment** — what they're doing, where, with specific spatial detail.
3. **Lighting** *(mandatory)* — source, angle, quality, interaction with surfaces. e.g. *"Single softbox 45° camera-left, casting a deep shadow along the jaw. Warm 4200K."*
4. **Medium/Lens** — camera body + lens, film stock OR artistic medium + technique. e.g. *"Shot on a Leica M11 with 50mm Summilux, Kodak Portra 400, slight grain"* or *"Watercolor and ink wash, loose expressive brushwork."*
5. **Atmosphere** *(optional)* — weather, air quality, secondary environmental details.
6. **Reference flags** *(optional)* — `--sref [URL] --sw 50` OR `--p mID`. Never both.
7. **Parameter block** — `--ar [ratio] --s [calibrated] --style raw (if photo) --v 8`
8. **High-compute flags** *(final render only)* — `--hd` and/or `--q 4` appended last.

**Compressed example:**
```
A retired deep-sea diver in her 70s sitting at a cluttered kitchen table, sorting through old brass diving equipment. Kitchen window light from the left, soft overcast diffusion, rim light catching the brass surfaces. Shot on a Hasselblad 503CW with 80mm Zeiss, Fuji Pro 400H, muted blue-green color grade. --ar 4:5 --s 120 --style raw --v 8
```

**Skeleton for illustration:**
Replace medium with artistic medium declaration, raise `--s 300-600`, drop `--style raw`.

## Leverage Points

**1. Literal text rendering** — V8 renders readable typography when text is batched in separate double-quote clusters: `"Neon" "Ghost"` not `"Neon Ghost"`. Limit to 1-4 words per cluster. Use `--style raw --s 50` for maximum typographic accuracy.

**2. Extreme --no fidelity** — V8 honors negative prompts with near-literal compliance. `--no background, shadows, props, environmental clutter` produces clean studio isolation suitable for e-commerce and UI assets. This is far more reliable than in V7.

**3. Photorealism via --style raw + low --s** — Combining `--style raw` with `--s 50-100` strips all algorithmic polish and produces documentary-grade realism. Trigger for technical shots, product photography, before/after documentation.

**4. 2K native resolution via --hd** — Unlike V7's post-generation upscaling, --hd bakes native 2K at generation time. Non-reversible — must be decided pre-generation. Reserve for final render confirmation only.

**5. Multi-subject coherence via --q 4** — Forces the diffusion model to render background subjects, secondary figures, and micro-textures with full coherence. Eliminates V8's default tendency to blur complex backgrounds ("Minecraft effect").

**6. Strict --sref mapping** — V8 applies style references with aggressive literalism — color, texture, medium transfer at high fidelity. Start at `--sw 50` (not default 100) to prevent style overwhelming text intent. Scale to `--sw 300-400` for total aesthetic override.

**7. Personalization amplification** — `--p` shifts V8's clinical baseline toward the user's taste profile. Strength governed by `--s`: high stylize = strong personalization pull. Works cleanly with Moodboards via `--p mID`.

## Failure Modes & Repair

**FAILURE: Keyword salad** — "portrait, neon, cyberpunk, 8k, highly detailed, trending on artstation"
WHY: V8's spatial parser requires syntactic relationships. Comma-separated tags produce disconnected attention, subjects float in generic vibes, spatial coherence collapses.
REPAIR: Rewrite as connected sentences. "A woman in a neon-lit cyberpunk district, sharp macro detail on rain-soaked leather jacket."

**FAILURE: No lighting directive**
WHY: V8 has no default aesthetic. No lighting instruction = flat clinical exposure, zero depth.
REPAIR: Always add `[source] from [angle], [quality], [interaction]`. Minimum: "Soft overcast ambient light from above."

**FAILURE: --oref or --cref appended to V8 prompt**
WHY: Both explicitly unsupported in V8 Alpha — will fail or be silently ignored.
REPAIR: Route entire request to `--v 7` with `--oref [URL] --ow 150`.

**FAILURE: --hd + --q 4 on exploratory prompts**
WHY: 16x GPU cost, 16x generation time, Relax mode disabled. Credits vaporize during ideation.
REPAIR: Run standard V8 for exploration. Append both flags only to confirmed final composition.

**FAILURE: Long text string in a single quote block** — `"Welcome to the Midnight Diner"`
WHY: Attention mechanism mangles long continuous token strings onto geometry, producing typos and character bleed.
REPAIR: `"Welcome" "to the" "Midnight Diner"` — max 4 words per cluster, always double quotes.

**FAILURE: Leaving --s at default 100 for illustration**
WHY: V8 baseline is hyper-realistic. --s 100 produces uncanny semi-photo renders for art mediums.
REPAIR: `--s 300-600` for illustration, concept art, vector design. `--s 50-150` for photography.

**FAILURE: Mixing --sref with Moodboard codes (--p mID)**
WHY: Syntax conflict — these are mutually exclusive reference systems in V8.
REPAIR: Use one per prompt. Moodboard for macro-aesthetic baseline; --sref for precise style extraction.

**FAILURE: --sv 6 with --hd or --q 4**
WHY: Legacy style engine, costs 4x, immediately errors when combined with high-compute flags.
REPAIR: Use default --sv 7 (free, fast, compatible with --hd and --q 4).

**FAILURE: Editing V8 image via Midjourney web Editor**
WHY: Vary Region, Pan, and Zoom run on V6.1 model — inpainted regions degrade in anatomical coherence and text rendering.
REPAIR: Export and use external inpainting tools (Photoshop, Gemini) for post-generation edits.

**FAILURE: --ar exceeding 4:1 with --hd**
WHY: Hard architectural limit. Prompt will error or silently cap.
REPAIR: Keep --ar at or below 4:1 when --hd is present. Standard V8 supports up to 14:1.

## Calibration

**Prompt length:** 40-80 words of text content, excluding parameter block. V8 rewards density, not brevity or verbosity — each sentence should load one distinct directive (subject, lighting, medium, atmosphere). A 30-word prompt is usually underspecified; a 120-word prompt is usually redundant.

**--s calibration table:**
- `--s 50-100`: documentary photography, technical product shots, text-heavy renders
- `--s 100-150`: photorealistic portraits, editorial photography
- `--s 300-400`: concept art, stylized illustration
- `--s 400-600`: 2D art, graphic design, painterly styles
- `--s 700+`: combine with --p only; high personalization pull, unpredictable aesthetics

**--sw for --sref:** Default to 50 in V8 (source material recommends 50 for subtle, 100-400 for increasing override). Default 100 is typically too strong in V8's literal architecture.

**--chaos:** 20-30 for initial ideation grids to force compositional variance. Set to 0 for style refinement and final render passes.

**--style raw:** Default on for photography, technical renders, text-heavy prompts. Omit for art/illustration workflows.

**Aspect ratio:** Decide before generation — cannot change without disrupting V8's spatial composition. Max 4:1 with --hd, up to 14:1 without.

## Operating Environment [EXTEND]

V8's cost/performance tiers change what a valid prompt looks like:

**Standard V8** (`--v 8` only): 4-5x faster than V7. Relax mode available (may throttle at capacity). Max AR 14:1. Use for all exploratory and iterative work.

**V8 + --hd**: 4x cost, 4x slower, native 2K output. Caps AR to 4:1. Disables Relax mode if combined with --q 4. Non-reversible — cannot upscale to HD post-generation. **Prompt requirement:** Only append to prompts you've already validated at standard quality.

**V8 + --q 4**: 4x cost, enhanced micro-detail and multi-subject coherence. No AR restriction alone. **Prompt requirement:** Use for complex multi-subject or high-texture-density scenes.

**V8 + --hd + --q 4**: 16x cost, maximum fidelity. Disables Relax mode entirely. **Prompt requirement:** Final production renders only. Warn user explicitly before recommending.

**V7 fallback** (`--v 7`): Required when prompts need: `--oref` (character/object consistency), `--draft` (fast iteration budget), multi-prompt weights (`::`), Niji 7. In V7, shorten prompts, allow atmospheric ambiguity, and rely on the model's latent aesthetic.

**Web Editor**: Currently runs on V6.1 model for all Vary Region, Pan, and Zoom operations. Avoid for pristine V8 outputs — triggers anatomical and text rendering regression in edited regions.

## CRITICAL — Midjourney V8 Rules

1. ALWAYS write prompts in connected natural language sentences — never comma-separated keyword lists.
2. ALWAYS include an explicit lighting directive (source + angle + quality) in every V8 prompt.
3. ALWAYS batch typography in separate double-quote clusters, max 4 words each, double quotes only.
4. ALWAYS calibrate --s to medium: 50-150 for photography, 300-600 for illustration.
5. NEVER append --oref or --cref to V8 prompts — route character consistency requests to --v 7.
6. NEVER append --draft to V8 prompts — unsupported.
7. NEVER combine --hd + --q 4 on exploratory prompts — finishing tools for confirmed compositions only.
8. NEVER exceed --ar 4:1 when --hd is active.
9. NEVER mix --sref and Moodboard (--p mID) in the same prompt.
10. PREFER --sw 50 as starting point for --sref in V8 (default 100 is typically overpowering).
11. AVOID --sv 6 — use default --sv 7 (free, compatible with --hd and --q 4).
12. REQUIRE explicit medium declaration (lens + film stock OR artistic medium) for every prompt.
