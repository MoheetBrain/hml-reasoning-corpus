"""Scalar conventions shared by the non-HML arms.

Every arm must be **losslessly readable**, which constrains how a proposition may be
written. The rule is the one the frozen HML view already uses: a value that could be
confused with syntax is written as a JSON literal, and a value that cannot is written
literally so the mathematics stays visible.

Two properties are relied on downstream:

* ``read(write(x)) == x`` for every string the corpus contains, checked by the parity gate
  over every item rather than asserted here;
* the literal form is chosen whenever it is safe, so the glyphs a model was pretrained on
  (``U+22A2``, ``U+2200``, ``U+211D``) reach it as glyphs. That is the whole point of §24.

Canonical propositions are single-line by construction (see ``canon.build_canonical``), so
the quoted form is rare and no arm systematically carries more escape text than another.
"""

from __future__ import annotations

import json
import re

__all__ = ["write_atom", "read_atom", "write_text", "read_text", "needs_quote", "JSON"]

JSON = json.JSONDecoder()

#: Bare atoms: identifier-like, no whitespace, no delimiter that any arm uses as syntax.
_BARE = re.compile(r"^[^\s\"(){}\[\],;:@#←⊢|]+$")

#: Characters that must never appear unquoted in a line-oriented surface. Everything below
#: U+0020 plus the three Unicode line breaks ``str.splitlines`` honours -- the same set the
#: frozen HML view escapes, and for the same reason: a proposition must not be able to cut
#: its own line in half.
_UNSAFE = tuple(chr(c) for c in range(0x20)) + ("\u0085", "\u2028", "\u2029")


#: Bare words a JSON reader would consume as literals. Lean genuinely binds case labels named
#: ``false`` (``case false`` in a Bool split), and a tokenizer that reads that as the boolean
#: ``False`` silently renames the branch. Quoting them keeps identifier position unambiguous.
_RESERVED = frozenset({"true", "false", "null"})


def needs_quote(value: str) -> bool:
    if not value:
        return True
    return value in _RESERVED or not bool(_BARE.match(value))


def write_atom(value: str) -> str:
    """An identifier-position value: bare when unambiguous, JSON otherwise."""
    return value if not needs_quote(value) else json.dumps(value, ensure_ascii=False)


def read_atom(token: str) -> str:
    if token.startswith('"'):
        return json.loads(token)
    return token


def write_text(value: str) -> str:
    """A proposition-position value: literal unless it opens a quote or could break a line."""
    if value == "" or value.startswith('"') or any(c in value for c in _UNSAFE):
        return json.dumps(value, ensure_ascii=False)
    return value


def read_text(rest: str) -> str:
    rest = rest.strip()
    if rest.startswith('"'):
        value, end = JSON.raw_decode(rest)
        if rest[end:].strip():
            raise ValueError(f"trailing content after quoted text: {rest[end:][:40]!r}")
        return value
    return rest
