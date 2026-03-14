[
  (code_span)
  (link_title)
] @text.literal.markup

[
  (emphasis_delimiter)
  (code_span_delimiter)
] @punctuation.markup

(emphasis) @emphasis.markup

(strong_emphasis) @emphasis.strong.markup

[
  (link_destination)
  (uri_autolink)
  (email_autolink)
] @link_uri.markup

[
  (link_label)
  (link_text)
  (image_description)
] @link_text.markup

[
  (backslash_escape)
  (hard_line_break)
] @string.escape

(image
  [
    "!"
    "["
    "]"
    "("
    ")"
  ] @punctuation.markup)

(inline_link
  [
    "["
    "]"
    "("
    ")"
  ] @punctuation.markup)

(shortcut_link
  [
    "["
    "]"
  ] @punctuation.markup)

; NOTE: extension not enabled by default
; (wiki_link ["[" "|" "]"] @punctuation.markup)

(strikethrough) @strikethrough.markup

(collapsed_reference_link
  [
    "["
    "]"
  ] @punctuation.markup)

(full_reference_link
  [
    "["
    "]"
  ] @punctuation.markup)
