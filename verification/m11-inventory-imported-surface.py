#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,pathlib,re,subprocess

CATEGORIES={
 "licenses":[r"(^|/)(LICENSE|LICENSE\..*|NOTICE|NOTICE\..*)$"],
 "state":[r"(^|/)\.aiboarding(/|$)",r"state\.json$",r"capabilit"],
 "hooks":[r"(^|/)hooks?(/|$)",r"hook"],
 "host_plugin_manifests":[r"plugin\.json$",r"marketplace\.json$",r"manifest\.json$",r"\.claude-plugin/",r"\.codex"],
 "install_update":[r"(^|/)scripts?/(install|verify_install|migrat|updat)",r"(^|/)INSTALL\.md$"],
 "generated_distribution":[r"(^|/)(templates?|dist|generated)(/|$)",r"MANIFEST\.sha256$"],
 "schemas_contracts":[r"schema",r"contract",r"protocol"],
 "tests_evals":[r"(^|/)(tests?|benchmarks?|fixtures?)(/|$)"],
 "ci":[r"(^|/)\.github/workflows(/|$)"],
 "openspec":[r"(^|/)openspec(/|$)"],
 "agent_roles":[r"(^|/)(agents?|skills?)(/|$)",r"AGENTS\.md$",r"CLAUDE\.md$"],
}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",required=True)
    ap.add_argument("--commit",required=True)
    ap.add_argument("--prefix",required=True)
    ap.add_argument("--json",action="store_true")
    ns=ap.parse_args(); repo=pathlib.Path(ns.repo).resolve(); prefix=ns.prefix.rstrip("/")+"/"
    p=subprocess.run(["git","-C",str(repo),"ls-tree","-r","--name-only",ns.commit,prefix],text=True,capture_output=True)
    if p.returncode: raise SystemExit(p.stderr)
    paths=[x for x in p.stdout.splitlines() if x]
    cats={k:[] for k in CATEGORIES}
    for path in paths:
        rel=path[len(prefix):] if path.startswith(prefix) else path
        for cat,pats in CATEGORIES.items():
            if any(re.search(pt,rel,re.I) for pt in pats):
                cats[cat].append(rel)
    report={"schema":"harness-rig/m11-imported-surface-inventory/v1","prefix":ns.prefix,
            "path_count":len(paths),"categories":cats,"all_paths":[p[len(prefix):] if p.startswith(prefix) else p for p in paths]}
    print(json.dumps(report,indent=2) if ns.json else f"{len(paths)} paths")
    return 0
if __name__=="__main__": raise SystemExit(main())
