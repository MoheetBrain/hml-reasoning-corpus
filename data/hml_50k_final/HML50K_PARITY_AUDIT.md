# HML50K representation parity audit

Result: `PASS`.

Both views originate from one canonical VNext transition. The independent audit checked:

- exact record, parent, split, task, label, and canonical-hash identity;
- 56,000 identical candidate sets and candidate orders;
- 112,000 independently parsed HML states equal to the Neutral state objects;
- 224,000 identical action envelopes;
- HML state round-trip through the pinned independent parser;
- cross-boundary corruption rejection for hypothesis, goal, action, scope, branch,
  obligation, dependency, actual corpus claim, actual corpus action, and actual dependency.

No HML_TREE view and no HML→JSON or JSON→HML crossed target exists. See
`audits/parity_audit.json` and `audits/mutation_tests.json`.
