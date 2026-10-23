#!/usr/bin/env python3
"""Portfolio builder — case-study edition.
Renders portfolio.json projects as full case studies (problem/build/reliability/proof/tech/links/media),
injects hero data, proof strip, "How I build" and "What I work on" sections from JSON where markers exist.
Static HTML+CSS only. GitHub Pages compatible.
"""
import json, html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "template.html"
DATA = ROOT / "portfolio.json"
OUT = ROOT / "index.html"
START = "<!-- AUTO_PROJECTS_START -->"
END = "<!-- AUTO_PROJECTS_END -->"
HOW_START = "<!-- AUTO_HOWIBUILD_START -->"
HOW_END = "<!-- AUTO_HOWIBUILD_END -->"


def esc(v):
    return html.escape(str(v), quote=True)


def workflow_visual(metric, label):
    return f'''<div class="workflow-visual reliability-visual" role="img" aria-label="Abstract workflow reliability diagram">
      <svg viewBox="0 0 760 280" aria-hidden="true">
        <g class="wires" fill="none" stroke="#52606f" stroke-width="3">
          <path d="M145 140 H260"/><path d="M370 140 H485"/><path d="M595 140 H690"/>
        </g>
        <g class="node"><rect x="35" y="102" rx="16" width="110" height="76"/><text x="90" y="136">Webhook</text><text class="sub" x="90" y="157">lead intake</text></g>
        <g class="node"><rect x="260" y="102" rx="16" width="110" height="76"/><text x="315" y="136">Validate</text><text class="sub" x="315" y="157">dedupe</text></g>
        <g class="node"><rect x="485" y="102" rx="16" width="110" height="76"/><text x="540" y="136">Route</text><text class="sub" x="540" y="157">safe state</text></g>
        <g class="node"><rect x="650" y="102" rx="16" width="85" height="76"/><text x="692" y="136">Done</text><text class="sub" x="692" y="157">receipt</text></g>
      </svg>
      <div class="visual-badge">{esc(metric)} <span>{esc(label)}</span></div>
    </div>'''


def terminal_visual(metric, label):
    return f'''<div class="workflow-visual terminal-visual" role="img" aria-label="LLM structured response terminal">
      <div class="terminal-card"><div class="terminal-top"><span></span><span></span><span></span><small>structured_output.json</small></div><pre>{{
  <b>"category"</b>: "hvac",
  <b>"urgency"</b>: "high",
  <b>"intent"</b>: "service_request",
  <b>"confidence"</b>: 0.96
}}</pre></div>
      <div class="signal-lines"><span></span><span></span><span></span><span></span></div>
      <div class="visual-badge">{esc(metric)} <span>{esc(label)}</span></div>
    </div>'''


def phone_visual(metric, label):
    return f'''<div class="workflow-visual phone-visual" aria-label="Mobile opportunity control dashboard (sanitized illustrative UI)">
      <div class="phone-shell"><div class="phone-notch"></div><div class="phone-screen">
        <div class="phone-head"><strong>Approval queue</strong><span class="online">● Gate</span></div>
        <div class="metric-grid"><div><b>Draft</b><small>→ Approve</small></div><div><b>Send</b><small>→ Monitor</small></div><div><b>Reply</b><small>→ Cancel FA</small></div></div>
        <div class="lead-row"><span class="lead-dot hot"></span><div><b>Approval gate</b><small>nothing sends without a tap</small></div><em>→</em></div>
        <div class="lead-row"><span class="lead-dot"></span><div><b>Reply watcher</b><small>inbound mirrored to thread</small></div><em>→</em></div>
        <div class="lead-row dim"><span class="lead-dot"></span><div><b>Follow-ups</b><small>auto-cancel on reply</small></div><em>→</em></div>
      </div></div><div class="visual-badge">{esc(metric)} <span>{esc(label)}</span></div>
    </div>'''


