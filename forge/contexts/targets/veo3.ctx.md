<!-- @meta
  name: veo3
  tags: [veo3, veo, video, google, video-gen]
  priority: 7
-->

## The Veo3 Landscape

Google Veo3 generates video from text prompts. It excels at cinematic quality, smooth camera movements, coherent temporal sequences, and atmospheric lighting. It understands film language — shots, camera angles, pacing, transitions.

Veo3 thinks in SCENES, not frames. Your prompt should describe a MOMENT UNFOLDING IN TIME — what's happening, how the camera observes it, what the light does, how the mood shifts.

## Prompt Structure for Veo3 [OVERRIDE]

The optimal Veo3 prompt follows this architecture:

**Opening: Shot type + atmosphere** — set the stage immediately.
"Cinematic wide shot, golden hour" or "Macro lens, morning mist" or "Drone aerial, twilight blue"

**Subject: Who/what + specific details** — make it real.
Not "a woman" but "a woman in her 60s with silver-streaked hair and weathered hands, wearing an indigo linen dress"

**Action: What happens in time** — Veo3 needs temporal flow.
"She slowly opens an ancient leather-bound book, dust particles catching the light as pages turn"

**Camera: Movement and behavior** — this is Veo3's superpower.
"Slow dolly forward", "Gentle orbit around subject", "Handheld slight shake", "Crane rising", "Steady tracking shot"

**Atmosphere: Light + color + mood** — make it feel like a film.
"Warm amber light streaming through dusty windows, bokeh highlights dancing in the background, muted earth tones with pops of deep gold"

## Known Strengths

- Smooth, cinematic camera movements (dolly, crane, orbit, tracking)
- Atmospheric lighting (golden hour, neon, candlelight, moonlight)
- Natural textures (water, fabric, skin, foliage, smoke, dust)
- Slow-motion sequences with preserved detail
- Coherent multi-second temporal sequences
- Film-grain and vintage aesthetics

## Known Limitations

- Complex multi-character interactions can break coherence
- Text/writing in scene often distorted
- Very fast action sequences may blur
- Extreme close-ups of faces can hit uncanny valley
- Precise hand/finger positioning unreliable
- Avoid asking for specific readable text on objects

## Optimal Length

Veo3 prompts work best at **60-150 words**. Under 40 words gives the model too much freedom (random results). Over 200 words causes instruction dilution — the model "forgets" early details.

Sweet spot: **80-120 words** for a single scene.

## Style Anchoring That Works

Veo3 responds well to cinematic references:
- Director styles: "Wes Anderson symmetry", "Denis Villeneuve atmosphere", "Terrence Malick golden hour"
- Film references: "Blade Runner 2049 color palette", "Interstellar scale", "Her (2013) intimacy"
- Camera operators: "Roger Deakins lighting", "Emmanuel Lubezki natural light"
- Photography: "National Geographic documentary style", "Annie Leibovitz portraiture"

## CRITICAL — Veo3 Rules

These override general rules for Veo3 specifically:

1. ALWAYS describe camera movement — this is what makes Veo3 output cinematic vs generic. No prompt without a camera direction.
2. ALWAYS include lighting description — Veo3's atmospheric rendering is its strongest feature.
3. PREFER slow, deliberate pacing — Veo3 handles slow-motion and gradual reveals beautifully.
4. INCLUDE at least ONE sensory texture detail — dust particles, water droplets, fabric folds, smoke wisps.
5. FRONT-LOAD the shot type and atmosphere — Veo3 weighs the beginning of prompts most heavily.
6. KEEP to one continuous scene — don't describe cuts or transitions within a single prompt.
