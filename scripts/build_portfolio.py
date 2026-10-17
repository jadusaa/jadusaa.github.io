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
        out.append(f'<a class="button small {cls}"{target} href="{esc(l["url"])}">{esc(l["label"])}{" ↗" if target else ""}</a>')
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


def render_project(p, idx):
    if not p.get("public_safe"):
        return ""
    tags = "".join(f"<span>{esc(t)}</span>" for t in p.get("tags", []))
    metric, label = p.get("metric", ""), p.get("metric_label", "")
    vt = p.get("visual_type", "generic")
    visual = VISUALS[vt](metric, label) if vt in VISUALS else generic_visual(metric, label, p["title"])

    one = f'<p class="case-one-liner">{esc(p["one_liner"])}</p>' if p.get("one_liner") else ""
    problem = case_block("Problem", f"<p>{esc(p['problem'])}</p>") if p.get("problem") else ""
    build = case_block("What I built", f"<p>{esc(p['build'])}</p>") if p.get("build") else ""
    rel = ""
    if p.get("reliability"):
        rel = case_block("Reliability & failure handling",
                         '<ul class="project-points">' + "".join(f"<li>{esc(x)}</li>" for x in p["reliability"]) + "</ul>")
    flow = f'<div class="case-flow">{esc(p["flow"])}</div>' if p.get("flow") else ""
    proof = case_block("Proof", f"<p>{esc(p['proof'])}</p>") if p.get("proof") else ""
    tech = ""
    if p.get("tech"):
        tech = case_block("Tech", '<div class="project-tags">'+"".join(f"<span>{esc(x)}</span>" for x in p["tech"])+"</div>")
    legacy_bullet_list = ""
    if not (problem or build):
        bullets = "".join(f"<li>{esc(b)}</li>" for b in p.get("bullets", []))
        legacy_bullet_list = f'<ul class="project-points">{bullets}</ul>'
    links = links_html(p.get("links")) or (
        f'<div class="project-links"><a class="button small primary" href="{esc(p["url"])}">{esc(p.get("cta","View project"))}</a></div>' if p.get("url") else "")

    text = (f'<div><h3>{esc(p["title"])}</h3>{one}'
            f'{problem}{build}{flow}{rel}{proof}{tech}{legacy_bullet_list}'
            f'{media_html(p.get("media"))}{links}</div>')
    reverse = bool(p.get("reverse"))
    inner = visual + text if reverse else text + visual
    classes = "project-card case-study" + (" project-featured" if p.get("featured") else "")
    rev_class = " reverse" if reverse else ""
    return f'''      <article class="{classes}" data-reveal data-project-id="{esc(p['id'])}">
        <div class="project-meta"><span class="project-number">{idx:02d}</span><div class="project-tags">{tags}</div></div>
        <div class="project-content{rev_class}">{inner}</div>
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