def architecture_visual(metric, label):
    return f'''<div class="workflow-visual reliability-visual" role="img" aria-label="Sanitized Opportunity Engine architecture diagram">
      <svg viewBox="0 0 760 280" aria-hidden="true">
        <g class="wires" fill="none" stroke="#52606f" stroke-width="3">
          <path d="M120 140 H215"/><path d="M330 140 H425"/><path d="M540 140 H635"/>
          <path d="M372 178 V215 H582 V178"/>
        </g>
        <g class="node"><rect x="10" y="102" rx="16" width="110" height="76"/><text x="65" y="132">Discover</text><text class="sub" x="65" y="153">sources</text></g>
        <g class="node"><rect x="215" y="102" rx="16" width="115" height="76"/><text x="272" y="132">Qualify</text><text class="sub" x="272" y="153">score · dedupe</text></g>
        <g class="node"><rect x="425" y="102" rx="16" width="115" height="76"/><text x="482" y="132">Draft</text><text class="sub" x="482" y="153">approval gate</text></g>
        <g class="node"><rect x="635" y="102" rx="16" width="115" height="76"/><text x="692" y="132">Send</text><text class="sub" x="692" y="153">monitor reply</text></g>
        <g class="node"><rect x="582" y="215" rx="16" width="120" height="56"/><text x="642" y="240">Follow-up</text><text class="sub" x="642" y="258">auto-cancel</text></g>
      </svg>
      <div class="visual-badge">{esc(metric)} <span>{esc(label)}</span></div>
    </div>'''


VISUALS = {
    "workflow": workflow_visual,
    "terminal": terminal_visual,
    "phone": phone_visual,
    "architecture": architecture_visual,
}


def links_html(links):
    if not links:
        return ""
    out = []
    for l in links:
        target = ' target="_blank" rel="noopener"' if l["url"].startswith("http") else ""
        cls = "primary" if l.get("kind") == "primary" else "ghost"
        track = f' onclick="gtag(\'event\',\'cta_click\',{{\'link_label\':\'{esc(l["label"])}\',\'link_url\':\'{esc(l["url"])}\'}});"'
        out.append(f'<a class="button small {cls}"{target} href="{esc(l["url"])}"{track}>{esc(l["label"])}{" ↗" if target else ""}</a>')
    return f'<div class="project-links">{"".join(out)}</div>'


def media_html(media):
    if not media:
        return ""
    figs = []
    for m in media:
        cap = f"<figcaption>{esc(m.get('caption',''))}</figcaption>" if m.get("caption") else ""
        figs.append(f'<figure class="project-fig"><img src="{esc(m["src"])}" alt="{esc(m.get("alt",""))}" loading="lazy">{cap}</figure>')
    return f'<div class="project-media">{"".join(figs)}</div>'


def case_block(title, body_html):
    return f'<div class="case-block"><h4>{esc(title)}</h4>{body_html}</div>'


def badge_html(text):
    return f'<p class="case-badge"><span aria-hidden="true">&#9679;</span> {esc(text)}</p>'


def video_html(v):
    """Accessible, no-autoplay, captioned-looking demo video with a real poster frame."""
    if not v:
        return ""
    poster = f' poster="{esc(v["poster"])}"' if v.get("poster") else ""
    # No <track> here on purpose: the walkthrough's captions are burned into the video.
    # A <track> pointing at a missing or empty file would render a broken captions menu.
    tracks = ""
    duration = f'<span class="video-duration">{esc(v["duration_label"])}</span>' if v.get("duration_label") else ""
    return (
        '<figure class="case-video">'
        f'<video controls preload="metadata" playsinline{poster} width="1920" height="1080">'
        f'<source src="{esc(v["src"])}" type="video/mp4">'
        f'{tracks}'
        f'<a href="{esc(v["src"])}">Download the {esc(v.get("duration_label","") or "")} recorded demo (MP4)</a>'
        '</video>'
        f'<figcaption>{esc(v.get("caption",""))}{duration}</figcaption>'
        '</figure>'
    )


def evidence_html(items, label="Technical detail and test evidence"):
    if not items:
        return ""
    lis = "".join(f"<li>{esc(x)}</li>" for x in items)
    return f'<details class="case-evidence"><summary>{esc(label)}</summary><ul class="project-points">{lis}</ul></details>'


