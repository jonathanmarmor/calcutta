# Calcutta: Other Doors

**Twelve new pieces · 60:00 including gaps · 59:38 of music**

An uneven album: three works around ten minutes, medium-length inventions, and miniatures down to 41 seconds. Different pieces have different generating engines and formal trajectories, rather than the same accompaniment underneath new presets. The dry, immediate, vibrato-free sound and the original Calcutta pitch fields remain the common ground.

The twelve individual listening files are linked below. A separate continuous 60-minute album with chapter metadata is delivered alongside this archive; duplicate album audio is omitted from Git.

| Album start | Track | Duration | What to listen for |
|---|---|---|---|
| 0:00 | [01. The Small Door](audio/01_the_small_door.mp3) | 0:52 | A quick succession of chamber apertures; a miniature journey rather than an overture. |
| 0:54 | [02. Reed Exchange](audio/02_reed_exchange.mp3) | 3:53 | Unequal answering choirs, long wind lines, keyboard interruptions and changing protagonists. |
| 4:49 | [03. Fifths Under Glass](audio/03_fifths_under_glass.mp3) | 6:58 | Walks through a graph of overlapping triads and sevenths; the same route changes register and color. |
| 11:49 | [04. A Very Short Parade](audio/04_a_very_short_parade.mp3) | 1:21 | Construction-tree endpoints become a moving instrumental genealogy, folding and unfolding. |
| 13:12 | [05. Three Unequal Rivers](audio/05_three_unequal_rivers.mp3) | 9:35 | Three phrase clocks with changing rational relationships; broad currents and fast tributaries. |
| 22:49 | [06. The Switches Are Singing](audio/06_the_switches_are_singing.mp3) | 3:15 | The sole amplitude-gate study: hard interlocks, ungated islands, variable duties and composite colors. |
| 26:06 | [07. One Window Left Open](audio/07_one_window_left_open.mp3) | 0:41 | An intimate near-still miniature entirely within the destination field; a deliberate exception to the full journey. |
| 26:49 | [08. Orchard of Circuits](audio/08_orchard_of_circuits.mp3) | 6:10 | A cue-driven instrumental network: phrase endings hand energy, register and contour to another player. |
| 33:01 | [09. Thirty-Two Small Clocks](audio/09_thirty-two_small_clocks.mp3) | 2:09 | Endpoint identities persist while unequal rhythmic clocks activate different branches of the construction. |
| 35:12 | [10. Rooms in a Long House](audio/10_rooms_in_a_long_house.mp3) | 10:48 | An episodic large form with returning rooms transformed by changing harmony, ensemble and temporal scale. |
| 46:02 | [11. The Stair Remembers](audio/11_the_stair_remembers.mp3) | 2:56 | Audible ascending and descending sequences through consonant chord subsets, with restrained mutations. |
| 49:00 | [12. An Unfinished Atlas](audio/12_an_unfinished_atlas.mp3) | 11:00 | A large additive/subtractive form: accumulate, clear, change direction, relocate, interrupt; a dry open-ended exit. |

## What changes from piece to piece

**Three Unequal Rivers**, **Rooms in a Long House**, and **An Unfinished Atlas** carry the large forms. The first repeatedly changes the relationships between three phrase clocks, with slower and faster material moving together. The second returns to contrasting rooms—dialogue, graph-based harmony, quiet chamber music, cue relays and moving registers—in changed harmonic surroundings. The last builds and subtracts layers, relocates registers, clears space and interrupts its own momentum. Shorter tracks provide different kinds of contrast rather than compressed copies of those forms.

**Fifths Under Glass** treats the internal triads and sevenths as a graph: shared pitches and voice-leading cost influence which subset follows which. **Orchard of Circuits** uses a queue of phrase cues: one player's cell schedules a transformed response from another player, so the network generates later entries. **A Very Short Parade** and **Thirty-Two Small Clocks** work directly with the original construction-tree endpoint identities. **The Stair Remembers** foregrounds recognizable rising/falling chord sequences.

**The Switches Are Singing** is the only track with amplitude-gate DSP. Sustained layers use different rates, phases and duties, with ungated islands and melodies. All other tracks omit gates and tremolo. The 41-second **One Window Left Open** is an intimate, near-still destination-field miniature—a deliberate exception to both the fuller textures and the full harmonic journey.

Every piece changes its substantial texture or ensemble within 25 seconds. Density and speed vary inside works: long outer melodies can sit over fast inner parts, independent clocks can become coordinated dialogue, and dense ensembles can open into chamber passages. These are written event/ensemble changes; the timing limit is not a claim about subjective surprise.

## Sound and tuning

All 97 inherited source models are heard across the album. Individual tracks use 11–90 actual sounds, with different inventories and changing ensembles; related presets count as distinct sounds, not distinct instrument families. Reed/keyboard colors are foregrounded in the second track, while acoustic, electric and synthetic colors share the larger works. Instrumentation counts and note-level assignments are in the scores and validation report.

These are the fixed-frequency, sample-derived resynthesized colors developed in Wide Palette and Prism Switchyard, not newly installed plugins or untouched acoustic samples. Attack/body spectra, short spectral settling, modeled pluck decay and faint stationary breath noise provide instrumental distinctions while discarding source pitch modulation. GeneralUser GS source provenance and license are included; eight earlier analog/FM colors remain available. There is no vibrato, added chorus/detune, reverb, delay, click or master ending fade. Notes have prompt entrances and short click-prevention releases. Individual dry endings replace a shared fade or loud final cadence.

Eleven tracks traverse all forty original harmonies through advancing contiguous neighborhoods, start on 2:3, and spend the last 40% entirely in the final golden-ratio field. Track 7 stays in that final field throughout. Early 1:2 visits are brief and occur after the opening. Every written note is an exact field member: no passing tones were needed on this album, and no octave substitutes or held-note retuning are used. Instruments move among actual field pitches. The harmonic/inharmonic partials of a timbre are distinct from the written MIDI pitches.

## Reproduce and inspect

Unpack the source ZIP, install FFmpeg and the pinned requirements, then run:

```sh
python compose_doors.py
python render_album.py
python validate_doors.py
python export_doors.py
python check_regeneration.py
python package_doors.py
```

The 97 compact saved models suffice for rendering; external banks and native plugins are not required. `suite/BRIEF.md` preserves the original request and public composition specification. The twelve scores record notes, construction identities, phrase sequences, relay cues, changing ensembles, beat grids, harmonic windows and gate parameters. The renderer and model provenance make the timbral process inspectable. Public instructions and decisions are included, not hidden reasoning.

MIDI uses independent bend lanes/ports and actual primary tempo maps. It supplies source program hints, but does not encode the resynthesized timbres or amplitude gates. The supplied renderer is authoritative for those sounds. Source audio is 24 kHz stereo, encoded to 48 kHz / 256 kbps MP3. The continuous album is encoded from concatenated PCM, with eleven two-second gaps and twelve chapter markers.

Validation checks exact pitches and harmonic boundaries, advancing windows, final-field residence, independent monophonic MIDI lanes, gate confinement, complete WAV bytes, output peaks, MP3 duration and positive audio energy from every scored instrument. All twelve scores regenerate identically; a representative gated note also rerenders identically. Render and occupancy metrics describe the actual files and score, not subjective musical quality.
