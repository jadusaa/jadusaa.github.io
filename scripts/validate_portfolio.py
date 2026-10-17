#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT/"index.html", ROOT/"portfolio.json"]
forbidden_phrases = [
    "i'm early on client work", "i’m early on client work", "early in client work",
    "not client work yet", "paid pilots welcome", "new to n8n", "beginner",
    "give me a chance", "trying to break in", "learning n8n", "aspiring",
    "junior automation developer", "first client"
]
secret_patterns = [
    r"sk-[A-Za-z0-9_-]{16,}", r"Bearer\s+[A-Za-z0-9._-]{16,}",
    r"gmail_token\.json", r"gmail_client_secret\.json", r"/Users/[^\s<\"]+",
    r"tailscale\.com/[A-Za-z0-9._/?=&%-]+", r"tailnet",
    r"192\.168\.\d+\.\d+", r"127\.0\.0\.1:\d+",
    r"gh[pousr]_[A-Za-z0-9]{20,}", r"xox[bap]-[A-Za-z0-9-]+",
    r"ans-mac-mini", r"taila8a8d9", r"webhook[_-]?secret",
    r"n8n[_-]?api[_-]?key", r"client_secret=[A-Za-z0-9]"
]
errors=[]
text="\n".join(p.read_text(encoding="utf-8") for p in FILES if p.exists())
low=text.lower()
for phrase in forbidden_phrases:
    if phrase in low:
        errors.append(f"forbidden weak-positioning phrase: {phrase}")
for pat in secret_patterns:
    if re.search(pat, text, re.I):
        errors.append(f"private/secret pattern found: {pat}")
try:
    data=json.loads((ROOT/"portfolio.json").read_text(encoding="utf-8"))
    ids=[]
    for p in data.get("projects",[]):
        for k in ("id","title","summary","public_safe"):
            if k not in p: errors.append(f"project missing {k}: {p.get('id','?')}")
        if p.get("id") in ids: errors.append(f"duplicate project id: {p.get('id')}")
        ids.append(p.get("id"))
        if p.get("public_safe") is not True:
            errors.append(f"project not explicitly public_safe: {p.get('id')}")
        # case-study fields (optional but must be lists/str when present)
        for k in ("problem","build","reliability","proof","tech","links","media","one_liner","flow"):
            if k in p and p[k] is None:
                errors.append(f"case-study field {k} is null: {p.get('id')}")
        for k in ("reliability","tech","links","media"):
            if k in p and not isinstance(p[k], list):
                errors.append(f"case-study field {k} must be a list: {p.get('id')}")
        # opportunity engine privacy invariant: no github repo link on private projects
        if p.get("visibility") == "private":
            for l in p.get("links", []):
                if "github.com" in l.get("url",""):
                    errors.append(f"private project links to github (must stay private): {p.get('id')}")
except Exception as e:
    errors.append(f"portfolio.json invalid: {e}")
if errors:
    print("VALIDATION FAIL")
    for e in errors: print("-", e)
    sys.exit(1)
print("VALIDATION PASS")
