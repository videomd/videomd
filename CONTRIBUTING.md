# Contributing

## Proposing a change

Open an issue that says:

1. What a reader or producer cannot do today.
2. The field, key, topic file or id you propose, with an example.
3. Whether existing packages stay valid. Most proposals are additions and keep `videomd: 1`; a change of meaning needs a new version.

## Taxonomy ids

Before proposing a new id, try it as an `x-` id in your own packages. An `x-` id that more than one producer uses, or that a consumer needs, is the strongest case for adding it to [TAXONOMY.md](docs/taxonomy.md).

## Changes to the spec

A pull request that changes [SPEC.md](docs/spec.md) updates, together:

- the schema in `schema/` and its copy in `src/videomd/`,
- the validator, when a conformance rule changes,
- a case in `conformance/valid/` or `conformance/invalid/` that shows the change,
- [CHANGELOG.md](CHANGELOG.md),
- the Chinese pages in `docs/zh/` and `README.zh-CN.md`, or a note in the pull request that they need updating.

Run the tests:

```bash
pip install -e ".[dev]"
python -m pytest -q
```
