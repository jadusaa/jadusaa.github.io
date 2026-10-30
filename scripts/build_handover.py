#!/usr/bin/env python3
"""
Build the handover sample as a styled, mobile-friendly HTML page.

Deliberate constraints:
  - Markdown stays the single content source (docs/HANDOVER_SAMPLE_lead-intake.md)
  - No third-party renderer, no CDN, no client-side JS, no new dependency
  - Output is self-contained HTML matching the portfolio's visual language
  - Wide tables scroll inside their own container; the page never scrolls sideways

Usage:  python3 scripts/build_handover.py
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "HANDOVER_SAMPLE_lead-intake.md"
OUT = ROOT / "docs" / "handover-sample.html"

CSS = """
:root{
  --ink:#1c1917; --muted:#57534e; --line:#e7e5e4; --bg:#faf9f7; --card:#fff;
  --accent:#3f6212; --accent-soft:#ecf3e3; --warn:#7c2d12; --warn-bg:#fdf1e7;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font:400 17px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  padding:20px 16px 64px;
}
.wrap{max-width:760px;margin:0 auto}
.topbar{display:flex;flex-wrap:wrap;gap:10px;justify-content:space-between;align-items:center;margin-bottom:22px}
.back,.dl{
  display:inline-block;padding:9px 14px;border-radius:8px;text-decoration:none;
  font-size:15px;font-weight:600;border:1px solid var(--line);background:var(--card);color:var(--ink);
}
.back:hover,.dl:hover{border-color:#d6d3d1}
.dl{background:var(--accent);border-color:var(--accent);color:#fff}
.doc{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:24px 20px}
h1{font-size:clamp(24px,6vw,32px);line-height:1.25;margin:0 0 6px;letter-spacing:-.02em}
h2{font-size:clamp(19px,4.4vw,23px);line-height:1.3;margin:34px 0 10px;padding-top:18px;border-top:1px solid var(--line)}
h2:first-of-type{border-top:0;padding-top:0}
h3{font-size:18px;margin:22px 0 8px}
p{margin:0 0 14px}
ul,ol{margin:0 0 16px;padding-left:22px}
li{margin:0 0 8px}
strong{font-weight:650}
hr{border:0;border-top:1px solid var(--line);margin:28px 0}
a{color:#2563eb;text-decoration:underline;text-underline-offset:2px}
.lead{color:var(--muted)}
.note{
  background:var(--accent-soft);border-left:4px solid var(--accent);
  padding:14px 16px;border-radius:0 10px 10px 0;margin:0 0 18px;font-size:16px;
}
.warn{
  background:var(--warn-bg);border-left:4px solid var(--warn);
  padding:14px 16px;border-radius:0 10px 10px 0;margin:0 0 18px;
}
.warn strong{color:var(--warn)}
/* tables: scroll locally, never the page */
.tablewrap{
  margin:0 0 20px;border:1px solid var(--line);border-radius:10px;
  overflow-x:auto;-webkit-overflow-scrolling:touch;
}
.tablewrap:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
table{border-collapse:collapse;width:100%;min-width:520px;font-size:15.5px}
caption{
  caption-side:top;text-align:left;padding:10px 14px;font-size:14px;font-weight:650;
  color:var(--muted);background:#f5f5f4;border-bottom:1px solid var(--line);
}
th,td{padding:11px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}
th{background:#f5f5f4;font-weight:650;white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
code{
  font:400 .91em/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;
  background:#f5f5f4;padding:1px 5px;border-radius:4px;
  overflow-wrap:anywhere;word-break:break-word;
}
.footer{margin-top:26px;color:var(--muted);font-size:15px}
@media (max-width:520px){
  body{font-size:16px;padding:14px 12px 48px}
  .doc{padding:18px 15px}

  /* Stack table rows: no horizontal scrolling, nothing clipped on a phone. */
  .tablewrap{overflow:visible;border:0;background:transparent}
  table{min-width:0;width:100%;display:block;font-size:15.5px}
  caption{display:block;background:#f5f5f4;border:1px solid var(--line);
          border-bottom:0;border-radius:10px 10px 0 0;padding:10px 13px}
  thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
  tbody{display:block;border:1px solid var(--line);border-top:0;
        border-radius:0 0 10px 10px;overflow:hidden}
  tr{display:block;border-bottom:1px solid var(--line)}
  tr:last-child{border-bottom:0}
  td{
    display:block;border:0;padding:9px 13px 9px 13px;
  }
  td+td{border-top:1px dashed var(--line)}
  td::before{
    content:attr(data-label);
    display:block;font-size:12.5px;font-weight:700;letter-spacing:.04em;
    text-transform:uppercase;color:var(--muted);margin-bottom:3px;
  }
  td:first-child{background:#fafaf9;font-weight:650}
}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
"""


def inline(text: str) -> str:
    """Inline markdown -> HTML. Escapes first, so no raw HTML passes through."""
    t = html.escape(text, quote=False)
    t = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
    return t


def is_table_row(line: str) -> bool:
    return line.strip().startswith("|") and line.strip().endswith("|")


def split_row(line: str):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def convert(md: str) -> str:
    lines = md.split("\n")
    out, i = [], 0
    in_ul = in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    while i < len(lines):
        line = lines[i]
        s = line.strip()

        # blank
        if not s:
            close_lists()
            out.append("")
            i += 1
            continue

        # horizontal rule
        if re.fullmatch(r"-{3,}", s):
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        # table: header row + separator row
        if is_table_row(s) and i + 1 < len(lines) and re.fullmatch(
                r"\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?", lines[i + 1].strip()):
            close_lists()
            headers = split_row(s)
            i += 2
            rows = []
            while i < len(lines) and is_table_row(lines[i]):
                rows.append(split_row(lines[i]))
                i += 1
            # first column often acts as the row label -> use as caption hint
            cap = headers[0]
            out.append('<div class="tablewrap" tabindex="0" role="region" '
                       f'aria-label="{html.escape(cap)} table (scrolls horizontally)">')
            out.append(f"<table><caption>{inline(cap)}</caption><thead><tr>")
            for h in headers:
                out.append(f"<th scope=\"col\">{inline(h)}</th>")
            out.append("</tr></thead><tbody>")
            for r in rows:
                out.append("<tr>")
                for hi, c in enumerate(r):
                    label = headers[hi] if hi < len(headers) else ""
                    out.append(f'<td data-label="{html.escape(label)}">{inline(c)}</td>')
                out.append("</tr>")
            out.append("</tbody></table></div>")
            continue

        # headings
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            close_lists()
            lvl = len(m.group(1))
            tag = "h1" if lvl == 1 else ("h2" if lvl == 2 else "h3")
            out.append(f"<{tag}>{inline(m.group(2))}</{tag}>")
            i += 1
            continue

        # unordered list
        m = re.match(r"^[-*]\s+(.*)$", s)
        if m:
            if in_ol:
                out.append("</ol>"); in_ol = False
            if not in_ul:
                out.append("<ul>"); in_ul = True
            out.append(f"<li>{inline(m.group(1))}</li>")
            i += 1
            continue

        # ordered list
        m = re.match(r"^\d+[.)]\s+(.*)$", s)
        if m:
            if in_ul:
                out.append("</ul>"); in_ul = False
            if not in_ol:
                out.append("<ol>"); in_ol = True
            out.append(f"<li>{inline(m.group(1))}</li>")
            i += 1
            continue

        # blockquote -> note
        m = re.match(r"^>\s?(.*)$", s)
        if m:
            close_lists()
            buf = [m.group(1)]
            i += 1
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            out.append(f'<div class="note">{inline(" ".join(x for x in buf if x))}</div>')
            continue

        # paragraph
        close_lists()
        out.append(f"<p>{inline(s)}</p>")
        i += 1

    close_lists()
    return "\n".join(out)


def postprocess(body: str) -> tuple[str, str]:
    """Pull the sample label into a note, and turn the caution into a warning box."""
    title = "Sample handover document"
    m = re.search(r"<h1>(.*?)</h1>", body)
    if m:
        title = re.sub(r"<[^>]+>", "", m.group(1))
        body = body.replace(m.group(0), "", 1)

    # the "Sample document." opening paragraph becomes a labelled note
    body = re.sub(r"<p>(<strong>Sample document\.</strong>.*?)</p>",
                  r'<div class="note">\1</div>', body, count=1, flags=re.S)

    # caution blocks -> warning styling (lines that begin "Do not" / "Not tested")
    body = re.sub(r"<p>(<strong>Do not</strong>.*?)</p>", r'<div class="warn">\1</div>', body, flags=re.S)
    return title, body


def main() -> int:
    md = SRC.read_text(encoding="utf-8")
    title, body = postprocess(convert(md))
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — Jawad Sabir</title>
<meta name="description" content="Sample handover runbook from an n8n lead-intake workflow build: failure handling, troubleshooting, safe replay and scope limits.">
<meta name="robots" content="index,follow">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <div class="topbar">
    <a class="back" href="../index.html">&larr; Back to portfolio</a>
    <a class="dl" href="HANDOVER_SAMPLE_lead-intake.md" download>Download Markdown</a>
  </div>
  <main class="doc">
    <h1>{html.escape(title)}</h1>
{body}
  </main>
  <p class="footer">Markdown source: <a href="HANDOVER_SAMPLE_lead-intake.md">HANDOVER_SAMPLE_lead-intake.md</a>
  &middot; <a href="../index.html">Back to portfolio</a></p>
</div>
</body>
</html>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"WROTE {OUT} ({len(page)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
