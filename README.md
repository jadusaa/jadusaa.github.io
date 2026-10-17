# Jawad Sabir — Automation Portfolio

Single-page static portfolio with a data-driven project section and a safe Hermes auto-update workflow.

## Structure
- `index.html` — deployable site output
- `template.html` — visual template with `AUTO_PROJECTS` markers
- `portfolio.json` — source of truth for public project cards
- `scripts/build_portfolio.py` — rebuilds project section
- `scripts/add_project.py` — adds/updates a verified manifest then rebuilds
- `scripts/validate_portfolio.py` — blocks weak positioning and obvious private/secret data
- `manifests/EXAMPLE_PROJECT.json` — future project schema
- `HERMES_PORTFOLIO_AUTOMATION.md` — reusable Hermes closeout rule

## Rebuild
```bash
cd ~/PORTFOLIO_SITE
python3 scripts/build_portfolio.py
python3 scripts/validate_portfolio.py
```

## Add/update a project
```bash
python3 scripts/add_project.py --manifest /path/to/project_manifest.json
```

Project IDs are stable. If the ID already exists, it is updated instead of duplicated.

## Positioning rule
The site uses confident factual language. It does not advertise lack of client history. Project-specific demo/synthetic-data disclosures belong in the underlying project evidence when relevant.

## Deployment
Connect this directory to an authorized GitHub Pages repository. After a validated project update, Hermes can commit/push automatically only when the remote already exists and publishing that project is clearly authorized/public-safe.
