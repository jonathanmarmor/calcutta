# Generation instructions and provenance

These pieces were composed by writing deterministic Python generators in response to Jonathan Marmor’s evolving instructions. There was no separate text-to-audio model prompt. The operational instructions are the Python sources, constants, seeds, sound states, and saved score JSON.

Each iteration has a `BRIEF.md` that explains the intent. Those files are retrospective reconstructions from the visible requests and implementation, explicitly labeled as such. They are not verbatim assistant prompts or a hidden reasoning transcript. No separately retained original model-prompt files were found. Original explanatory README files, listening guides, source comments, research notes and generated decisions are preserved inside each source snapshot.

For the latest piece, the brief also includes the user’s exact current request. Future iterations should save a public composition brief and structured plan at generation time, before running the composer, then record the seed, dependencies and resulting file hashes. This makes the instructions inspectable without fabricating unavailable history.
