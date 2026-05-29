# DewaldOosthuizen/python_rest_tutorial — Copilot Instructions

Always reference these instructions first and fall back to search or
bash only when you encounter something that does not match the info here.

---

<!-- graph-tools-start -->

## Code Exploration and Token Efficiency

If `.codegraph/` exists, use CodeGraph tools FIRST for symbol lookup,
context gathering, and call tracing before opening any source files.

```bash
codegraph context "<task description>" -p .
codegraph query "<ClassName or function>" -p .
codegraph affected <changed-files> -p .   # find affected tests
codegraph sync .                          # after any code changes
```

If `.understand-anything/knowledge-graph.json` exists, use it for architecture
questions (layers, relationships, guided tour) — launch the dashboard with:

```bash
cd ~/.understand-anything-plugin/packages/dashboard
GRAPH_DIR=$(pwd) npx vite --host 127.0.0.1
```

Fall back to grep/file reading only when these tools return insufficient results.

<!-- graph-tools-end -->
