#!/usr/bin/env python3
import argparse, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"portfolio.json"

ap=argparse.ArgumentParser()
ap.add_argument("--manifest", required=True)
args=ap.parse_args()
manifest=Path(args.manifest)
p=json.loads(manifest.read_text(encoding="utf-8"))
required=["id","title","summary","tags","metric","metric_label","visual_type","featured","reverse","public_safe"]
missing=[k for k in required if k not in p]
if missing:
    raise SystemExit("Missing fields: "+", ".join(missing))
if p["public_safe"] is not True:
    raise SystemExit("Refusing to publish: public_safe must be true")
# case-study mode: either full case fields OR legacy bullets+url
has_case = bool(p.get("problem")) and bool(p.get("build")) and bool(p.get("proof"))
has_legacy = isinstance(p.get("bullets"),list) and len(p.get("bullets",[]))>=2
if not (has_case or has_legacy):
    raise SystemExit("Need either case-study fields (problem+build+proof) or >=2 evidence bullets")
# link/CTA normalization
if has_case:
    if not isinstance(p.get("links"),list) or not p["links"]:
        raise SystemExit("Case-study mode requires links[] (View GitHub / evidence etc.)")
# optional extended fields (v2 schema)
for k in ("reliability","tech","media","one_liner","flow","visibility","private_notes","public_case_study","test_metrics"):
    if k in p and p[k] is None:
        p.pop(k)  # drop nulls silently
if "visibility" not in p:
    p["visibility"] = "public"

data=json.loads(DATA.read_text(encoding="utf-8"))
projects=data.setdefault("projects",[])
for i,old in enumerate(projects):
    if old.get("id")==p["id"]:
        projects[i]=p
        action="updated"
        break
else:
    projects.append(p); action="added"
DATA.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
subprocess.run([sys.executable,str(ROOT/"scripts/build_portfolio.py")],check=True)
subprocess.run([sys.executable,str(ROOT/"scripts/validate_portfolio.py")],check=True)
print(f"{action}: {p['id']}")
