# Zed Tree-sitter Markdown

A Zed extension that overrides the built-in `Markdown` and `Markdown-Inline`
languages with upstream `tree-sitter-markdown` grammars and queries.

It exists to keep Zed Markdown behavior closer to upstream tree-sitter
coverage, including:

- heading marker punctuation like `#`
- link and image punctuation like `![]()`
- code span and emphasis delimiters
- inline raw HTML injection
- YAML front matter injection

## Install In Zed

1. Open Zed.
2. Run `zed: install dev extension`.
3. Select this repository directory.

## Sync From Upstream

To refresh the extension from the latest upstream `tree-sitter-markdown`
repository:

```bash
python3 scripts/sync_from_upstream.py
```

To sync from a local checkout instead:

```bash
python3 scripts/sync_from_upstream.py --source-repo /path/to/tree-sitter-markdown
```

The sync configuration lives in `upstream_sync.toml`.

## Notes

- This extension intentionally only targets Markdown behavior.
- It keeps a small number of Zed-specific adjustments where upstream queries do
  not map directly onto Zed's syntax names or injection behavior.
