# Gold-10 exact payload size

The measured payload is exactly the ten canonical trajectories plus their per-example
problem/source and three renderings. It excludes `hml_core`, reports, schemas, tests, and
the manifest.

- Files: **50** (10 canonical trajectory JSON files + 40 source/rendering files)
- UTF-8 bytes: **86,028**
- Lexical tokens: **28,053**
- Tokenizer: Unicode regex `\w+|[^\w\s]`, implemented by
  `src/hml_corpus/size.py`

This is an exact reproducible corpus-size measurement, not a claim about any model's BPE
tokenizer. Re-run `python3 scripts/measure_gold10.py` to reproduce it.
