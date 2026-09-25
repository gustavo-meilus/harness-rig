#!/usr/bin/env python3
"""Verify a native-Git M11 rewritten history against its source commits."""
from __future__ import annotations
import argparse, json, pathlib, subprocess

def run(repo,*args):
    p=subprocess.run(['git','-C',str(repo),*args],capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr.decode(errors='replace'))
    return p.stdout

def manifest(repo,commit):
    out=run(repo,'ls-tree','-rz','-r','--full-tree',commit); rows=[]
    for rec in out.split(b'\0'):
        if not rec: continue
        meta,path=rec.split(b'\t',1); mode,_typ,oid=meta.split(); rows.append((path,mode,oid))
    return sorted(rows)

def expected(repo,commit,prefix,includes):
    rows=[]
    for path,mode,oid in manifest(repo,commit):
        ps=path.decode('utf-8','surrogateescape')
        if includes and not any(ps==x or ps.startswith(x.rstrip('/')+'/') for x in includes): continue
        rows.append(((prefix.rstrip('/')+'/'+ps).encode('utf-8','surrogateescape'),mode,oid))
    return sorted(rows)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',required=True); ap.add_argument('--mapping',required=True)
    ap.add_argument('--prefix',required=True); ap.add_argument('--include',action='append',default=[]); ap.add_argument('--json',action='store_true')
    ns=ap.parse_args(); repo=pathlib.Path(ns.repo).resolve(); mapping=json.loads(pathlib.Path(ns.mapping).read_text())
    errors=[]
    for old,new in mapping.items():
        if expected(repo,old,ns.prefix,ns.include)!=manifest(repo,new): errors.append({'source':old,'import':new,'kind':'tree-mismatch'})
        src_par=run(repo,'show','-s','--format=%P',old).decode().strip().split(); dst_par=run(repo,'show','-s','--format=%P',new).decode().strip().split()
        exp_par=[mapping[p] for p in src_par]
        if exp_par!=dst_par: errors.append({'source':old,'import':new,'kind':'parent-mismatch','expected':exp_par,'actual':dst_par})
        for label,fmt in [('author','%an%x00%ae%x00%at%x00%ai'),('committer','%cn%x00%ce%x00%ct%x00%ci'),('message','%B')]:
            a=run(repo,'show','-s','--format='+fmt,old); b=run(repo,'show','-s','--format='+fmt,new)
            if a!=b: errors.append({'source':old,'import':new,'kind':label+'-mismatch'})
    report={'schema':'harness-rig/m11-history-rewrite-verification/v1','result':'PASS' if not errors else 'FAIL',
            'mapping_count':len(mapping),'errors':errors}
    print(json.dumps(report,indent=2) if ns.json else f"M11 rewrite verification: {report['result']} ({len(mapping)} commits)")
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
