# Gold-10 controlled repin: before/after matrix

This matrix is the same 23-transition Gold-10 set. “Pure repin” means the old
corpus renderer was executed after pinning HML to `5688aba`; “adapted corpus” adds
only corpus-side evidence/judgment rendering. The canonical mathematical payload
was checked against corpus base `467a4866756e6653c1b618a1eed479cda8d5927a` with
rendering and HML-pin metadata excluded from the comparison.

| transition | old HML @ `164d194` | pure repin @ `5688aba` | adapted corpus @ `5688aba` | final representability | final verification path | remaining blocker |
|---|---|---|---|---|---|---|
| G01:a0 | native domain path | unchanged | unchanged | CURRENT_HML | NATIVE_KERNEL | — |
| G01:a1 | native subtraction | unchanged | unchanged | CURRENT_HML | NATIVE_KERNEL | — |
| G01:a2 | numeric normalization not rendered | checker available, unused | `closed_eval_v1` validates `5-2=3` | CURRENT_HML | CHECKED_CERTIFICATE | — |
| G02:a0 | native substitution | unchanged | unchanged | CURRENT_HML | NATIVE_KERNEL | — |
| G02:a1 | numeric evaluation not rendered | checker available, unused | `closed_eval_v1` validates `2+3=5` | CURRENT_HML | CHECKED_CERTIFICATE | — |
| G03:a0 | definition call only | checker available, unused | `definition_unfold_v1` validates `f(3)=4` | CURRENT_HML | CHECKED_CERTIFICATE | — |
| G03:a1 | dependency structure only | checker available, unused | `definition_unfold_v1` validates `g(3)=2*4` | CURRENT_HML | CHECKED_CERTIFICATE | — |
| G03:a2 | final value not evidenced | checker available, unused | `definition_unfold_v1` validates `g(3)=8` | CURRENT_HML | CHECKED_CERTIFICATE | — |
| G04:a0 | native precondition | unchanged | unchanged | CURRENT_HML | NATIVE_KERNEL | — |
| G04:a1 | native inequality rule | unchanged | unchanged | CURRENT_HML | NATIVE_KERNEL | — |
| G05:a0 | native modus ponens | unchanged | unchanged | CURRENT_HML | NATIVE_KERNEL | — |
| G05:a1 | native discharge | unchanged | unchanged | CURRENT_HML | NATIVE_KERNEL | — |
| G06:a0 | implicit countermodel | certified checker available, unused | two checked models emitted | CURRENT_HML | CHECKED_CERTIFICATE | — |
| G06:a1 | missing epistemic terminal | `UNDERDETERMINED` exists, old renderer unused | `undetermined g0 by e1` accepted | CURRENT_HML | CHECKED_CERTIFICATE | — |
| G07:a0 | quantified goal parses | unchanged | unchanged | CURRENT_HML | NATIVE_KERNEL | — |
| G07:a1 | no generic quantifier proof path | generic core exists; body untrusted | unchanged Gold-10 body | LIBRARY_REQUIRED | LIBRARY_CERTIFICATE_REQUIRED | trusted evidence for `n+0=n` |
| G08:a0 | native modus tollens | unchanged | unchanged | CURRENT_HML | NATIVE_KERNEL | — |
| G08:a1 | native discharge | unchanged | unchanged | CURRENT_HML | NATIVE_KERNEL | — |
| G09:a0 | probability law not inferred | no probability-law core rule | unchanged | LIBRARY_REQUIRED | LIBRARY_CERTIFICATE_REQUIRED | conditional-probability product theorem |
| G09:a1 | numeric product not evidenced | checker available, unused | `closed_eval_v1` validates `0.5*0.8=0.4` | CURRENT_HML | CHECKED_CERTIFICATE | — |
| G10:a0 | native domain precondition | unchanged | unchanged | CURRENT_HML | NATIVE_KERNEL | — |
| G10:a1 | derivative theorem not inferred | calculus law absent by design | unchanged | LIBRARY_REQUIRED | LIBRARY_CERTIFICATE_REQUIRED | trusted calculus evidence |
| G10:a2 | numeric derivative not evidenced | numeric checker available, full transition blocked | numeric substep checked; full action remains blocked | LIBRARY_REQUIRED | LIBRARY_CERTIFICATE_REQUIRED | valid derivative formula and calculus evidence |

The machine-readable form, including the separate representability, verification
path, and outcome dimensions, is [PHASE_B_ADAPTED.json](PHASE_B_ADAPTED.json).
