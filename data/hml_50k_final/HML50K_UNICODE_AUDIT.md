# HML50K Unicode audit

Result: `PASS`.

Every JSON serialization uses `ensure_ascii=False`. Across every task, split, and paired
view, the audit found 14,039,188 literal non-ASCII codepoints and zero JSON `\uXXXX`
escape sequences. This preserves Lean glyphs such as `⊢`, `∀`, `ℝ`, and daggered binder
names as tokenizer-native text. See `audits/unicode_audit.json`.
