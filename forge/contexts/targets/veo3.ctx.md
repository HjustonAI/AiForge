<!-- @meta
  name: veo3
  tags: [veo3, veo, video, google, video-gen, generative, audio]
  priority: 6
  category: generative
-->

## Mental Model

Veo3 is not a semantic vibe machine — it is a 3D latent diffusion engine that processes video and audio latents jointly in a single denoising pass. Each spatial region of the frame has its own attention vector that actively searches the prompt for geometric, textural, and temporal guidance. If a region finds no specific instruction, it collapses to the statistical mean of training data: the "plastic" smoothness that marks amateur AI video.

The mental model for a prompt architect: you are writing a technical brief for a virtual production engine, not describing a scene to a human. The model treats early tokens as immutable spatial coordinates. Later tokens modulate behavior within those established boundaries. Structure is not optional — deviating from the correct component order forces the transformer to retroactively rewire already-calculated spacetime patches, causing temporal hallucinations, prompt dropping, or identity drift.

Audio is not post-processing. Veo3 compresses audio and video into a shared latent space and denoises them together, meaning dialogue, sound effects, and ambience must be explicitly routed using syntactic triggers — not described in natural language.

## Prompt Architecture [OVERRIDE]

Strict component sequence — deviating from this order increases failure probability:

1. **CAMERA** — Shot framing, focal length, camera movement using professional terminology (e.g., "locked-off medium close-up, 35mm lens, slow lateral dolly right"). Establishes spatial bounding box before anything else.
2. **SUBJECT** — Precise demographic, sartorial, anatomical descriptors. Generic descriptions trigger demographic drift toward training mean. Specify exact age, skin texture, clothing material, resting expression.
3. **ACTION** — Specific biomechanical movement, not emotional state. "Points right with a swift biomechanical gesture" not "gestures emotionally."
4. **CONTEXT** — Background environment, temporal lighting, atmospheric conditions.
5. **STYLE** — Aesthetic, film stock, color grade, director/cinematographer references. Placed after physical elements so it acts as a filter, not a geometry generator.
6. **AUDIO** — Dialogue uses mandatory colon+quotes syntax: `[Character] [action verb] and says: "exact text."` Environmental audio uses prefix tags: `SFX: [event]` for synchronized effects, `Ambient: [soundscape]` for continuous room tone.
7. **NEGATIVES** — All exclusions at end only. Use `avoid [X]` exclusively — never `no` or `don't` mid-prompt.

**Multi-shot:** Bracket each shot with timestamp syntax `[00:00-00:02]`. Use `[cut]`, `match-on-action`, or `cross-dissolve` as editing directives between shots. Pin wardrobe and prop positions explicitly across cuts.

**Compressed example:**
`Locked-off medium close-up, 35mm lens, shallow depth of field. Seasoned 72-year-old male, deeply lined face, black technical hoodie, silver chain. He looks directly at lens, points right with a swift biomechanical gesture. Dimly lit urban alleyway, flickering neon out of focus. Film noir, chiaroscuro lighting, heavy film grain, teal-orange grade. Ambient: distant sirens and rain. He looks at camera and says: "The city always has a story." Avoid slow motion, avoid daylight, avoid camera tracking.`

## Leverage Points

**Native 48kHz audio sync:** Veo3 denoises audio and video latents together — temporal synchronization is architectural, not layered. Trigger dialogue with mandatory syntax: `[Character] [action] and says: "[text]."` Omit the colon or quotes and the token misroutes to the visual latent pathway, rendering text as subtitle artifacts or silence. Layer audio using `SFX: [specific event]` and `Ambient: [soundscape]`.

**Character Sheet (Ingredients to Video):** Upload 3-4 reference images (front portrait, profile, full-body) as `reference_images` in the API payload to lock identity across shots. This is the only reliable mitigation for identity drift — text-only identity anchoring degrades at camera angles beyond 45°.

**First+Last Frame Control (Motion-Lock):** Provide start and end reference frames with ≥60% shared background pixels. The model dedicates compute exclusively to interpolating biomechanical movement within a static environment, eliminating physics hallucinations on critical transitions.

**Professional cinematography vocabulary:** Veo3 parses film production terminology literally — `smooth 180-degree arc shot`, `slow lateral dolly right`, `overhead tracking shot`, `35mm lens`, `shallow depth of field`. These bypass default pacing and route directly to camera vector calculation.

**Scene extension via delta prompts:** Native generation is 4-8s per block. Extend to 60s (or 148s via API stitching) using delta-only prompts — describe only what changes (new motion, new audio). Redescribing the existing scene forces full audio-visual realignment and breaks lip-sync continuity.

**Lighting precision:** Veo3 outperforms competitors in global illumination and shadow tracking. Trigger with architectural language: `soft golden rim light outlines silhouette`, `venetian blind light patterns`, `natural backlight`, `chiaroscuro`.

## Failure Modes & Repair

**FAILURE: Identity drift at camera angles >45°**
WHY: Cross-frame attention loses spatial anchors during wide angle shifts; model falls back to demographic training mean, documented bias toward lighter skin tones on dropout.
REPAIR: Use Character Sheet (3-4 reference views via `reference_images`). Add targeted negatives at prompt end: `avoid different hair color`, `avoid changing facial structure`. Pin wardrobe per shot: `scarf remains visible on neck`.

