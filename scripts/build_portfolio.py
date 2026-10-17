#!/usr/bin/env python3
import json, html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "template.html"
DATA = ROOT / "portfolio.json"
OUT = ROOT / "index.html"
START = "<!-- AUTO_PROJECTS_START -->"
END = "<!-- AUTO_PROJECTS_END -->"


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
    return f'''<div class="workflow-visual phone-visual" aria-label="Mobile opportunity control dashboard">
      <div class="phone-shell"><div class="phone-notch"></div><div class="phone-screen">
        <div class="phone-head"><strong>Opportunity Engine</strong><span class="online">● Online</span></div>
        <div class="metric-grid"><div><b>03</b><small>Approval</small></div><div><b>01</b><small>Replies</small></div><div><b>02</b><small>Follow-ups</small></div></div>
        <div class="lead-row"><span class="lead-dot hot"></span><div><b>n8n Automation Role</b><small>Score 91 · Ready</small></div><em>→</em></div>
        <div class="lead-row"><span class="lead-dot"></span><div><b>AI Workflow Project</b><small>Score 86 · Drafted</small></div><em>→</em></div>
        <div class="lead-row dim"><span class="lead-dot"></span><div><b>Agency Lead</b><small>Waiting · 2d</small></div><em>→</em></div>
      </div></div><div class="visual-badge">{esc(metric)} <span>{esc(label)}</span></div>
    </div>'''


def generic_visual(metric, label, title):
    return f'''<div class="workflow-visual generic-visual" role="img" aria-label="Project proof visual">
      <div style="position:relative;z-index:3;text-align:center;padding:38px;max-width:520px">
        <div class="eyebrow">VERIFIED PROJECT</div>
        <div style="font-size:clamp(28px,4vw,48px);font-weight:900;letter-spacing:-.055em;margin-top:14px">{esc(title)}</div>
        <div style="color:#838b96;margin-top:12px">Workflow · evidence · documentation</div>
      </div>
      <div class="visual-badge">{esc(metric)} <span>{esc(label)}</span></div>
    </div>'''

VISUALS = {
    "workflow": workflow_visual,
    "terminal": terminal_visual,
    "phone": phone_visual,
}


def render_project(p, idx):
    if not p.get("public_safe"):
        return ""
    tags = "".join(f"<span>{esc(t)}</span>" for t in p.get("tags", []))
    bullets = "".join(f"<li>{esc(b)}</li>" for b in p.get("bullets", []))
    metric, label = p.get("metric", ""), p.get("metric_label", "")
    vt = p.get("visual_type", "generic")
    if vt in VISUALS:
        visual = VISUALS[vt](metric, label)
    else:
        visual = generic_visual(metric, label, p["title"])
    link = ""
    if p.get("url"):
        target = ' target="_blank" rel="noopener"' if p["url"].startswith("http") else ""
        cls = "primary" if p["url"].startswith("http") else "ghost"
        link = f'<div class="project-links"><a class="button small {cls}"{target} href="{esc(p["url"])}">{esc(p.get("cta","View project ↗"))}</a></div>'
    text = f'''<div><h3>{esc(p["title"])}</h3><p>{esc(p["summary"])}</p><ul class="project-points">{bullets}</ul>{link}</div>'''
    reverse = bool(p.get("reverse"))
    inner = visual + text if reverse else text + visual
    classes = "project-card" + (" project-featured" if p.get("featured") else "")
    rev_class = " reverse" if reverse else ""
    return f'''      <article class="{classes}" data-reveal data-project-id="{esc(p['id'])}">
        <div class="project-meta"><span class="project-number">{idx:02d}</span><div class="project-tags">{tags}</div></div>
        <div class="project-content{rev_class}">{inner}</div>
      </article>'''


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    template = TEMPLATE.read_text(encoding="utf-8")
    if START not in template or END not in template:
        raise SystemExit("Template missing AUTO_PROJECTS markers")
    projects = [p for p in data.get("projects", []) if p.get("public_safe")]
    rendered = "\n".join(render_project(p, i+1) for i,p in enumerate(projects))
    before, rest = template.split(START, 1)
    _, after = rest.split(END, 1)
    out = before + START + "\n" + rendered + "\n      " + END + after
    OUT.write_text(out, encoding="utf-8")
    print(f"Built {OUT} with {len(projects)} public projects")

if __name__ == "__main__":
    main()
