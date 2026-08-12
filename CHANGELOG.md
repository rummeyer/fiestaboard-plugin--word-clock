# Changelog

All notable changes to this plugin are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The version here is the source of truth for `manifest.json` — a test fails if
the two drift apart.

## [Unreleased]

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

[Unreleased]: https://github.com/rummeyer/fiestaboard-plugin--word-clock/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/rummeyer/fiestaboard-plugin--word-clock/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/rummeyer/fiestaboard-plugin--word-clock/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/rummeyer/fiestaboard-plugin--word-clock/releases/tag/v1.0.0
