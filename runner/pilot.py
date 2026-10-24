#!/usr/bin/env python3
"""SIMC Secondary Optimizer v033 remote native compatibility pilot.

No external packages. Never accepts arbitrary SimC input from workflow dispatch.
Uses one user-proven archived scenario, changing ONLY Omnium 4th rune,
iterations, and JSON2 output path. Not a CHMV optimization.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, math, os, pathlib, re, subprocess, sys, traceback
ROOT=pathlib.Path(__file__).resolve().parent.parent
PROFILE=ROOT/'inputs'/'v031r3_reference.simc'
FIXTURE=ROOT/'fixtures'/'v031r3_reference_summary.json'
EXPECTED_OTHER_RUNE=[136822,136817,136814]
RUNES={'haste':136821,'crit':136815}
BUFFS={'haste':'rune_of_burning_haste','crit':'rune_of_critical_power'}
STAT_KEYS=('crit_rating','haste_rating','mastery_rating','versatility_rating')
EXPECTED_VECTOR={'crit_rating':600,'haste_rating':1140,'mastery_rating':1115,'versatility_rating':329}
class PilotError(RuntimeError):pass
def need(ok,why):
 if not ok:raise PilotError(why)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
def source():
 a=json.loads(FIXTURE.read_text(encoding='utf8'))
 text=PROFILE.read_text(encoding='utf8')
 need(sha(PROFILE)==a['portable_input_sha256'],'REFERENCE_PROFILE_HASH_CHANGED')
 need('C:\\' not in text and 'json2=' not in text,'REFERENCE_LOCAL_PATH_OR_OUTPUT_OVERRIDE')
 need(text.count('omnium_talents=136822:1/136817:1/136821:1/136814:1')==1,'REFERENCE_RUNE_SETTING_CHANGED')
 need(text.count('race=dwarf')==1,'RACE_CHANGED')
 need(text.count('food=royal_roast')==1,'FOOD_CHANGED')
 need(text.count('embellishment=arcanoweave_lining')==2,'EMBELLISHMENT_COUNT_CHANGED')
 for k in STAT_KEYS:need(text.count('gear_'+k+'=')==1,'GEAR_INJECTION_CHANGED:'+k)
 for val in ('270164','281215','239648'):
  need('id='+val+',' in text,'PINNED_ITEM_MISSING:'+val)
 return text,a

def generate(text,output,rune,iterations):
 need(rune in RUNES,'UNSUPPORTED_RUNE')
 need(iterations in (60,320),'UNAPPROVED_ITERATIONS')
 old='omnium_talents=136822:1/136817:1/136821:1/136814:1'
 new='omnium_talents=136822:1/136817:1/'+str(RUNES[rune])+':1/136814:1'
 need(text.count(old)==1,'SOURCE_OMNIUM_NOT_UNIQUE')
 transformed=text.replace(old,new)
 lines=transformed.splitlines()
 newlines=[]
 for line in lines:
  if line.startswith('iterations='):line='iterations='+str(iterations)
  newlines.append(line)
 newlines.append('json2='+str(output.resolve()))
 body='\n'.join(newlines)+'\n'
 # no profile overrides/overlapping opaque input between cases
 need(body.count('json2=')==1,'JSON2_NOT_UNIQUE')
 need(body.count('omnium_talents=')==1,'OMNIUM_NOT_UNIQUE')
 need(body.count(new)==1,'RUNE_INJECTION_FAILED')
 return body

def report_native(doc,runefamily,iterations):
 need(doc.get('report_version')=='2.0.0','JSON2_REPORT_VERSION_CHANGED')
 sim=doc.get('sim') or {};people=sim.get('players') or []
 need(len(people)==1,'JSON2_PLAYER_COUNT')
 p=people[0]
 need(p.get('race')=='dwarf' and p.get('specialization')=='Arcane Mage','CHARACTER_CHANGED')
 need(p.get('food')=='royal_roast','FOOD_NOT_NATIVE')
 items=p.get('gear') or {}
 ids={'head':271564,'shoulders':271562,'chest':271567,'legs':271563,
      'back':239656,'wrists':239648,'trinket1':270164,'trinket2':281215}
 for slot,item in ids.items():
  x=items.get(slot) or {}
  need(re.search(r'(?:^|,)id='+str(item)+r'(?:,|$)',x.get('encoded_item','')) is not None,
       'ITEM_ID_NOT_NATIVE:'+slot)
  need(x.get('ilevel')==334,'ITEM_LEVEL_MISMATCH:'+slot)
 for slot in ('back','wrists'):
  need('embellishment=arcanoweave_lining' in items[slot]['encoded_item'],'EMBELLISHMENT_NOT_NATIVE:'+slot)
 rating=p.get('collected_data',{}).get('buffed_stats',{}).get('stats',{})
 actual={k:int(round(rating[k])) for k in STAT_KEYS}
 need(actual==EXPECTED_VECTOR,'FINAL_CHMV_MISMATCH:'+str(actual))
 need(sum(actual.values())==3184,'STATIC_TOTAL_CHANGED')
 need(sim.get('options',{}).get('fight_style')=='Patchwerk','FIGHT_STYLE_CHANGED')
 need(sim.get('options',{}).get('desired_targets')==1,'TARGET_COUNT_CHANGED')
 need(sim.get('options',{}).get('max_time')==300.0,'MAX_TIME_CHANGED')
 buffs=[x.get('name','') for x in p.get('buffs',[])]
 need('cumulative_power' in buffs,'TIER4_BUFF_ABSENT')
 need('arcanoweave_insight' in buffs,'LINING_BUFF_ABSENT')
 need(BUFFS[runefamily] in buffs,'REQUESTED_RUNE_BUFF_ABSENT:'+BUFFS[runefamily])
 for other,token in BUFFS.items():
  if other!=runefamily:need(token not in buffs,'OPPOSITE_RUNE_BUFF_PRESENT')
 dps=p.get('collected_data',{}).get('dps',{})
 mean=float(dps['mean']);sem=float(dps['mean_std_dev']); count=int(dps['count'])
 need(math.isfinite(mean) and mean>0 and math.isfinite(sem) and sem>0,'DPS_OR_UNCERTAINTY_INVALID')
 need(count>=max(30,iterations-3),'DPS_SAMPLES_TOO_LOW')
 return {'status':'PASS_NATIVE_JSON2','dps_mean':mean,'sem':sem,'ci95':1.96*sem,
         'samples':count,'chmv_vector':actual,'chmv_total':3184,'rune_buff':BUFFS[runefamily],
         'tier4_buff':True,'arcanoweave_buff':True,'native_buff_names':buffs,
         'simc_git_revision':doc.get('git_revision'),'simc_version':doc.get('version'),
         'native_logs':doc.get('logs',[])}

def launch(binary,runes,iterations,output):
 output.mkdir(parents=True,exist_ok=True)
 text,reference=source()
 status={'schema':'v033_simc_remote_pilot','status':'PENDING','requested_runes':runes,
         'iterations_per_case':iterations,'reference_win_git_revision':'7bc1071',
         'reference_win_dps':reference['reference_dps_mean'],
         'reference_chmv':reference['reference_rating'],'runs':{}}
 for rune in runes:
  case=output/rune;case.mkdir(parents=True,exist_ok=True)
  inp=case/'input.simc';result=case/'result.json'
  inp.write_text(generate(text,result,rune,iterations),encoding='utf8')
  record={'status':'ATTEMPTED','input_sha256':sha(inp),'rune':rune,
          'rune_id':RUNES[rune],'iterations':iterations}
  status['runs'][rune]=record
  write(output/'RUN_RECEIPT_v033.json',status)
  try:
   with (case/'stdout.txt').open('w',encoding='utf8') as out,(case/'stderr.txt').open('w',encoding='utf8') as err:
    proc=subprocess.run([str(binary),str(inp)],cwd=binary.parent,stdin=subprocess.DEVNULL,
                     stdout=out,stderr=err,timeout=1200,check=False)
   record['exit_code']=proc.returncode
   need(proc.returncode==0,'NATIVE_SIMC_EXIT_'+str(proc.returncode))
   need(result.is_file() and result.stat().st_size>1000,'JSON2_NOT_CREATED')
   record['result_sha256']=sha(result)
   doc=json.loads(result.read_text(encoding='utf8'))
   record.update(report_native(doc,rune,iterations))
   # Compare Windows vs Linux only as diagnostic, not strict parity.
   if rune=='haste':
    delta=record['dps_mean']-reference['reference_dps_mean']
    record['baseline_windows_delta_dps']=delta
    record['baseline_windows_delta_pct']=100*delta/reference['reference_dps_mean']
    record['different_iterations_or_os_prevent_strict_parity']=True
  except Exception as e:
   record['status']='BLOCKED'
   record['error']=type(e).__name__+':'+str(e)
  write(case/'CASE_RECEIPT_v033.json',record)
  write(output/'RUN_RECEIPT_v033.json',status)
  if record['status']!='PASS_NATIVE_JSON2':break
 status['status']='PASS_ALL_NATIVE' if len(status['runs'])==len(runes) and all(
     x['status']=='PASS_NATIVE_JSON2' for x in status['runs'].values()) else 'PARTIAL_OR_BLOCKED'
 status['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 write(output/'RUN_RECEIPT_v033.json',status)
 text_lines=['v033 cloud SimC source/build compatibility pilot',
              'status='+status['status'],'iterations_per_case='+str(iterations)]
 for rune,r in status['runs'].items():
  text_lines.append(rune+': '+r['status']+' DPS='+str(round(r.get('dps_mean',0),2))+
           ' '+r.get('error',''))
 (output/'SUMMARY_v033.txt').write_text('\n'.join(text_lines)+'\n',encoding='utf8')
 return 0 if status['status']=='PASS_ALL_NATIVE' else 2

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('action',choices=('check','execute'))
 parser.add_argument('--binary',type=pathlib.Path)
 parser.add_argument('--rune',choices=('both','haste','crit'),default='both')
 parser.add_argument('--iterations',type=int,choices=(60,320),default=60)
 parser.add_argument('--output',type=pathlib.Path,default=ROOT/'run-output')
 args=parser.parse_args()
 try:
  src,fixture=source()
  for which in RUNES:generate(src,args.output/which/'result.json',which,args.iterations)
  if args.action=='check':
   print('PASS_OFFLINE_INPUT_CONTRACT: '+','.join(RUNES));return 0
  need(args.binary is not None and args.binary.is_file(),'MISSING_LINUX_SIMC_EXECUTABLE')
  to_run=['haste','crit'] if args.rune=='both' else [args.rune]
  return launch(args.binary.resolve(),to_run,args.iterations,args.output.resolve())
 except Exception as e:
  args.output.mkdir(parents=True,exist_ok=True)
  write(args.output/'RUN_RECEIPT_v033.json',{'schema':'v033_simc_remote_pilot','status':'BLOCKED',
          'error':type(e).__name__+':'+str(e)})
  print('BLOCKED:',type(e).__name__,str(e),file=sys.stderr)
  return 2
if __name__=='__main__':raise SystemExit(main())
