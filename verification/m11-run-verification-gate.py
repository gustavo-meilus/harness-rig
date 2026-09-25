#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,pathlib,subprocess,sys
HERE=pathlib.Path(__file__).resolve().parent

def call(args):
    p=subprocess.run(args,text=True,capture_output=True)
    obj=None
    try: obj=json.loads(p.stdout)
    except Exception: obj={"stdout":p.stdout,"stderr":p.stderr}
    return p.returncode,obj

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--inputs-dir",required=True)
    ap.add_argument("--target-repo",required=True)
    ap.add_argument("--import-commits",required=True,help="JSON mapping source -> import merge commit")
    ap.add_argument("--legacy-checks",required=True,help="JSON mapping source -> checks spec path")
    ap.add_argument("--json",action="store_true")
    ns=ap.parse_args()
    commits=json.loads(pathlib.Path(ns.import_commits).read_text())
    checks=json.loads(pathlib.Path(ns.legacy_checks).read_text())
    report={"schema":"harness-rig/m11-verification-gate/v1","result":"PASS","checks":{}}
    rc,obj=call([sys.executable,"-S",str(HERE/"m11-verify-reproducibility.py"),"--inputs-dir",ns.inputs_dir,"--json"])
    report["checks"]["M11-V01"]={"exit":rc,"evidence":obj}
    if rc: report["result"]="FAIL"
    # V02 legacy checks for each imported source/worktree path supplied by checks mapping.
    v02=[]
    for source,spec in checks.items():
        rc2,obj2=call([sys.executable,"-S",str(HERE/"m11-run-legacy-checks.py"),
                       "--repo",spec["repo"],"--checks",spec["checks"],"--json"])
        v02.append({"source":source,"exit":rc2,"evidence":obj2})
        if rc2: report["result"]="FAIL" if rc2==1 else "BLOCKED"
    report["checks"]["M11-V02"]=v02
    # V03 import-only
    v03=[]
    prefixes={"aiboarding":"legacy/aiboarding","tacticswitch":"legacy/tacticswitch","skill-kit":"legacy/skill-kit"}
    for source,commit in commits.items():
        rc3,obj3=call([sys.executable,"-S",str(HERE/"m11-verify-import-only.py"),
                       "--repo",ns.target_repo,"--commit",commit,
                       "--allowed-prefix",prefixes[source],"--json"])
        v03.append({"source":source,"exit":rc3,"evidence":obj3})
        if rc3: report["result"]="FAIL"
    report["checks"]["M11-V03"]=v03
    # V04 surface inventory
    v04=[]
    for source,commit in commits.items():
        rc4,obj4=call([sys.executable,"-S",str(HERE/"m11-inventory-imported-surface.py"),
                       "--repo",ns.target_repo,"--commit",commit,
                       "--prefix",prefixes[source],"--json"])
        v04.append({"source":source,"exit":rc4,"evidence":obj4})
        if rc4: report["result"]="FAIL"
    report["checks"]["M11-V04"]=v04
    print(json.dumps(report,indent=2) if ns.json else report["result"])
    return 0 if report["result"]=="PASS" else (2 if report["result"]=="BLOCKED" else 1)
if __name__=="__main__": raise SystemExit(main())
