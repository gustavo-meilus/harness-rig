#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, shutil, subprocess, sys, tempfile

HERE=pathlib.Path(__file__).resolve().parent

def run(args):
    p=subprocess.run(args,text=True,capture_output=True)
    if p.returncode:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(map(str,args))}\n{p.stderr}")
    return p

def load_json(path):
    return json.loads(path.read_text())

def semantic_bundle_refs(bundle):
    p=run(["git","bundle","list-heads",str(bundle)])
    rows=[]
    for line in p.stdout.splitlines():
        if line.strip():
            oid,ref=line.split(None,1)
            rows.append({"oid":oid,"ref":ref})
    return sorted(rows,key=lambda x:x["ref"])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--inputs-dir",required=True)
    ap.add_argument("--json",action="store_true")
    ns=ap.parse_args()
    inputs=pathlib.Path(ns.inputs_dir).resolve()
    with tempfile.TemporaryDirectory(prefix="hr-m11-repro-") as td:
        td=pathlib.Path(td)
        runs=[]
        for i in [1,2]:
            work=td/f"work{i}"; out=td/f"out{i}"
            p=run([sys.executable,"-S",str(HERE/"m11-run-history-imports.py"),
                   "--inputs-dir",str(inputs),"--work-dir",str(work),"--output-dir",str(out)])
            summary=json.loads(p.stdout)
            runs.append((out,summary))
        errors=[]
        for source in ["aiboarding","tacticswitch","skill-kit"]:
            a=runs[0][0]/source; b=runs[1][0]/source
            for fname in ["commit-map.json","ref-map.json","tag-map.json","rewrite-report.json","verify-report.json"]:
                if load_json(a/fname)!=load_json(b/fname):
                    errors.append({"source":source,"kind":"json-mismatch","file":fname})
            ba=a/f"{source}-import.bundle"; bb=b/f"{source}-import.bundle"
            if semantic_bundle_refs(ba)!=semantic_bundle_refs(bb):
                errors.append({"source":source,"kind":"bundle-ref-mismatch"})
        result={"schema":"harness-rig/m11-reproducibility-verification/v1",
                "result":"PASS" if not errors else "FAIL","errors":errors}
        print(json.dumps(result,indent=2) if ns.json else result["result"])
        return 0 if not errors else 1
if __name__=="__main__": raise SystemExit(main())
