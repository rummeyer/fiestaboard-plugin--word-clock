"""Word Clock plugin for FiestaBoard.

Renders the current time the way a QLOCKTWO-style word clock does — as a
spelled-out phrase in five-minute steps ("ES IST VIERTEL NACH ZEHN",
"IT IS QUARTER PAST TEN") — and lays it out for the board it is rendering
on, so the same plugin fits a Flagship (22x6) and a Note (15x3).

A real word clock lights letters inside a fixed matrix. A split-flap has no
"dim" state, so this plugin renders only the words that would be lit, which
is what the matrix visually reduces to anyway.
"""

import logging
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.plugins.base import PluginBase, PluginResult

logger = logging.getLogger(__name__)

DEFAULT_TIMEZONE = "Europe/Berlin"

# Board geometry assumed when the plugin runs outside a board-scoped render
# (unit tests, the /plugins/{id}/data endpoint). Flagship is the wider of the
# two shapes, so a phrase laid out for it never silently loses words.
FALLBACK_WIDTH = 22
FALLBACK_HEIGHT = 6

# Characters the board can actually flap. Anything outside this set is dropped
# rather than sent as a wrong tile. Reference: src/board_chars.py in FiestaBoard.
BOARD_CHARSET = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 !@#$()-+&=;:'\"%,./?°")

# Umlauts have no board tile. "expand" is the correct German transliteration
# (FÜNF -> FUENF); "strip" is the shorter, more telegraphic form (FUNF).
UMLAUT_EXPAND = {"Ä": "AE", "Ö": "OE", "Ü": "UE", "ß": "SS"}
UMLAUT_STRIP = {"Ä": "A", "Ö": "O", "Ü": "U", "ß": "SS"}

DOT_COLORS = {
    "red": "{63}",
    "orange": "{64}",
    "yellow": "{65}",
    "green": "{66}",
    "blue": "{67}",
    "violet": "{68}",
    "white": "{69}",
}

DE_PREFIX = "ES IST"
EN_PREFIX = "IT IS"

# Hour 1 is "EIN" only when it is immediately followed by UHR ("ES IST EIN UHR"),
# and "EINS" everywhere else ("ES IST FÜNF NACH EINS").
DE_HOURS = {
    1: "EINS",
    2: "ZWEI",
    3: "DREI",
    4: "VIER",
    5: "FÜNF",
    6: "SECHS",
    7: "SIEBEN",
    8: "ACHT",
    9: "NEUN",
    10: "ZEHN",
    11: "ELF",
    12: "ZWÖLF",
}

EN_HOURS = {
    1: "ONE",
    2: "TWO",
    3: "THREE",
    4: "FOUR",
    5: "FIVE",
    6: "SIX",
    7: "SEVEN",
    8: "EIGHT",
    9: "NINE",
    10: "TEN",
    11: "ELEVEN",
    12: "TWELVE",
}

# Phrase templates keyed by the five-minute step. "{h}" is the current hour,
# "{h1}" the next one — German counts toward the coming hour from :25 onward.
DE_STANDARD = {
    0: "{h} UHR",
    5: "FÜNF NACH {h}",
    10: "ZEHN NACH {h}",
    15: "VIERTEL NACH {h}",
    20: "ZWANZIG NACH {h}",
    25: "FÜNF VOR HALB {h1}",
    30: "HALB {h1}",
    35: "FÜNF NACH HALB {h1}",
    40: "ZWANZIG VOR {h1}",
    45: "VIERTEL VOR {h1}",
    50: "ZEHN VOR {h1}",
    55: "FÜNF VOR {h1}",
}

# Ostdeutsch/fränkisch/sächsisch: quarters are counted into the coming hour
# ("VIERTEL ZEHN" = 9:15), and :20/:40 hinge on HALB instead of the full hour.
DE_REGIONAL = {
    **DE_STANDARD,
    15: "VIERTEL {h1}",
    20: "ZEHN VOR HALB {h1}",
    40: "ZEHN NACH HALB {h1}",
    45: "DREIVIERTEL {h1}",
}

EN_STANDARD = {
    0: "{h} O'CLOCK",
    5: "FIVE PAST {h}",
    10: "TEN PAST {h}",
    15: "QUARTER PAST {h}",
    20: "TWENTY PAST {h}",
    25: "TWENTY FIVE PAST {h}",
    30: "HALF PAST {h}",
    35: "TWENTY FIVE TO {h1}",
    40: "TWENTY TO {h1}",
    45: "QUARTER TO {h1}",
    50: "TEN TO {h1}",
    55: "FIVE TO {h1}",
}


