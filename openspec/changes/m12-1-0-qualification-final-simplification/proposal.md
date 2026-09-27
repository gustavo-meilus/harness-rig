## Why

M11 passed with recorded limits, so the final 1.0 qualification can begin from
the committed baseline `bccbfcb7c4d03df843d7bc5a1a87a343d0b6c7d7`. M12 must
show that the supported product scope still satisfies its trust, host,
repository, migration, and release claims, and retire anything not supported
by evidence.

## What Changes

- Re-run the existing deterministic, adversarial, Context, OpenSpec, CI,
  migration, gate, and release-provenance checks against the final tree.
- Retain current native evidence for the supported Stable host and verify
  unsupported host capabilities remain explicit non-claims.
- Produce a complete current-revision repository verdict and verify local
  release provenance against it.
- Record a fresh-context architecture review, feature-retirement review, and
  final M12 decision as `PASS` or a precise `BLOCKED` result.
- Keep the M12 scope limited to qualification and final simplification. Do not
  add product behavior without updating this change first.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This change qualifies existing behavior and records evidence; it does not
change product requirements. Specs are deliberately skipped in
`.openspec.yaml`.

## Impact

The work uses existing product code, tests, verification scripts, M8-M11
evidence, and CI/release contracts. It will add M12 verification artifacts and
update the roadmap, progressive plan, canonical Context references, generated
manifest, and agent projection. Any required product fix is out of this
qualification scope until the OpenSpec design and acceptance criteria are
updated.
