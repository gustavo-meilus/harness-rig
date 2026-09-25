#!/usr/bin/env python3
import argparse,pathlib,subprocess,json
def run(args):
 p=subprocess.run(args,text=True,capture_output=True)
 if p.returncode: raise RuntimeError(p.stderr)
 return p.stdout
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--target-repo",required=True); ap.add_argument("--imports-dir",required=True); ns=ap.parse_args()
 repo=pathlib.Path(ns.target_repo).resolve(); imports=pathlib.Path(ns.imports_dir).resolve(); out={"schema":"harness-rig/m11-target-fetch/v1","result":"PASS","sources":[]}
 for s in ["aiboarding","tacticswitch","skill-kit"]:
  b=imports/s/f"{s}-import.bundle"; prefix=f"refs/remotes/m11-import/{s}"
  run(["git","-C",str(repo),"fetch",str(b),f"refs/heads/harness-rig-import/*:{prefix}/*",f"refs/tags/{s}/*:refs/tags/{s}/*"])
  refs=run(["git","-C",str(repo),"for-each-ref","--format=%(refname)",prefix]).splitlines()
  out["sources"].append({"id":s,"remote_refs":refs})
 print(json.dumps(out,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
