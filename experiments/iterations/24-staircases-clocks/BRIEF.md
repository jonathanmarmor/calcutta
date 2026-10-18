# Staircases and Clocks: composition brief

**Provenance:** retrospective reconstruction from user requests and saved implementation; not an original model transcript.

Louder average level with soft attacks; more acoustic/electric colors and prominent solos; chord-stack sequences, simultaneous clocks, no fade.

The saved Python source is the operational generation instruction; JSON records the decisions it produced. No separate free-standing internal model prompt file was retained. This brief was assembled during archival and is not presented as a verbatim historical prompt.

## Original user request (verbatim)

> - Use that gentler dynamic ceiling to make the whole thing a little louder
> - bring in more sounds that sound like acoustic instruments to blend with the synths. Electric guitars, Rhodes, Clavinet too.
> - get into those fifths and triads and sevenths even more. Make sequences that ascend and descend through that stack of chords.
> - don’t fade at the end. Come up with better endings. Awkward and unexpected can be your friend when ending music.
> - do even more of the multi tempo stuff. Rubato is good, but a little less, and more of multi tempo in this version
> - in addition to the new blends of instruments, be sure to also keep and expose individual instruments. And have some individual instruments that are prominent. Variety is a goal.

## Public implementation plan, recorded during this iteration

Seed 2026101757. Thirteen scenes / 500 seconds. Twelve two-layer exact-unison blends and eight unblended solo parts. Search the actual original fields for approximately 434-cent thirds and 702-cent fifths; attach available seventh extensions. Sequence stable degree contours through root-ordered chord stacks; alter the last note every fourth repeat. Three accompanying lines run at independent fixed local rates. Keep conductor drift below one BPM. Expose full field inventories as quiet staggered notes. Leave a breath after the final ensemble cutoff, then an unresolved two-note Clavinet question. Keep the final master level fixed rather than applying a fade. Aim for higher average loudness without restoring hard tutti attacks.

This is a public design summary, not a hidden reasoning transcript. The exact operational details are in `source/calcutta/interleave_piece.py` and `source/calcutta_interleave/render.py`.

## Attack revision, requested before delivery

The user found the previous Murmur version too consistently slow to speak. In this revision, foreground sequences and exposed acoustic replies use 8 ms outer smoothing, clock lines use 12 ms, inventory notes use 14 ms, and the final Clavinet uses 6 ms. A small number of sustained background-frame notes retain 280 ms entrances. TAL-NoiseMaker’s native amplitude attack is shortened in the renderer too. Instrument sample attacks otherwise retain their natural character. Loudness and orchestration, rather than a slow blanket envelope, keep the mix gentle.
