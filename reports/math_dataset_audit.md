# Hendrycks MATH dataset audit

## Provenance

- Copied parquet: `data/raw/math/train-00000-of-00001-7320a6f3aba8ebd2.parquet`
- Original: `/Users/moheet/Desktop/train-00000-of-00001-7320a6f3aba8ebd2.parquet`
- Source: Hendrycks MATH training split, local Desktop copy
- Rows: **12,500**
- Columns: `problem`, `level`, `type`, `solution`
- Null values: none in all four columns
- Duplicate problems: 0; duplicate problem+solution records: 0

## Category distribution

| Category | Rows | Selected Gold-25 |
|---|---:|---:|
| Algebra | 2,931 | 5 |
| Counting & Probability | 1,245 | 4 |
| Geometry | 1,349 | 3 |
| Intermediate Algebra | 2,198 | 4 |
| Number Theory | 1,409 | 4 |
| Prealgebra | 2,076 | 2 |
| Precalculus | 1,292 | 3 |

## Level distribution

| Level | Rows |
|---|---:|
| Level 1 | 1,001 |
| Level 2 | 2,242 |
| Level 3 | 2,723 |
| Level 4 | 2,904 |
| Level 5 | 3,628 |
| Level ? | 2 |

## Length distributions

- `problem` characters: mean 202.7, median 146, p90 402, max 4309
- `solution` characters: mean 539.3, median 405, p90 1085, max 6767

## Visual/format markers

| Marker | Rows |
|---|---:|
| `[asy]` | 2,071 |
| `tabular` | 78 |
| `\begin{array}` | 225 |
| `\includegraphics` | 0 |
| `image` | 45 |
| `graph` | 617 |
| `diagram` | 292 |

The 25 selected records contain no `[asy]` or `\includegraphics` marker in either problem or solution. This is a text-first discovery set, not a claim that visual reasoning is unimportant.

## Selection

Exactly 25 records were selected deliberately for operation diversity. The manifest preserves each problem and solution verbatim; canonical trajectories are generated separately under `data/gold25/trajectories/`.
