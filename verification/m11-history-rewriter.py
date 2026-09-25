#!/usr/bin/env python3
"""Rewrite a disposable source repository into a prefixed Harness Rig import history.

This is migration-only tooling. It creates new commit objects and refs in the supplied
repository; therefore use it only on a disposable clone made from a verified bundle.
It keeps one rewritten commit for every source commit reachable from the captured
source heads/tags. For filtered repositories, commits that did not touch selected paths
remain as metadata-only history events with unchanged filtered trees.
"""
from __future__ import annotations
import argparse, json, os, pathlib, re, subprocess, tempfile

def run(repo: pathlib.Path, *args: str, input_bytes: bytes|None=None, env=None) -> bytes:
    p=subprocess.run(['git','-C',str(repo),*args],input=input_bytes,capture_output=True,env=env)
    if p.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed ({p.returncode}): {p.stderr.decode(errors='replace')}")
    return p.stdout

def parse_ident(line: bytes):
    m=re.match(rb'^(.*) <([^>]*)> (\d+) ([+-]\d{4})$',line)
    if not m: raise ValueError(f'cannot parse identity line: {line!r}')
    return tuple(x.decode('utf-8','surrogateescape') for x in m.groups())

def selected(path: str, includes: list[str]) -> bool:
    if not includes: return True
    return any(path==inc or path.startswith(inc.rstrip('/') + '/') for inc in includes)

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',required=True)
    ap.add_argument('--prefix',required=True)
    ap.add_argument('--include',action='append',default=[])
    ap.add_argument('--tag-namespace',required=True)
    ap.add_argument('--output-dir',required=True)
    ns=ap.parse_args()
    repo=pathlib.Path(ns.repo).resolve(); outdir=pathlib.Path(ns.output_dir).resolve(); outdir.mkdir(parents=True,exist_ok=True)
    if not (repo/'.git').exists() and not (repo/'HEAD').exists():
        raise SystemExit('repo must be a Git work repository or bare repository')

    head_refs=run(repo,'for-each-ref','--format=%(refname)','refs/heads').decode().splitlines()
    head_refs=[r for r in head_refs if not r.startswith('refs/heads/harness-rig-import/')]
    tag_refs=run(repo,'for-each-ref','--format=%(refname)','refs/tags').decode().splitlines()
    tag_refs=[r for r in tag_refs if not r.startswith('refs/tags/'+ns.tag_namespace)]
    source_refs=head_refs+tag_refs
    if not source_refs: raise SystemExit('no source heads/tags found')

    rev_lines=run(repo,'rev-list','--reverse','--topo-order','--parents',*source_refs).decode().splitlines()
    mapping={}; signed=[]; tmp_index=pathlib.Path(tempfile.mktemp(prefix='hr-m11-index-'))
    try:
        for line in rev_lines:
            parts=line.split(); old=parts[0]; parents=parts[1:]
            raw_tree=run(repo,'ls-tree','-rz','-r','--full-tree',old)
            entries=[]
            for rec in raw_tree.split(b'\0'):
                if not rec: continue
                meta,path=rec.split(b'\t',1); mode,_typ,oid=meta.split()
                path_s=path.decode('utf-8','surrogateescape')
                if not selected(path_s,ns.include): continue
                new_path=(ns.prefix.rstrip('/')+'/'+path_s).encode('utf-8','surrogateescape')
                entries.append((new_path,mode,oid))
            env=os.environ.copy(); env['GIT_INDEX_FILE']=str(tmp_index)
            if tmp_index.exists(): tmp_index.unlink()
            run(repo,'read-tree','--empty',env=env)
            index_input=b''.join(mode+b' '+oid+b'\t'+p+b'\0' for p,mode,oid in sorted(entries))
            if index_input: run(repo,'update-index','-z','--index-info',input_bytes=index_input,env=env)
            tree=run(repo,'write-tree',env=env).decode().strip()

            raw=run(repo,'cat-file','commit',old); hdr,msg=raw.split(b'\n\n',1)
            author=committer=None
            if b'\ngpgsig ' in b'\n'+hdr: signed.append(old)
            for h in hdr.splitlines():
                if h.startswith(b'author '): author=parse_ident(h[7:])
                elif h.startswith(b'committer '): committer=parse_ident(h[10:])
            if not author or not committer: raise RuntimeError(f'missing author/committer: {old}')
            an,ae,at,atz=author; cn,ce,ct,ctz=committer
            cenv=os.environ.copy(); cenv.update({
                'GIT_AUTHOR_NAME':an,'GIT_AUTHOR_EMAIL':ae,'GIT_AUTHOR_DATE':f'@{at} {atz}',
                'GIT_COMMITTER_NAME':cn,'GIT_COMMITTER_EMAIL':ce,'GIT_COMMITTER_DATE':f'@{ct} {ctz}',
            })
            args=['commit-tree',tree]
            for parent in parents: args += ['-p',mapping[parent]]
            new=run(repo,*args,input_bytes=msg,env=cenv).decode().strip(); mapping[old]=new

        refmap=[]
        for ref in head_refs:
            short=ref.removeprefix('refs/heads/'); old=run(repo,'rev-parse',ref).decode().strip(); new=mapping[old]
            newref='refs/heads/harness-rig-import/'+short
            run(repo,'update-ref',newref,new)
            refmap.append({'source_ref':ref,'source_commit':old,'import_ref':newref,'import_commit':new})

        tagmap=[]
        for ref in tag_refs:
            short=ref.removeprefix('refs/tags/')
            source_obj=run(repo,'rev-parse',ref).decode().strip()
            peeled=run(repo,'rev-parse',ref+'^{commit}').decode().strip(); new=mapping[peeled]
            newref='refs/tags/'+ns.tag_namespace+short
            run(repo,'update-ref',newref,new)
            tagmap.append({'source_ref':ref,'source_object':source_obj,'source_commit':peeled,
                           'import_ref':newref,'import_commit':new,'annotation_preserved':False})

        (outdir/'commit-map.json').write_text(json.dumps(mapping,indent=2,sort_keys=True)+'\n')
        (outdir/'ref-map.json').write_text(json.dumps(refmap,indent=2)+'\n')
        (outdir/'tag-map.json').write_text(json.dumps(tagmap,indent=2)+'\n')
        report={'schema':'harness-rig/m11-history-rewrite-report/v1','prefix':ns.prefix,'includes':ns.include,
                'source_commit_count':len(mapping),'branch_count':len(head_refs),'tag_count':len(tag_refs),
                'signed_source_commits':signed,'signed_commit_signatures_preserved':False,
                'tag_annotations_preserved':False,
                'note':'Rewritten commit IDs intentionally differ; commit-map.json is authoritative.'}
        (outdir/'rewrite-report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report))
        return 0
    finally:
        if tmp_index.exists(): tmp_index.unlink()

if __name__=='__main__': raise SystemExit(main())
