# Changelog

All notable changes to this plugin are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The version here is the source of truth for `manifest.json` — a test fails if
the two drift apart.

## [Unreleased]

## [1.4.0] — 2026-08-12

### Changed

- **The timezone default is now empty**, meaning "follow the FiestaBoard-wide
  timezone" — the fallback the code already implemented. It used to ship as
  `Europe/Berlin`, so a fresh install anywhere else showed the wrong hour until
  the field was changed by hand.
- The last-resort timezone, used only when FiestaBoard has no timezone either,
  moved from `Europe/Berlin` to `UTC`.

### Fixed

- `validate_config` rejected an empty timezone, which as of this release is the
  shipped default — a plugin nobody had touched would have failed its own
  validation. Empty and whitespace now pass; a non-string still does not.

## [1.3.0] — 2026-08-12

### Changed

- **The default language is now English.** A fresh install used to render in
  German, which no longer matched an English README or an English plugin card.
  Existing boards are unaffected — they already have a language stored.
- An unrecognised `language` value falls back to that same default rather than
  to German.

### Documentation

- All illustrations now show English wording, with one showcase board per
  other language. `board-english.png` is gone; `board-german.png` takes its
  place in the showcase row.
- The manifest `teaser` and `previews` — the boards fiestaboard.app renders on
  the plugin card — are English too, as are the variable examples shown in the
  template editor.
- Dropped the trailing blank lines from the `{{word_clock.block}}` examples;
  the surrounding prose already says to leave the remaining lines empty.
- Sample page for the minute dots in the README, rendered from real plugin
  output rather than written by hand.
- Corrected the minute-dot example in `docs/SETUP.md`: 10:33 floors to the
  half-hour step and reads `ES IST HALB ELF`, not `ES IST FUENF NACH HALB ELF`.
- Re-rendered `board-minute-dots.png`, which showed 10:35 with three dots — a
  state that cannot occur, since :35 is exactly on a five-minute step.

## [1.2.0] — 2026-08-12

### Added

- Spanish and French, alongside German and English.
  - Spanish agrees the opener with the hour the phrase *names*, not the hour on
    the clock: 12:40 reads `ES LA UNA MENOS VEINTE`, singular.
  - French carries the unit with the hour (`UNE HEURE` / `DEUX HEURES`) and
    replaces the twelves outright — `MIDI` and `MINUIT`, never "douze heures".
- `board-spanish.png` and `board-french.png` screenshots.

### Changed

- The hour placeholder in a phrase template now expands to a full hour phrase
  rather than a bare numeral, because Spanish and French name the hour first
  and hang the minutes off it.
- The opener is computed per render instead of being a per-language constant,
  which is what Spanish agreement requires.
- An unrecognised `language` value falls back to German instead of being
  treated as English.

### Notes

French is the longest wording at 37 characters
(`IL EST QUATRE HEURES MOINS VINGT-CINQ`) and still fits a Note's 15×3.

## [1.1.0] — 2026-08-12

### Added

- `block` variable: the whole laid-out board as one newline-separated value.
  FiestaBoard splits such a value across board rows, so putting it on the first
  template line reproduces the centered layout. `{{word_clock.phrase}}` on a
  plain line is a single string and gets cut off at the board edge.

### Fixed

- `line1`…`line6` were right-trimmed, which rendered wrong on a centered line:
  the template engine pads *around* what it is given, so a short row was
  indented twice. The rows now keep their full board width.

### Changed

- Category moved from `art` to `utility`.

## [1.0.0] — 2026-08-12

### Added

- Initial release: a QLOCKTWO-style word clock in German and English.
- Board-adaptive layout — every phrase fits a Note (15×3) as well as a
  Flagship (22×6), verified exhaustively across all hours and steps.
- Standard German (`VIERTEL NACH ZEHN`) and the regional East German,
  Franconian and Saxon counting (`VIERTEL ELF`, `DREIVIERTEL ELF`).
- `EIN UHR` vs. `FUENF NACH EINS` — the German hour keeps its `S` everywhere
  except before `UHR`.
- Umlaut handling for a character set that has none: `FUENF`/`ZWOELF` or
  `FUNF`/`ZWOLF`.
- QLOCKTWO-style minute dots as colored tiles, skipped when the bottom row
  is full.
- `live_data`, so the board never shows a cached time.

[Unreleased]: https://github.com/rummeyer/fiestaboard-plugin--word-clock/compare/v1.4.0...HEAD
[1.4.0]: https://github.com/rummeyer/fiestaboard-plugin--word-clock/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/rummeyer/fiestaboard-plugin--word-clock/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/rummeyer/fiestaboard-plugin--word-clock/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/rummeyer/fiestaboard-plugin--word-clock/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/rummeyer/fiestaboard-plugin--word-clock/releases/tag/v1.0.0
