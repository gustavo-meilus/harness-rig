#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,pathlib,subprocess,sys,shutil,hashlib,tempfile
SOURCES=[
 {"id":"aiboarding","bundle":"aiboarding.bundle","prefix":"legacy/aiboarding","tag_namespace":"aiboarding/","includes":[]},
 {"id":"tacticswitch","bundle":"tacticswitch.bundle","prefix":"legacy/tacticswitch","tag_namespace":"tacticswitch/","includes":[]},
 {"id":"skill-kit","bundle":"skill-kit.bundle","prefix":"legacy/skill-kit","tag_namespace":"skill-kit/","includes":["plugins/llm-knowledge-base-maintainer","plugins/engineering-harness-adaptive","LICENSE"]},
]
HERE=pathlib.Path(__file__).resolve().parent
def run(args):
 p=subprocess.run(args,text=True,capture_output=True)
 if p.returncode: raise RuntimeError(f"command failed ({p.returncode}): {' '.join(map(str,args))}\n{p.stderr}")
 return p
def verify_bundle(path):
 with tempfile.TemporaryDirectory(prefix="hr-m11-bundle-") as td:
  repo=pathlib.Path(td)/"r.git"
  run(["git","clone","--mirror",str(path),str(repo)])
  run(["git","-C",str(repo),"fsck","--full"])
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--inputs-dir",required=True); ap.add_argument("--work-dir",required=True); ap.add_argument("--output-dir",required=True); ns=ap.parse_args()
 inputs=pathlib.Path(ns.inputs_dir).resolve(); work=pathlib.Path(ns.work_dir).resolve(); output=pathlib.Path(ns.output_dir).resolve()
 if work.exists(): shutil.rmtree(work)
 work.mkdir(parents=True); output.mkdir(parents=True,exist_ok=True)
 pre=json.loads(run([sys.executable,"-S",str(HERE/"m11-history-input-preflight.py"),"--dir",str(inputs),"--json"]).stdout)
 summary={"schema":"harness-rig/m11-import-run-summary/v1","result":"PASS","preflight":pre,"sources":[]}
 for spec in SOURCES:
  repo=work/f"{spec['id']}.git"; run(["git","clone","--mirror",str(inputs/spec["bundle"]),str(repo)])
  out=output/spec["id"]; out.mkdir(parents=True,exist_ok=True)
  cmd=[sys.executable,"-S",str(HERE/"m11-history-rewriter.py"),"--repo",str(repo),"--prefix",spec["prefix"],"--tag-namespace",spec["tag_namespace"],"--output-dir",str(out)]
  for inc in spec["includes"]: cmd+=["--include",inc]
  rw=json.loads(run(cmd).stdout)
  cmd=[sys.executable,"-S",str(HERE/"m11-verify-rewrite.py"),"--repo",str(repo),"--mapping",str(out/"commit-map.json"),"--prefix",spec["prefix"],"--json"]
  for inc in spec["includes"]: cmd+=["--include",inc]
  vv=json.loads(run(cmd).stdout); (out/"verify-report.json").write_text(json.dumps(vv,indent=2)+"\n")
  refs=run(["git","-C",str(repo),"for-each-ref","--format=%(refname)","refs/heads/harness-rig-import/","refs/tags/"+spec["tag_namespace"]]).stdout.splitlines()
  refs=[r for r in refs if r]
  bundle=out/f"{spec['id']}-import.bundle"; run(["git","-C",str(repo),"bundle","create",str(bundle),*refs]); verify_bundle(bundle)
  summary["sources"].append({"id":spec["id"],"rewrite_report":rw,"verify_report":vv,"rewritten_refs":refs,"import_bundle":str(bundle),"import_bundle_sha256":hashlib.sha256(bundle.read_bytes()).hexdigest(),"bundle_verify":"PASS-by-clone-fsck"})
 (output/"m11-import-run-summary.json").write_text(json.dumps(summary,indent=2)+"\n"); print(json.dumps(summary)); return 0
if __name__=="__main__": raise SystemExit(main())
