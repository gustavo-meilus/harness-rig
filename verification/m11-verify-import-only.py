#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,pathlib,subprocess

def run(repo,*args):
    p=subprocess.run(["git","-C",str(repo),*args],capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode(errors="replace"))
    return p.stdout

def tree(repo,commit):
    rows={}
    for rec in run(repo,"ls-tree","-rz","-r","--full-tree",commit).split(b"\0"):
        if not rec: continue
        meta,path=rec.split(b"\t",1); mode,typ,oid=meta.split()
        rows[path.decode("utf-8","surrogateescape")]={"mode":mode.decode(),"type":typ.decode(),"oid":oid.decode()}
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",required=True)
    ap.add_argument("--commit",required=True)
    ap.add_argument("--allowed-prefix",action="append",required=True)
    ap.add_argument("--json",action="store_true")
    ns=ap.parse_args(); repo=pathlib.Path(ns.repo).resolve()
    parents=run(repo,"show","-s","--format=%P",ns.commit).decode().strip().split()
    errors=[]
    if len(parents)!=2:
        errors.append({"kind":"parent-count","expected":2,"actual":len(parents)})
    else:
        first, imported=parents
        changed=[x for x in run(repo,"diff-tree","-r","--name-only","--no-commit-id",first,ns.commit).decode("utf-8","surrogateescape").splitlines() if x]
        allowed=tuple(p.rstrip("/")+"/" for p in ns.allowed_prefix)
        bad=[p for p in changed if not any(p==x.rstrip("/") or p.startswith(x) for x in allowed)]
        if bad: errors.append({"kind":"outside-prefix-change","paths":bad})
        imported_tree=tree(repo,imported); merged_tree=tree(repo,ns.commit)
        mismatches=[]
        for p,v in imported_tree.items():
            if merged_tree.get(p)!=v: mismatches.append(p)
        if mismatches: errors.append({"kind":"imported-tree-not-preserved","paths":mismatches[:100]})
    report={"schema":"harness-rig/m11-import-only-verification/v1",
            "result":"PASS" if not errors else "FAIL","commit":ns.commit,"errors":errors}
    print(json.dumps(report,indent=2) if ns.json else report["result"])
    return 0 if not errors else 1
if __name__=="__main__": raise SystemExit(main())
