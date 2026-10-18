# Synth research for Calcutta: Obsessions

## What the evidence supports

**Stevie Wonder:** TONTO is the most useful reference here: a Moog modular system expanded with Oberheim SEMs, ARP 2600s, and other modules. That is a better starting point than assigning every early Wonder bass or lead to a Minimoog. Malcolm Cecil's [NAMM oral history](https://www.namm.org/library/oral-history/malcolm-cecil) documents TONTO's components; [Pitchfork's historical overview](https://pitchfork.com/features/overtones/stevie-wonder-and-his-dream-machines-synth/) connects the system to Wonder and discusses the ARP 2600 and Yamaha GX-1. Exact track/preset attribution remains a separate question.

**Early Ozric Tentacles:** Ed Wynne directly identifies the Sequential Circuits Pro-One as his first synth and an important source of the band's swoops, bubbles, and leads in this [2020 interview](https://echoesanddust.com/2020/10/ed-wynne-of-ozric-tentacles/).

**1990s detail:** The [August 1996 Sound On Sound interview](https://www.soundonsound.com/people/ed-wynne-ozric-tentacles-five-go-mad-somerset) discusses the Roland D-50, Korg Wavestation, Waldorf Wave, BassStation, Prophecy, and Pro-Ones. Its relevant passages are reproduced in a [2014 forum discussion](https://www.supportimusicali.it/forum/view/8/0/71556/916/tastiere_altro_setup). The interview describes Waldorf Wave material on *Arborescence*, Pro-One sequencer patterns and effects, and Prophecy replacing the Pro-One for live effects. The original site blocked a full fetch during this research; the forum reproduction and indexed original were checked, alongside Wynne's direct 2020 confirmation of the Pro-One. A separate [Gearspace thread](https://gearspace.com/threads/ozric-tentacles-synth-sound.674039/) contains fan discussion of D-50/Supernova sounds, but its full page was blocked. Forum-era gear lists mix different decades and are not reliable album-by-album credits.

## Actual software models worth distinguishing

| Hardware family | Software | Status in this recording |
|---|---|---|
| Oberheim OB-X | [OB-Xf](https://github.com/surge-synthesizer/OB-Xf) | Used: three new dry patches. An Oberheim-family model, not a recreation of TONTO's SEM modules. |
| Moog-style ladder filtering | [Surge XT](https://surge-synthesizer.github.io/manual-xt/index.html) | Used: new vintage-ladder bass and diode-ladder lead. These are inspired patches, not complete hardware emulations. |
| Sequential Pro-One | [u-he Repro-1](https://u-he.com/products/repro/) | Researched; not used or purchased. The most direct match to the early Ozrics Pro-One evidence. |
| ARP 2600 | [Arturia ARP2600 V](https://www.arturia.com/products/software-instruments/arp2600v/overview) | Researched; not used or purchased. |
| Moog modular | [Arturia Modular V](https://www.arturia.com/products/software-instruments/modular-v/overview) | Researched; not used or purchased. |
| Roland D-50 | [Roland Cloud D-50](https://www.roland.com/global/products/rc_d-50/) | Researched; not used. |
| Korg Wavestation / Prophecy | [Korg Collection](https://www.korg.com/us/products/software/korg_collection/) | Researched; not used. |

## What is actually audible

The recording adds OB-Xf, whose developer identifies it as an OB-X-inspired continuation of OB-Xd, plus newly programmed Surge patches. It also uses GeneralUser GS fretless-bass and sitar samples. The latter is a buzzy **sitar color**, not a physical model of a Coral electric sitar. The previous acoustic/keyboard colors and mobile choirs remain available.

The new OB-Xf sounds use a single oscillator, no unison, zero slop, no LFO modulation, and sustained envelopes. Their tuning was checked at A=440 before rendering. Surge effects are bypassed. There is no delay, reverb, chorus, click track, or intentionally added vibrato. Releases are cropped and smoothed inside each note's gate.
