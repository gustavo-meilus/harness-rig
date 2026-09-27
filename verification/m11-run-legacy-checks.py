#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,pathlib,shutil,subprocess,time
import os,sys,tempfile

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",required=True)
    ap.add_argument("--checks",required=True)
    ap.add_argument("--json",action="store_true")
    ns=ap.parse_args()
    repo=pathlib.Path(ns.repo).resolve()
    spec=json.loads(pathlib.Path(ns.checks).read_text())
    env=os.environ.copy()
    python_shim=None
    windows_tmp=None
    if os.name == "nt":
        windows_tmp=tempfile.TemporaryDirectory(prefix="hr-m11-tests-",dir=repo.parent)
        python_shim=windows_tmp.name
        shutil.copy2(sys.executable,pathlib.Path(python_shim)/"python3.exe")
        tmp_path=pathlib.Path(python_shim)
        drive=tmp_path.drive.rstrip(":").lower()
        env["TMPDIR"]=(f"/{drive}{tmp_path.as_posix()[len(tmp_path.drive):]}"
                       if drive else tmp_path.as_posix())
        env["PATH"] = os.pathsep.join([
            python_shim,
            r"C:\Program Files\Git\bin",
            r"C:\Program Files\Git\usr\bin",
            r"C:\Program Files\Git\mingw64\libexec\git-core",
            env.get("PATH", ""),
        ])
    results=[]
    overall="PASS"
    for check in spec.get("checks",[]):
        argv=check["argv"]
        cwd=(repo/check.get("cwd",".")).resolve()
        if repo not in [cwd,*cwd.parents]:
            results.append({"id":check["id"],"outcome":"BLOCKED","reason":"cwd-outside-repo"})
            overall="BLOCKED"; continue
        exe=shutil.which(argv[0],path=env.get("PATH"))
        if exe is None:
            outcome="BLOCKED" if check.get("required",True) else "NOT_RUN"
            results.append({"id":check["id"],"outcome":outcome,"reason":"executable-unavailable","argv":argv})
            if outcome=="BLOCKED": overall="BLOCKED"
            continue
        start=time.time()
        resolved_argv=[exe,*argv[1:]]
        p=subprocess.run(resolved_argv,cwd=cwd,env=env,text=True,capture_output=True)
        outcome="PASS" if p.returncode==0 else "FAIL"
        results.append({"id":check["id"],"outcome":outcome,"exit_code":p.returncode,
                        "argv":resolved_argv,"cwd":str(cwd.relative_to(repo)),
                        "stdout":p.stdout[-8000:],"stderr":p.stderr[-8000:],
                        "duration_ms":round((time.time()-start)*1000)})
        if outcome=="FAIL" and overall!="BLOCKED": overall="FAIL"
    report={"schema":"harness-rig/m11-legacy-check-results/v1","result":overall,"results":results}
    print(json.dumps(report,indent=2) if ns.json else overall)
    if windows_tmp is not None:
        windows_tmp.cleanup()
    return 0 if overall=="PASS" else (2 if overall=="BLOCKED" else 1)
if __name__=="__main__": raise SystemExit(main())
