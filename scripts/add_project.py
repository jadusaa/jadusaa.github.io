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
required=["id","title","summary","tags","bullets","metric","metric_label","url","cta","visual_type","featured","reverse","public_safe"]
missing=[k for k in required if k not in p]
if missing:
    raise SystemExit("Missing fields: "+", ".join(missing))
if p["public_safe"] is not True:
    raise SystemExit("Refusing to publish: public_safe must be true")
if not isinstance(p["bullets"],list) or len(p["bullets"])<2:
    raise SystemExit("Need at least 2 evidence bullets")

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
