#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,pathlib,shutil,subprocess,time

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",required=True)
    ap.add_argument("--checks",required=True)
    ap.add_argument("--json",action="store_true")
    ns=ap.parse_args()
    repo=pathlib.Path(ns.repo).resolve()
    spec=json.loads(pathlib.Path(ns.checks).read_text())
    results=[]
    overall="PASS"
    for check in spec.get("checks",[]):
        argv=check["argv"]
        cwd=(repo/check.get("cwd",".")).resolve()
        if repo not in [cwd,*cwd.parents]:
            results.append({"id":check["id"],"outcome":"BLOCKED","reason":"cwd-outside-repo"})
            overall="BLOCKED"; continue
        exe=shutil.which(argv[0])
        if exe is None:
            outcome="BLOCKED" if check.get("required",True) else "NOT_RUN"
            results.append({"id":check["id"],"outcome":outcome,"reason":"executable-unavailable","argv":argv})
            if outcome=="BLOCKED": overall="BLOCKED"
            continue
        start=time.time()
        p=subprocess.run(argv,cwd=cwd,text=True,capture_output=True)
        outcome="PASS" if p.returncode==0 else "FAIL"
        results.append({"id":check["id"],"outcome":outcome,"exit_code":p.returncode,
                        "argv":argv,"cwd":str(cwd.relative_to(repo)),
                        "stdout":p.stdout[-8000:],"stderr":p.stderr[-8000:],
                        "duration_ms":round((time.time()-start)*1000)})
        if outcome=="FAIL" and overall!="BLOCKED": overall="FAIL"
    report={"schema":"harness-rig/m11-legacy-check-results/v1","result":overall,"results":results}
    print(json.dumps(report,indent=2) if ns.json else overall)
    return 0 if overall=="PASS" else (2 if overall=="BLOCKED" else 1)
if __name__=="__main__": raise SystemExit(main())
