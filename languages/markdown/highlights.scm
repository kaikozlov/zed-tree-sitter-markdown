[
  (paragraph)
  (pipe_table)
] @text

(atx_heading
  (inline) @title.markup)

(setext_heading
  (paragraph) @title.markup)

[
  (atx_h1_marker)
  (atx_h2_marker)
  (atx_h3_marker)
  (atx_h4_marker)
  (atx_h5_marker)
  (atx_h6_marker)
  (setext_h1_underline)
  (setext_h2_underline)
  (thematic_break)
] @punctuation.markup

[
  (link_title)
  (indented_code_block)
  (fenced_code_block)
] @text.literal.markup

(fenced_code_block_delimiter) @punctuation.embedded.markup

(code_fence_content) @none

(link_destination) @link_uri.markup

(link_label) @link_text.markup

[
  (list_marker_plus)
  (list_marker_minus)
  (list_marker_star)
  (list_marker_dot)
  (list_marker_parenthesis)
] @punctuation.list_marker.markup

[
  (block_continuation)
  (block_quote_marker)
] @punctuation.markup

(backslash_escape) @string.escape

(pipe_table_header
  "|" @punctuation.markup)

(pipe_table_row
  "|" @punctuation.markup)

(pipe_table_delimiter_row
  "|" @punctuation.markup)

(pipe_table_delimiter_cell
  "-" @punctuation.markup)
