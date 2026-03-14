#!/usr/bin/env python3

import argparse
import re
import shutil
import subprocess
import tempfile
import tomllib
from contextlib import contextmanager
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").strip() + "\n"


def strip_leading_comments(text: str) -> str:
    lines = text.splitlines()
    while lines and lines[0].lstrip().startswith(";"):
        lines.pop(0)
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines)


def ensure_contains(text: str, block: str) -> str:
    block = normalize_newlines(block).rstrip("\n")
    if block in text:
        return text
    return text.rstrip() + "\n\n" + block + "\n"


def replace_once(text: str, pattern: str, replacement: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise ValueError(f"expected exactly one match for pattern: {pattern}")
    return updated


def transform_markdown_block_highlights(text: str) -> str:
    text = strip_leading_comments(text)
    text = text.replace("@text.title", "@title.markup")
    text = text.replace("@text.literal", "@text.literal.markup")
    text = text.replace("@text.uri", "@link_uri.markup")
    text = text.replace("@text.reference", "@link_text.markup")
    text = replace_once(
        text,
        r"\[\n  \(atx_h1_marker\)\n  \(atx_h2_marker\)\n  \(atx_h3_marker\)\n  \(atx_h4_marker\)\n  \(atx_h5_marker\)\n  \(atx_h6_marker\)\n  \(setext_h1_underline\)\n  \(setext_h2_underline\)\n\] @punctuation\.special",
        """[
  (atx_h1_marker)
  (atx_h2_marker)
  (atx_h3_marker)
  (atx_h4_marker)
  (atx_h5_marker)
  (atx_h6_marker)
  (setext_h1_underline)
  (setext_h2_underline)
  (thematic_break)
] @punctuation.markup""",
    )
    text = replace_once(
        text,
        r"\(fenced_code_block_delimiter\) @punctuation\.delimiter",
        "(fenced_code_block_delimiter) @punctuation.embedded.markup",
    )
    text = replace_once(
        text,
        r"\[\n  \(list_marker_plus\)\n  \(list_marker_minus\)\n  \(list_marker_star\)\n  \(list_marker_dot\)\n  \(list_marker_parenthesis\)\n  \(thematic_break\)\n\] @punctuation\.special",
        """[
  (list_marker_plus)
  (list_marker_minus)
  (list_marker_star)
  (list_marker_dot)
  (list_marker_parenthesis)
] @punctuation.list_marker.markup""",
    )
    text = replace_once(
        text,
        r"\[\n  \(block_continuation\)\n  \(block_quote_marker\)\n\] @punctuation\.special",
        """[
  (block_continuation)
  (block_quote_marker)
] @punctuation.markup""",
    )
    text = (
        """[
  (paragraph)
  (pipe_table)
] @text

"""
        + text.strip()
    )
    text = ensure_contains(
        text,
        """(pipe_table_header
  "|" @punctuation.markup)

(pipe_table_row
  "|" @punctuation.markup)

(pipe_table_delimiter_row
  "|" @punctuation.markup)

(pipe_table_delimiter_cell
  "-" @punctuation.markup)""",
    )
    return normalize_newlines(text)


def transform_markdown_block_injections(text: str) -> str:
    text = normalize_newlines(strip_leading_comments(text))
    return text.replace('"markdown_inline"', '"markdown-inline"')


def transform_markdown_inline_highlights(text: str) -> str:
    text = strip_leading_comments(text)
    text = text.replace("@text.literal", "@text.literal.markup")
    text = text.replace("@punctuation.delimiter", "@punctuation.markup")
    text = text.replace("@text.emphasis", "@emphasis.markup")
    text = text.replace("@text.strong", "@emphasis.strong.markup")
    text = text.replace("@text.uri", "@link_uri.markup")
    text = text.replace("@text.reference", "@link_text.markup")
    text = ensure_contains(text, "(strikethrough) @strikethrough.markup")
    text = replace_once(
        text,
        r"\[\n  \(link_destination\)\n  \(uri_autolink\)\n\] @link_uri\.markup",
        """[
  (link_destination)
  (uri_autolink)
  (email_autolink)
] @link_uri.markup""",
    )
    text = ensure_contains(
        text,
        """(collapsed_reference_link
  [
    "["
    "]"
  ] @punctuation.markup)

(full_reference_link
  [
    "["
    "]"
  ] @punctuation.markup)""",
    )
    return normalize_newlines(text)


def transform_markdown_inline_injections(text: str) -> str:
    text = normalize_newlines(strip_leading_comments(text))
    return replace_once(
        text,
        r'\(\(html_tag\) @injection\.content\n  \(#set! injection\.language "html"\)\)',
        '((html_tag) @injection.content\n  (#set! injection.language "html")\n  (#set! injection.combined))',
    )


def transform_identity(text: str) -> str:
    return normalize_newlines(strip_leading_comments(text))


TRANSFORMS = {
    "identity": transform_identity,
    "markdown_block_highlights": transform_markdown_block_highlights,
    "markdown_block_injections": transform_markdown_block_injections,
    "markdown_inline_highlights": transform_markdown_inline_highlights,
    "markdown_inline_injections": transform_markdown_inline_injections,
}


def git(*args: str, cwd: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


@contextmanager
def upstream_checkout(config: dict, source_repo_arg: str | None, ref: str | None):
    if source_repo_arg:
        repo = Path(source_repo_arg).resolve()
        yield repo
        return

    temp_dir = Path(tempfile.mkdtemp(prefix="zed-tree-sitter-markdown-"))
    try:
        subprocess.check_call(
            ["git", "clone", "--depth", "1", config["repository_url"], str(temp_dir)],
            cwd=PROJECT_ROOT,
        )
        if ref:
            subprocess.check_call(["git", "fetch", "--depth", "1", "origin", ref], cwd=temp_dir)
            subprocess.check_call(["git", "checkout", ref], cwd=temp_dir)
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def update_extension_manifest(extension_toml: Path, source_repo: Path, grammars: list[dict]) -> None:
    head_rev = git("rev-parse", "HEAD", cwd=source_repo)
    manifest_text = extension_toml.read_text()
    for grammar in grammars:
        name = grammar["manifest_name"]
        pattern = rf"(\[grammars\.{re.escape(name)}\][^\[]*?rev = \")([0-9a-f]+)(\")"
        manifest_text, count = re.subn(
            pattern,
            rf"\g<1>{head_rev}\g<3>",
            manifest_text,
            count=1,
            flags=re.DOTALL,
        )
        if count != 1:
            raise ValueError(f"could not update rev for grammar {name} in {extension_toml}")
    extension_toml.write_text(manifest_text)


def sync_queries(config_path: Path, source_repo_arg: str | None, ref: str | None) -> None:
    config = tomllib.loads(config_path.read_text())
    extension_toml = PROJECT_ROOT / config["extension_toml"]

    with upstream_checkout(config, source_repo_arg, ref) as source_repo:
        update_extension_manifest(extension_toml, source_repo, config["grammars"])

        for query in config["queries"]:
            source_path = source_repo / query["source"]
            target_path = PROJECT_ROOT / query["target"]
            transform_name = query.get("transform", "identity")
            transform = TRANSFORMS[transform_name]
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(transform(source_path.read_text()))
            print(f"synced {target_path.relative_to(PROJECT_ROOT)} from {query['source']}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync Zed Tree-sitter Markdown query overrides from upstream"
    )
    parser.add_argument(
        "--config",
        default="upstream_sync.toml",
        help="Path to the sync config TOML file relative to the repo root",
    )
    parser.add_argument(
        "--source-repo",
        help="Path to a local tree-sitter-markdown checkout. If omitted, clone the official repo temporarily.",
    )
    parser.add_argument(
        "--ref",
        help="Git ref to checkout when cloning the upstream repo temporarily",
    )
    args = parser.parse_args()
    sync_queries(PROJECT_ROOT / args.config, args.source_repo, args.ref)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