def round_to_step(hour: int, minute: int, rounding: str) -> tuple[int, int, int]:
    """Reduce a wall-clock time to a five-minute word-clock step.

    Returns ``(hour, step, leftover)`` where *step* is a multiple of 5 and
    *leftover* is the minutes the words cannot express, which the corner dots
    show. Rounding up past :57 carries into the next hour. Only floor rounding
    has a leftover — with "nearest" the phrase already absorbs the difference.
    """
    if rounding == "nearest":
        step, leftover = ((minute + 2) // 5) * 5, 0
    else:
        step, leftover = (minute // 5) * 5, minute % 5
    if step >= 60:
        step = 0
        hour = (hour + 1) % 24
    return hour, step, leftover


def _template_for(step: int, language: str, german_style: str) -> str:
    """Return the raw phrase template for a five-minute step."""
    if language == "en":
        return EN_STANDARD[step]
    return (DE_REGIONAL if german_style == "regional" else DE_STANDARD)[step]


def spoken_hour(hour: int, step: int, language: str, german_style: str) -> int:
    """Return the 1-12 hour the phrase actually names.

    From :25 onward German counts toward the coming hour ("HALB ZEHN" is 9:30),
    and English switches to "TO" — in both cases the spoken hour is the next one.
    """
    h12 = hour % 12 or 12
    if "{h1}" in _template_for(step, language, german_style):
        return h12 % 12 + 1
    return h12


def build_phrase(hour: int, step: int, language: str, german_style: str) -> str:
    """Spell out ``hour``/``step`` as a word-clock phrase, without the prefix.

    The result still contains umlauts; :func:`to_board_text` converts them.
    """
    h12 = hour % 12 or 12
    next_h12 = h12 % 12 + 1
    template = _template_for(step, language, german_style)
    hours = EN_HOURS if language == "en" else DE_HOURS

    hour_word = hours[h12]
    if language == "de" and h12 == 1 and template.startswith("{h} UHR"):
        # "ES IST EIN UHR", but "ES IST FÜNF NACH EINS".
        hour_word = "EIN"

    return template.format(h=hour_word, h1=hours[next_h12])


def to_board_text(text: str, umlauts: str) -> str:
    """Uppercase *text* and reduce it to characters the board can display."""
    table = UMLAUT_STRIP if umlauts == "strip" else UMLAUT_EXPAND
    text = text.upper()
    for source, replacement in table.items():
        text = text.replace(source, replacement)
    return "".join(char for char in text if char in BOARD_CHARSET)


def wrap_words(text: str, width: int) -> list[str]:
    """Greedily wrap *text* to *width*, never splitting a word.

    A word longer than the board is emitted on its own line rather than
    truncated — the caller decides what to do with an overlong layout.
    """
    lines: list[str] = []
    current = ""
    for word in text.split():
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= width:
            current = f"{current} {word}"
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _align(line: str, width: int, alignment: str) -> list[str]:
    """Return *line* as a list of exactly *width* single-tile tokens."""
    tiles = list(line[:width])
    padding = width - len(tiles)
    if alignment == "center":
        left = padding // 2
        return [" "] * left + tiles + [" "] * (padding - left)
    return tiles + [" "] * padding


def _place_dots(rows: list[list[str]], dots: int, marker: str) -> None:
    """Write *dots* corner markers into the bottom-right of *rows*, in place.

    Skipped when the bottom row has no free tiles — the time itself always
    outranks the dots.
    """
    if dots <= 0 or not rows:
        return
    row = rows[-1]
    # One blank tile of breathing room between the words and the dots.
    if any(tile != " " for tile in row[-(dots + 1) :]):
        return
    row[len(row) - dots :] = [marker] * dots


def layout(
    phrase: str,
    prefix: str,
    width: int,
    height: int,
    alignment: str,
    dots: int = 0,
    dot_marker: str = "",
) -> list[str]:
    """Lay the phrase out as *height* board rows of *width* tiles.

    The prefix ("ES IST"/"IT IS") is the first thing sacrificed when the phrase
    does not fit; if it still overflows, the leading rows are dropped so the
    hour survives.
    """
    text = f"{prefix} {phrase}".strip() if prefix else phrase
    lines = wrap_words(text, width)
    if len(lines) > height and prefix:
        lines = wrap_words(phrase, width)
    if len(lines) > height:
        lines = lines[-height:]

    top = (height - len(lines)) // 2
    rows = [[" "] * width for _ in range(top)]
    rows += [_align(line, width, alignment) for line in lines]
    rows += [[" "] * width for _ in range(height - len(rows))]

    if dot_marker:
        _place_dots(rows, dots, dot_marker)
    return ["".join(row) for row in rows]


class WordClockPlugin(PluginBase):
    """Word clock in German and English, sized to the board it renders on."""

    @property
    def plugin_id(self) -> str:
        return "word_clock"

    def validate_config(self, config: dict[str, Any]) -> list[str]:
        """Reject a timezone the runtime cannot resolve; everything else is enum-bounded."""
        errors: list[str] = []
        timezone = config.get("timezone", DEFAULT_TIMEZONE)
        if not isinstance(timezone, str) or not timezone.strip():
            errors.append(f"Invalid timezone: {timezone!r}")
            return errors
        try:
            ZoneInfo(timezone)
        except (ZoneInfoNotFoundError, ValueError, AttributeError, KeyError):
            errors.append(f"Invalid timezone: {timezone}")
        return errors

    def _now(self) -> datetime:
        """Current time in the configured timezone, falling back to the board's."""
        timezone = self.config.get("timezone")
        if not timezone:
            from src.config import Config

            timezone = Config.GENERAL_TIMEZONE or DEFAULT_TIMEZONE
        return datetime.now(ZoneInfo(timezone))

    def fetch_data(self) -> PluginResult:
        """Build the phrase for the current time and lay it out for this board."""
        try:
            now = self._now()
            language = "en" if self.config.get("language") == "en" else "de"
            umlauts = self.config.get("umlauts", "expand")
            german_style = self.config.get("german_style", "standard")
            alignment = self.config.get("alignment", "center")

            hour, step, leftover = round_to_step(now.hour, now.minute, self.config.get("rounding", "down"))
            phrase = to_board_text(build_phrase(hour, step, language, german_style), umlauts)
            prefix = ""
            if self.config.get("show_prefix", True):
                prefix = EN_PREFIX if language == "en" else DE_PREFIX

            board = self.board
            width = board.width if board else FALLBACK_WIDTH
            height = board.height if board else FALLBACK_HEIGHT

            dot_marker = ""
            if self.config.get("show_minute_dots", False):
                dot_marker = DOT_COLORS.get(self.config.get("dot_color", "white"), DOT_COLORS["white"])

            lines = layout(phrase, prefix, width, height, alignment, leftover, dot_marker)

            full = f"{prefix} {phrase}".strip()
            data: dict[str, Any] = {
                "phrase": full,
                "phrase_short": phrase,
                "prefix": prefix,
                "hour_word": to_board_text(
                    (EN_HOURS if language == "en" else DE_HOURS)[
                        spoken_hour(hour, step, language, german_style)
                    ],
                    umlauts,
                ),
                "time": now.strftime("%H:%M"),
                "step": str(step),
                "minute_offset": str(leftover),
                "minute_dots": dot_marker * leftover,
                "language": language,
                "formatted": full,
            }
            # One variable that fills the whole board: the laid-out rows joined
            # by newlines. FiestaBoard's template engine splits a value on "\n"
            # across board rows, so `{{word_clock.block}}` on the first template
            # line reproduces the centered layout without needing |wrap.
            data["block"] = "\n".join(lines)
            # line1..line6 mirror the same rows individually. They keep their
            # full board width on purpose: the engine's alignment pads *around*
            # whatever it is given, so an rstripped row would be indented twice
            # on a centered line. A full-width row passes through untouched.
            for index in range(FALLBACK_HEIGHT):
                data[f"line{index + 1}"] = lines[index] if index < len(lines) else ""

            return PluginResult(available=True, data=data, formatted_lines=lines)

        except Exception as error:  # noqa: BLE001 — a broken clock must not break the render loop
            logger.exception("Error building word clock")
            return PluginResult(available=False, error=str(error))

    def get_formatted_display(self) -> list[str] | None:
        """Return the laid-out board rows for the "single plugin" page type."""
        result = self.fetch_data()
        if not result.available:
            return None
        return result.formatted_lines


# Export the plugin class
Plugin = WordClockPlugin
