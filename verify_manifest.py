#!/usr/bin/env python3
"""Validate package manifest, schema, file metadata, and manifest.sha256.

CI exit codes:
  0  PASS
  10 manifest.json missing
  11 manifest schema missing
  12 JSON syntax error
  13 schema validation failed
  20 file_count mismatch
  21 listed file missing
  22 unlisted file found in --strict mode
  30 file size mismatch
  31 listed file SHA-256 mismatch
  32 manifest.sha256 missing or mismatch
  40 corrupt ZIP
  50 runtime/internal error
"""
from __future__ import annotations
import argparse, hashlib, json, sys, tempfile, zipfile
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

EXIT = {"PASS":0,"MANIFEST_MISSING":10,"SCHEMA_MISSING":11,"JSON_ERROR":12,"SCHEMA_FAIL":13,"COUNT_FAIL":20,"FILE_MISSING":21,"UNLISTED":22,"SIZE_FAIL":30,"HASH_FAIL":31,"MANIFEST_HASH_FAIL":32,"ZIP_FAIL":40,"INTERNAL":50}

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def locate(path: Path):
    if path.is_dir(): return path,None,None
    if path.suffix.lower()!='.zip': raise ValueError('Input must be package directory or ZIP')
    tmp=tempfile.TemporaryDirectory(prefix='bwctg_verify_')
    try:
        with zipfile.ZipFile(path) as z:
            bad=z.testzip()
            if bad: return None,tmp,f'Corrupt ZIP member: {bad}'
            z.extractall(tmp.name)
    except zipfile.BadZipFile as e: return None,tmp,str(e)
    manifests=list(Path(tmp.name).rglob('manifest.json'))
    if len(manifests)!=1: raise ValueError(f'Expected one manifest.json, found {len(manifests)}')
    return manifests[0].parent,tmp,None

def parse_manifest_sha(path: Path):
    text=path.read_text(encoding='utf-8').strip()
    parts=text.split()
    if len(parts)<2 or len(parts[0])!=64: raise ValueError('Invalid manifest.sha256 format')
    return parts[0].lower(),parts[-1].lstrip('*')

