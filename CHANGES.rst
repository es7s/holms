###########
Changelog
###########

This project uses Semantic Versioning -- https://semver.org

===============
Version list
===============

0.3.0 (Oct 23)
---------------
- Core

0.4.0 (Oct 23)
---------------
- Add `--count` option.

0.5.0 (Nov 23)
----------------
- Add `--color` and `--no-color` options.
- Add `index` column.
- Add chars/names internal overrides.

1.0.0 (Nov 23)
---------------
- 🌱 NEW: `raw`, `type`, `typename` columns
- 🌱 NEW: `--legend` option
- 🌱 NEW: add readme img generating script

1.1.0 (Nov 23)
---------------
- 🌱 NEW: basic latin letters different look
- 🐞 FIX: `--version` option
- 🐞 FIX: `dev` environment initializing

1.2.0 (Dec 23)
---------------
- 🐞 FIX: invoking main entrypoint in testing environment
- 🐞 FIX: missing counts with `--merge` option, but without `--group`
- 💎 REFACTOR: `-F|--full` -> `-a|--all`, `-S` -> `-s`
- 🧪 TESTS: environment
- 🧪 TESTS: `writer`
- 🧪 TESTS: `cli` (WIP)

1.3.0 (Feb 24)
---------------
- 🌱 NEW: `--oneline` option
- 💥 REWORK: complete rewrite of CLI entrypoint, splitting one command into 5 separate ones

1.3.1 (Feb 24)
---------------
- 🐞 FIX: main entrypoint
