# DewaldOosthuizen/python_rest_tutorial

This file instructs AI agents (Hermes, GitHub Copilot, Codex, etc.) on how
to orient themselves in this repository efficiently.

<!-- graph-tools-start -->

## graphify

graphify-out/ not yet generated for this repo.

## understand-anything

.understand-anything/knowledge-graph.json is present.
Use it for layered architecture questions (layers, communities, entry points).

```bash
# Launch the interactive dashboard
cd ~/.understand-anything-plugin/packages/dashboard
GRAPH_DIR=$(pwd) npx vite --host 127.0.0.1
```

For prose questions load the skill:
```
skill: understand-chat
```

## codegraph

.codegraph/ is present. Use it FIRST for any symbol lookup,
call tracing, or targeted context gathering before opening source files.

```bash
codegraph context "<task description>" -p .   # focused file+symbol context
codegraph query "<ClassName or function>" -p . # where is X defined / used
codegraph affected <changed-files> -p .        # which tests are affected
codegraph sync .                               # after any code change
```

Decision order for code tasks:
  1. codegraph context  — which symbols matter?
  2. graphify query     — which files are involved?
  3. understand-anything — where in the architecture does this live?
  4. Read raw source    — only the 1-2 files that actually matter.

<!-- graph-tools-end -->
