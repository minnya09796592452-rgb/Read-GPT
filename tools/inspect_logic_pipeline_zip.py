#!/usr/bin/env python3
import hashlib,json,re,zipfile
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath
ROOT=Path.cwd(); ARCHIVE=ROOT/'reports/NYAMIST_LOGIC_PARTS_DETAILED_20261115.zip'; OUT=ROOT/'reports'; OUT.mkdir(exist_ok=True)
PHASES=[('1. Full Logic Mapping',['import','function','class','dependency','control flow','ceto','fourier','shader','ocean','pinvoke','unitypy']),('2. APK Editor Architecture Mapping',['apk','android','jni','native','vulkan','render loop','surface','editor','engine']),('3. Compatibility and Bridge Design',['adapter','bridge','compatib','interface','descriptor','buffer','texture','shader','lifecycle','synchronization']),('4. Full Logic Integration',['integration','pipeline','scheduler','render','fourier','fft','mesh','scene','gameplay','physics','buoyancy']),('5. Testing, Optimization & Final APK',['test','validation','pass','fail','performance','device','driver','build','apk','runtime','sha256','crc'])]
def sha(b): return hashlib.sha256(b).hexdigest()
def main():
 if not ARCHIVE.is_file(): raise SystemExit('Missing archive: '+str(ARCHIVE))
 raw=ARCHIVE.read_bytes(); data={'generated_utc':datetime.now(timezone.utc).isoformat(),'archive':ARCHIVE.name,'archive_bytes':len(raw),'archive_sha256':sha(raw),'entries':0,'txt_files':[],'non_txt_files':[],'duplicate_basenames':{},'unsafe_paths':[],'crc_error':None,'phase_evidence':[],'limitations':['These are AST-generated static summaries, not original source files.','Keyword matches are evidence pointers only, not proof of execution or integration.','APK runtime, Vulkan pipeline compatibility and target-device behavior remain unverified.']}
 with zipfile.ZipFile(ARCHIVE) as z:
  infos=z.infolist(); data['entries']=len(infos); data['crc_error']=z.testzip(); stems=Counter(); texts=[]
  for i in infos:
   p=PurePosixPath(i.filename)
   if p.is_absolute() or '..' in p.parts: data['unsafe_paths'].append(i.filename); continue
   if i.is_dir(): continue
   b=z.read(i)
   if p.suffix.lower()=='.txt':
    t=b.decode('utf-8-sig',errors='replace'); stems[p.stem.lower()]+=1; texts.append((i.filename,t)); data['txt_files'].append({'path':i.filename,'bytes':len(b),'lines':len(t.splitlines()),'sha256':sha(b),'excerpt':bool(re.search('excerpt',t,re.I)),'limitation_notice':bool(re.search('static analysis|not executed|runtime.*not',t,re.I))})
   else: data['non_txt_files'].append({'path':i.filename,'bytes':len(b)})
  data['duplicate_basenames']={k:v for k,v in stems.items() if v>1}; alltext='\n'.join(t for _,t in texts).lower()
  for phase,terms in PHASES:
   hits=[x for x in terms if x in alltext]; data['phase_evidence'].append({'phase':phase,'matched_topics':hits,'status':'PARTIAL — static summary references only; source/runtime verification required'})
 md=['# Detailed Logic ZIP — Five-Phase Pipeline Inspection','',f"- Generated UTC: {data['generated_utc']}",f"- Archive SHA-256: `{data['archive_sha256']}`",f"- Archive entries: {data['entries']}",f"- TXT files inspected: {len(data['txt_files'])}",f"- Non-TXT files: {len(data['non_txt_files'])}",f"- CRC: {'PASS' if data['crc_error'] is None else 'FAIL '+str(data['crc_error'])}",f"- Unsafe paths: {len(data['unsafe_paths'])}",f"- Duplicate basenames: {len(data['duplicate_basenames'])}",'','## Five-phase comparison','']
 for p in data['phase_evidence']: md += ['### '+p['phase'],'- Status: **'+p['status']+'**','- Matched topics: '+(', '.join(p['matched_topics']) or 'none'),'']
 md += ['## TXT inventory','','| File | Bytes | Lines | SHA-256 | Excerpt | Limitation notice |','|---|---:|---:|---|---|---|']
 for x in data['txt_files']: md.append(f"| `{x['path']}` | {x['bytes']} | {x['lines']} | `{x['sha256']}` | {x['excerpt']} | {x['limitation_notice']} |")
 if data['duplicate_basenames']: md += ['','## Duplicate basenames']+[f'- {k}: {v}' for k,v in data['duplicate_basenames'].items()]
 md += ['','## Full TXT report contents','']
 for n,t in texts: md += ['### `'+n+'`','','~~~text',t.rstrip(),'~~~','']
 md += ['## Conclusion','', 'This archive contains static-analysis summaries. It can inform Phase 1 and provide leads for Phases 2–5, but it does not prove APK architecture mapping, bridge design, full integration, successful builds, or runtime tests.','']+['- '+x for x in data['limitations']]
 (OUT/'logic_pipeline_inspection.md').write_text('\n'.join(md)+'\n',encoding='utf-8'); (OUT/'logic_pipeline_inspection.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print(json.dumps({'entries':data['entries'],'txt_count':len(data['txt_files']),'non_txt_count':len(data['non_txt_files']),'crc':data['crc_error'],'duplicate_basenames':data['duplicate_basenames'],'reports':['reports/logic_pipeline_inspection.md','reports/logic_pipeline_inspection.json']},indent=2))
 return 1 if data['crc_error'] or data['unsafe_paths'] or not data['txt_files'] else 0
if __name__=='__main__': raise SystemExit(main())
