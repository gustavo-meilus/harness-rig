#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,pathlib,subprocess,tempfile
SOURCES=[
 {"id":"aiboarding","filename":"aiboarding.bundle","required_ref":"refs/heads/main","required_paths":[]},
 {"id":"tacticswitch","filename":"tacticswitch.bundle","required_ref":"refs/heads/main","required_paths":[]},
 {"id":"skill-kit","filename":"skill-kit.bundle","required_ref":"refs/heads/main","required_paths":["plugins/llm-knowledge-base-maintainer","plugins/engineering-harness-adaptive"]},
]
def run(args):
 p=subprocess.run(args,text=True,capture_output=True); return p.returncode,p.stdout,p.stderr
def bundle(spec,path):
 item={"source":spec["id"],"path":str(path),"kind":"bundle","ok":False}
 rc,out,err=run(["git","bundle","list-heads",str(path)])
 item["list_heads_exit"]=rc
 if rc: item["reason"]="list-heads-failed"; item["stderr"]=err.strip(); return item
 refs=[]
 for line in out.splitlines():
  if line.strip():
   oid,ref=line.split(None,1); refs.append({"oid":oid,"ref":ref})
 item["refs"]=refs
 if spec["required_ref"] not in {x["ref"] for x in refs}: item["reason"]="missing-required-ref"; return item
 with tempfile.TemporaryDirectory(prefix="hr-m11-preflight-") as td:
  repo=pathlib.Path(td)/"repo.git"
  rc,_,err=run(["git","clone","--mirror",str(path),str(repo)])
  if rc: item["reason"]="mirror-clone-failed"; item["stderr"]=err.strip(); return item
  rc,_,err=run(["git","-C",str(repo),"fsck","--full"])
  if rc: item["reason"]="fsck-failed"; item["stderr"]=err.strip(); return item
  rc,out,_=run(["git","-C",str(repo),"rev-list","--count",spec["required_ref"]])
  item["main_commit_count"]=int(out.strip()) if rc==0 and out.strip().isdigit() else None
  if not item["main_commit_count"]: item["reason"]="main-has-no-commits"; return item
  missing=[]
  for rp in spec["required_paths"]:
   rc,_,_=run(["git","-C",str(repo),"cat-file","-e",f"{spec['required_ref']}:{rp}"])
   if rc: missing.append(rp)
  item["missing_required_paths"]=missing
  if missing: item["reason"]="missing-required-paths"; return item
 item["ok"]=True; return item
def repo(spec,path):
 item={"source":spec["id"],"path":str(path),"kind":"repository","ok":False}
 rc,_,err=run(["git","-C",str(path),"fsck","--full"])
 if rc: item["reason"]="fsck-failed"; item["stderr"]=err.strip(); return item
 rc,_,_=run(["git","-C",str(path),"show-ref","--verify",spec["required_ref"]])
 if rc: item["reason"]="missing-required-ref"; return item
 rc,out,_=run(["git","-C",str(path),"rev-list","--count",spec["required_ref"]])
 item["main_commit_count"]=int(out.strip()) if rc==0 and out.strip().isdigit() else None
 if not item["main_commit_count"]: item["reason"]="main-has-no-commits"; return item
 missing=[]
 for rp in spec["required_paths"]:
  rc,_,_=run(["git","-C",str(path),"cat-file","-e",f"{spec['required_ref']}:{rp}"])
  if rc: missing.append(rp)
 item["missing_required_paths"]=missing
 if missing: item["reason"]="missing-required-paths"; return item
 item["ok"]=True; return item
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--dir",default="."); ap.add_argument("--json",action="store_true"); ns=ap.parse_args()
 base=pathlib.Path(ns.dir).resolve(); report={"schema":"harness-rig/m11-history-input-preflight/v2","base":str(base),"sources":[],"result":"PASS"}
 for spec in SOURCES:
  p=base/spec["filename"]
  if not p.exists(): item={"source":spec["id"],"expected":str(p),"ok":False,"reason":"missing"}
  elif p.is_file(): item=bundle(spec,p)
  else: item=repo(spec,p)
  report["sources"].append(item)
  if not item.get("ok"): report["result"]="BLOCKED"
 print(json.dumps(report,indent=2) if ns.json else report["result"])
 return 0 if report["result"]=="PASS" else 2
if __name__=="__main__": raise SystemExit(main())
