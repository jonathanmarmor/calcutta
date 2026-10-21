# Wide Palette: public generation brief

User request: “Make 5 more:
- let's use a much broader instrument set. At least triple the number of instruments in each piece. Use different instrumentation in each piece. use different instrumentation for different sections of each piece.
- Let's bring back our earlier prohibition on vibrato. Look up the sound textures we defined earlier and use that as guidance.
- Don't start the piece with the 1:2 harmony.”

Earlier guidance recovered: dry, immediate attacks; steady sustained tones; immediate gates; no vibrato, chorus, detuned doubles, reverb or delay. Earlier individual colors included open ladder-filter saw, resonant sequencer, Oberheim pulse/brass, TAL hollow/rubber reed, and FM glass/organ. Acoustic/electric instruments included sampled guitars, Rhodes, Clavinet, piano, harp, winds, fretless bass, mallets and sitar. Blended timbres used quieter synthetic layers inside an acoustic color, while exposed individual instruments remained important. These were researched/informed software configurations, not authenticated artist presets. No new compositional research was performed.

Implementation: 64 distinct source presets per piece, compared with 14–16 in the preceding set. Five different pools are drawn from 97 available sources. Assign a different ensemble each four-bar scene, and feature two scheduled sounds in each scene so the full pool is actually used rather than merely declared. Retain the full texture, expressive primary pulse and forward progression through adjacent harmonic windows, spending the last third or more in the final field. Generate fresh cells and section orders. Open on the 2:3 or 3:5 field, never 1:2. Retain rare strictly functional passing tones, no extra sustained pitches and no mid-note retuning.

Vibrato policy: discard the source's pitch-modulation trajectory and use fixed-frequency carriers with sample-derived attack/body spectra. All partial ratios are constant during a note. Allow stable inharmonic partials for struck metals; exclude detuned double oscillators and periodic pitch/amplitude modulation. Use fast noncyclic settling, stationary breath noise where appropriate and modeled pluck decay. These are sample-derived resynthesized instruments, not untouched sample recordings. Preserve musical immediacy and dry eight-millisecond release gates.

The public operational specification is compose_wide.py, flow_base.py, pitch_core.py, build_models.py, render_wide.py, validate_wide.py and the actual scores/model coefficients. This brief records user instructions and design choices, not a hidden reasoning transcript.