def verify(package: Path, strict: bool):
    report={"tool":"verify_manifest.py","tool_version":"2.0.0","input":str(package.resolve()),"strict":strict,"checks":{"zip_integrity":"NOT_APPLICABLE","manifest_json":"NOT_RUN","manifest_checksum":"NOT_RUN","schema":"NOT_RUN","file_count":"NOT_RUN","files":"NOT_RUN"},"summary":{"total":0,"passed":0,"failed":0},"failed_files":[],"files":[],"warnings":[],"errors":[],"result":"FAIL","exit_code":50}
    tmp=None
    try:
        root,tmp,zip_error=locate(package.resolve())
        if zip_error:
            report['checks']['zip_integrity']='FAIL'; report['errors'].append(zip_error); report['exit_code']=40; return report
        if package.suffix.lower()=='.zip': report['checks']['zip_integrity']='PASS'
        report['package_name']=root.name
        mp=root/'manifest.json'; sp=root/'Documentation'/'manifest.schema.json'; hp=root/'Documentation'/'manifest.sha256'
        if not mp.is_file(): report['errors'].append('Missing manifest.json'); report['exit_code']=10; return report
        if not sp.is_file(): report['errors'].append('Missing manifest.schema.json'); report['exit_code']=11; return report
        try:
            manifest=json.loads(mp.read_text(encoding='utf-8')); schema=json.loads(sp.read_text(encoding='utf-8')); report['checks']['manifest_json']='PASS'
        except json.JSONDecodeError as e:
            report['checks']['manifest_json']='FAIL'; report['errors'].append(str(e)); report['exit_code']=12; return report
        if not hp.is_file():
            report['checks']['manifest_checksum']='FAIL'; report['errors'].append('Missing Documentation/manifest.sha256'); report['exit_code']=32; return report
        expected,name=parse_manifest_sha(hp); actual=sha256(mp)
        if name!='manifest.json' or expected!=actual:
            report['checks']['manifest_checksum']='FAIL'; report['errors'].append(f'manifest SHA-256 mismatch expected={expected} actual={actual}'); report['exit_code']=32; return report
        report['checks']['manifest_checksum']='PASS'
        Draft202012Validator.check_schema(schema)
        serr=list(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(manifest))
        if serr:
            report['checks']['schema']='FAIL'; report['errors'] += [f"Schema [{'/'.join(map(str,e.absolute_path)) or '$'}]: {e.message}" for e in serr]; report['exit_code']=13; return report
        report['checks']['schema']='PASS'
        entries=manifest.get('files',[]); report['summary']['total']=len(entries)
        if manifest.get('file_count')!=len(entries):
            report['checks']['file_count']='FAIL'; report['errors'].append('file_count mismatch'); report['exit_code']=20; return report
        report['checks']['file_count']='PASS'
        listed=set(); first_failure=None
        for item in entries:
            rel=item['path']; listed.add(rel); p=root/rel; detail={"path":rel,"exists":p.is_file(),"size":"NOT_RUN","sha256":"NOT_RUN"}
            if not p.is_file():
                detail['error_type']='file_missing'; report['failed_files'].append(detail); first_failure=first_failure or 21; report['files'].append(detail); continue
            size=p.stat().st_size; digest=sha256(p); detail.update({"expected_size_bytes":item['size_bytes'],"actual_size_bytes":size,"size":"PASS" if size==item['size_bytes'] else "FAIL","expected_sha256":item['sha256'],"actual_sha256":digest,"sha256":"PASS" if digest==item['sha256'] else "FAIL"})
            if detail['size']=='FAIL': detail['error_type']='size_mismatch'; report['failed_files'].append(detail); first_failure=first_failure or 30
            elif detail['sha256']=='FAIL': detail['error_type']='sha256_mismatch'; report['failed_files'].append(detail); first_failure=first_failure or 31
            else: report['summary']['passed']+=1
            report['files'].append(detail)
        report['summary']['failed']=len(report['failed_files'])
        allowed_unlisted={'manifest.json','Documentation/manifest.sha256'}
        actual_files={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc' and not p.name.endswith(('.artifactvalidatepass','.artifactvalidatefixed','.tmp','.bak','.orig'))}
        unlisted=sorted(actual_files-listed-allowed_unlisted)
        if unlisted:
            msg='Unlisted files: '+', '.join(unlisted)
            if strict: report['errors'].append(msg); first_failure=first_failure or 22
            else: report['warnings'].append(msg)
        report['checks']['files']='PASS' if not first_failure else 'FAIL'
        if first_failure:
            report['exit_code']=first_failure; return report
        report['result']='PASS'; report['exit_code']=0; return report
    except Exception as e:
        report['errors'].append(f'{type(e).__name__}: {e}'); report['exit_code']=50; return report
    finally:
        if tmp: tmp.cleanup()

def emit(report,as_json):
    if as_json: print(json.dumps(report,ensure_ascii=False,indent=2)); return
    print(f"Package: {report.get('package_name','unknown')}")
    for k,v in report['checks'].items(): print(f"{k}: {v}")
    for e in report['errors']: print('ERROR:',e,file=sys.stderr)
    print(f"RESULT: {report['result']} (exit {report['exit_code']})")

def main():
    p=argparse.ArgumentParser(); p.add_argument('package',type=Path); p.add_argument('--strict',action='store_true'); p.add_argument('--json',action='store_true',dest='json_output'); p.add_argument('--show-exit-codes',action='store_true')
    a=p.parse_args()
    if a.show_exit_codes:
        print(json.dumps(EXIT,indent=2)); return 0
    report=verify(a.package,a.strict); emit(report,a.json_output); return report['exit_code']
if __name__=='__main__': raise SystemExit(main())
