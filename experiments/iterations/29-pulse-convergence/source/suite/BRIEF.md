# Pulse and Convergence: public generation brief

## User request

“Go ahead and make 10 more with the following changes:

- More layers, most of the time. Textures with just one or two voices should be the exception.
- Don't stall out. Keep the music moving and changing.
- it's ok to have a pulse. Don't ram it home or overdo it, but rhythm is ok. many of the previous versions subverted the pulse. Ideally we want a pulse most of the time, but for the rhythms to be subtle and expressive, not robotic
- The piece should always progress through the harmonies in the original sequence throughout the piece. The general harmonic area at any given moment should be a subset of adjacent harmonies in the sequence. For example, in the opening, it could use A, B, C, then in the next section B, C, D, E, F, then in the next F, G, then just hang out on H for a while, then I/J/K/L/M, etc. This is a high-level structural element of the piece. It's ok to go backwards and forwards, and to bundle different combinations at any given time, but over time it should generally move from left to right through the progression, so the piece converges on the golden ratios chord and is basically just that chord for the last third or more of the piece.”

## Public implementation specification

Use the earlier musical methods and saved dry sampled/synth palette, with fresh note material for every piece. No new composition research. Keep sampled acoustic/electric instruments prominent, synths in changing roles, moving instrumental choirs, consonant triad/seventh sequences, counterpoint, hocket, phrasing, dynamics and occasional subsidiary clocks. Keep the main pulse audible through instrumental activity and avoid a click or a drum beat. Small timing offsets, mild common tempo breathing, strong/weak metrical accents, varied articulation and phrase-level dynamics support an expressive 4/4 pulse.

Place each moment inside an explicit contiguous harmonic window. Window bounds advance monotonically through the forty original fields, while the internal chord order may go back and forth. Hear all forty fields. After a specified convergence point, use only original field 39 for the rest of the piece; reserve at least one third of total elapsed time for that final field. Continue compositional motion inside it by changing internal chords, melodic sequences, registers, texture and orchestration.

Build fuller scores with independently articulated inner parts, a soft distributed pulse and several foreground/counterpoint lines. Aim for at least four active notes during more than 85% of the piece and at most two during less than 8%. Make one short thinner episode an exception. Change texture roughly every four bars and always within thirty seconds. Maintain variety without violent tutti attacks. Write distinct dry exits; no master fade.

Structural pitches are exact members of the active original field. Retain the previous permission for rare passing tones only: brief, quieter, monotonic connections between two actual same-part structural notes in one harmonic span, with endpoint IDs recorded and checked. End notes before incompatible harmony changes; do not bend held notes into the next field. No added chord tones or octave-equivalent substitutes. No reverb, delay, chorus, added vibrato, tremolo/gating DSP, click or vocal gimmick.

## Inspectable specification

`compose_flow.py` contains the ten explicit forms, ensembles, seeds, pulse timing, harmonic-window schedules, melodic construction and endings. `pitch_core.py` contains the original-field selection, consonance search, passing-tone checks and independent voice allocation. `suite/scores/NN.json` preserves all actual notes, local harmonic changes, advancing windows, primary beat times, form sections, sequence contours, instrument choices and passing-tone endpoints. `render_flow.py` contains the full sampler and mixing method. This is a public brief and code specification, not a hidden reasoning transcript.