def render_project(p, idx):
    if not p.get("public_safe"):
        return ""
    tags = "".join(f"<span>{esc(t)}</span>" for t in p.get("tags", []))
    metric, label = p.get("metric", ""), p.get("metric_label", "")
    vt = p.get("visual_type", "generic")
    visual = VISUALS[vt](metric, label) if vt in VISUALS else generic_visual(metric, label, p["title"])
    reverse = bool(p.get("reverse"))

    one = f'<p class="case-one-liner">{esc(p["one_liner"])}</p>' if p.get("one_liner") else ""

    # Short answers to the four buyer questions.
    summary = ""
    if p.get("problem"):
        summary += case_block("Problem demonstrated", f'<p>{esc(p["problem"])}</p>')
    behaviours = ""
    if p.get("observable"):
        behaviours = case_block(
            "What it visibly does",
            '<ul class="project-points">' + "".join(f"<li>{esc(x)}</li>" for x in p["observable"]) + "</ul>")
    tested = ""
    if p.get("tested") or p.get("not_tested"):
        body = f'<p>{esc(p.get("tested",""))}</p>'
        if p.get("not_tested"):
            body += f'<p class="case-scope"><strong>Outside scope:</strong> {esc(p["not_tested"])}</p>'
        tested = case_block("What was actually tested", body)

    video = video_html(p.get("video"))
    badge = badge_html(p.get("disclosure") or "Independent demo &bull; synthetic data")
    evidence = evidence_html(p.get("evidence") or p.get("reliability") or [])
    tech = ""
    if p.get("tech"):
        tech = ('<div class="case-tech"><span class="case-tech-label">Tech</span>'
                '<div class="project-tags">'
                + "".join(f"<span>{esc(x)}</span>" for x in p["tech"])
                + "</div></div>")

    links = links_html(p.get("links")) or (
        f'<div class="project-links"><a class="button small primary" href="{esc(p["url"])}">{esc(p.get("cta","View project"))}</a></div>' if p.get("url") else "")
    link_note = f'<p class="project-link-note">{esc(p["link_note"])}</p>' if p.get("link_note") else ""

    inner = f"""<div class="case-head">
          <h3>{esc(p['title'])}</h3>
          {badge}
        </div>
        {one}
        {video}
        {summary}
        {behaviours}
        {tested}
        {links}
        {link_note}
        {evidence}
        {tech}"""

    classes = "project-card case-study" + (" project-featured" if p.get("featured") else "")
    rev_class = " reverse" if reverse else ""
    return f'''      <article class="{classes}" data-reveal data-project-id="{esc(p['id'])}">
        <div class="project-meta"><span class="project-number">{idx:02d}</span><div class="project-tags">{tags}</div></div>
        <div class="project-body">{inner}</div>
      </article>'''


def generic_visual(metric, label, title):
    return f'''<div class="workflow-visual generic-visual" role="img" aria-label="Project proof visual">
      <div style="position:relative;z-index:3;text-align:center;padding:38px;max-width:520px">
        <div class="eyebrow">VERIFIED PROJECT</div>
        <div style="font-size:clamp(28px,4vw,48px);font-weight:900;letter-spacing:-.055em;margin-top:14px">{esc(title)}</div>
        <div style="color:#838b96;margin-top:12px">Workflow · evidence · documentation</div>
      </div>
      <div class="visual-badge">{esc(metric)} <span>{esc(label)}</span></div>
    </div>'''


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    template = TEMPLATE.read_text(encoding="utf-8")
    if START not in template or END not in template:
        raise SystemExit("Template missing AUTO_PROJECTS markers")
    projects = [p for p in data.get("projects", []) if p.get("public_safe")]
    rendered = "\n".join(render_project(p, i+1) for i, p in enumerate(projects))
    before, rest = template.split(START, 1)
    _, after = rest.split(END, 1)
    out = before + START + "\n" + rendered + "\n      " + END + after

    # "How I build" section injection (new in v2)
    if HOW_START in out and HOW_END in out and data.get("how_i_build"):
        steps = "".join(f"<article data-reveal><span>{i+1:02d}</span><h3>{esc(s.split('. ',1)[-1] if s[0].isdigit() else s)}</h3></article>"
                        for i, s in enumerate(data["how_i_build"]))
        # simpler: single card list
        items = "".join(f"<li data-reveal>{esc(s)}</li>" for s in data["how_i_build"])
        section = ('<div class="howibuild-grid"><ol class="howibuild-list">' + items + '</ol></div>')
        out = out.replace(HOW_START, section + " ").replace(HOW_END, "")

    OUT.write_text(out, encoding="utf-8")
    print(f"Built {OUT} with {len(projects)} public projects (case-study mode)")


if __name__ == "__main__":
    main()