**FAILURE: Dialogue hallucination (subtitle artifacts or silence)**
WHY: Without colon+quotes syntax, dialogue tokens route to the visual latent pathway — the model renders text geometrically, producing corrupted subtitle artifacts or ignores it.
REPAIR: Mandatory format only: `The woman looks at camera and says: "We have to leave now."` No descriptive dialogue tags. No alternatives to colon+quotes.

**FAILURE: Physics violations (abrupt halts, object pass-through)**
WHY: Veo3 predicts probable pixel arrangements from 2D training data — no physics engine, no momentum conservation. Documented weakness: explosive physics, fluid dynamics, sequential force transfer.
REPAIR: Avoid unconstrained collision prompts. Use First+Last Frame Control with ≥60% background overlap for critical movements. Anchor interactions with biomechanical descriptors, not outcome descriptions.

**FAILURE: "Plastic" aesthetic (AI-smooth output)**
WHY: Model biased toward high-quality, noise-free training data when prompts lack specific optical constraints. Default output is cinematically perfect but visually synthetic.
REPAIR: Inject analog hardware limitations: `heavy film grain`, `fog layer`, `bokeh halo`, `water droplets on lens`. Forces the model to calculate light refraction and particulate matter.

**FAILURE: Safety filter rejection or premature termination**
WHY: Vertex AI runs aggressive real-time classifiers in parallel. Sensitive to specific vocabulary even in benign prompts. Also triggers on topics with insufficient training coverage.
REPAIR: Sanitize forbidden vocabulary. Push all negative constraints to absolute end. Run split-step verification for complex or edge-case prompts before full generation.

**FAILURE: Audio desync on scene extension**
WHY: Redescribing an existing scene during extension forces the transformer to recalculate audio-visual alignment from scratch, disrupting temporal audio latent continuity.
REPAIR: Delta-only extension prompts. Describe only the new motion and new audio required for that segment. Silence on existing elements lets memory banks maintain continuity.

## Calibration

**Length:** 50-150 words per generation block. Beyond this, cross-attention overloads and trailing constraints drop. Multi-shot sequences use timestamp brackets per shot rather than longer prose.

**Style anchors:** Named directors and cinematographers parse reliably — Wes Anderson (symmetrical framing), documentary handheld, film noir chiaroscuro, Kurosawa dramatic composition. Film stocks work: `Kodak 5219`, `Fuji Velvia`, `heavy 16mm grain`, `Zack D Films aesthetic`.

**Quality boosters:** `35mm lens`, `macro photography`, `commercial production style`, `shallow depth of field`, `natural backlight`, `chiaroscuro lighting`.

**Technical parameters:** 720p / 1080p / 4K native; 16:9 and 9:16 (no post-crop needed); 4-8s base generation block.

**Vocabulary to avoid:** Subjective vague modifiers — `cinematic`, `epic`, `beautiful`, `stunning`, `amazing` — push output to training average. Use `avoid` only for negatives, never `no` or `don't`. For image-to-video: never redescribe static elements already visible in reference image — describe motion delta only.

## Operating Environment [EXTEND]

**Vertex AI API (production / enterprise):** JSON payload to model endpoints (`veo-3.1-generate-001`, `veo-3.1-fast-generate-001`). Supports `reference_images` parameter (base64 or GCS URI). Metered: $0.40/s at 1080p, $0.60/s at 4K. Full architectural fidelity — prompts reach the model unmodified. Batch processing reduces effective cost 70-90% for repetitive workflows. Use for precise architectural prompting, benchmarking, multi-shot batch production.

**Google Flow / VideoFX (creative / iterative):** UI-driven filmmaking environment. Use Scene Builder for shot-by-shot generation and native timeline stitching rather than complex multi-shot text prompts. Supports post-generation Insert/Remove (add/remove objects with auto-relit global illumination). Subscription-based (~$19.99/mo AI Pro). Cost-effective for high-iteration, prompt-refinement workflows.

**Gemini App (consumer — avoid for architecture work):** Applies system-level prompt abstraction and rewriting before reaching Veo3. Precise lens specs, temporal brackets, and negative constraints are sanitized or overwritten by Gemini's internal instructions. Never benchmark or run architectural prompts here.

## CRITICAL — Veo3 Rules

1. ALWAYS sequence components: Camera → Subject → Action → Context → Style → Audio → Negatives. Order is structural, not stylistic preference.
2. ALWAYS trigger dialogue with strict syntax: `[Character] [action] and says: "[text]."` Colon and quotes are hard routing tokens — not optional.
3. ALWAYS use `SFX:` and `Ambient:` prefix tags for non-dialogue audio layers.
4. ALWAYS place all negative constraints at the end using `avoid` — never `no` or `don't` in mid-prompt position.
5. ALWAYS use Character Sheet (3-4 reference views as `reference_images`) for any multi-shot sequence where identity consistency matters.
6. ALWAYS bracket multi-shot segments: `[HH:MM-HH:MM]` per shot + editing directive (`[cut]`, `match-on-action`) between shots.
7. ALWAYS write delta-only prompts for scene extension — never redescribe existing scene elements.
8. REQUIRE ≥60% shared background pixels between start/end frames when using First+Last Frame Control.
9. NEVER use vague aesthetic modifiers: `cinematic`, `epic`, `beautiful`, `stunning` — replace with specific optical and textural descriptors.
10. NEVER run precise architectural prompts in the Gemini consumer app — use Vertex AI or Flow for all production and benchmarking work.
11. PREFER biomechanical descriptors in Action component — physical mechanics, not emotional states.
12. INCLUDE analog imperfection vocabulary when realism is the goal: `heavy film grain`, `lens distortion`, `fog layer`, `water droplets on lens`.
