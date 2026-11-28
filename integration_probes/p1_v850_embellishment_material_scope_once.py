#!/usr/bin/env python3
"""Real replay: original v847/v848 bytes plus only missing quality tables."""
import argparse,json,hashlib
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
import v216_environment_build_coordinator as env
import v848_embellishment_recipe_source as engine
from p1_v847_embellishment_source_once import reuse

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--prior",type=Path,required=True)
    p.add_argument("--spell-root",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();root=a.root.resolve();a.out.mkdir(parents=True,exist_ok=True)
    doc={"status":"SOURCE_PENDING","native_calls":0,"new_source_requests":0}
    try:
        raw=(a.prior/"V847_EMBELLISHMENT_SOURCE.json").read_bytes()
        engine.need(hashlib.sha256(raw).hexdigest()=="2ee25f3824fc7925ab7fa90b910ee17b987374fd2a51b2986a26e256ab343b44","V847_PRIOR_SHA_DRIFT")
        prior=json.loads(raw);build=prior["game_build"]
        paths,wstamp=reuse(root,"fresh-wago-db2",("ItemSparse","Item","CraftingData","receipt"),
                           prior["reused_receipts"]["wago"])
        engine.need(json.loads(paths["receipt"].read_text("utf8"))["build"]==build,"WAGO_BUILD")
        for table in ("ItemBonus","ItemBonusTreeNode"):
            source,stamp=reuse(root,"season-bonus-raw-"+table,("raw",),
                              prior["reused_receipts"][table])
            paths[table]=source["raw"]
        for table in engine.RAW:
            if table in ("CraftingQuality","CraftingReagentQuality"):
                url="https://wago.tools/db2/"+table+"/csv?"+urlencode({"build":build,"locale":"enUS"})
                def obtain():
                    doc["new_source_requests"]+=1
                    with urlopen(Request(url,headers={"User-Agent":"SIMC-Secondary-CraftingSource/1.0"}),timeout=75) as resp:
                        engine.need(resp.status==200,"QUALITY_HTTP")
                        return resp.read(engine.MAX_RAW+1)
                path,_,stamp=env._sealed_season_raw_source(root=root,
                    source_id="season-crafting-raw-"+table,build=build,url=url,
                    relative="source/raw_"+table+".csv",obtain=obtain,
                    validate_bytes=lambda b:engine.valid_raw(b,table))
                paths[table]=path
            else:
                source,stamp=reuse(a.prior/"source","season-crafting-raw-"+table,("raw",),
                                  prior["new_receipts"][table])
                paths[table]=source["raw"]
        source,stamp=reuse(a.spell_root,"v848-research-recipe-spell-effect",("raw",),
                            "8435f18063e5c0f708773c07804126268bf526164cf4c2e7df7ce6eb4abb54b0")
        paths["SpellEffect"]=source["raw"]
        entries=[r for m in prior["matches"] for r in m["simc_rows"]]
        result=engine.recipe_outputs(engine.project(entries,paths,prior["expansion_id"]),paths,
            game_build=build,simc_revision=prior["simc_revision"],expansion_id=prior["expansion_id"])
        engine.need(result["exact_recipe_spell_count"]==201 and result["pending_recipe_spell_count"]==2,
                    "V848_RECIPE_REPLAY_DRIFT")
        opts=engine.material_options(result,paths)
        doc.update(status="MATERIAL_SCOPE_PROJECTED",game_build=build,
            exact_recipe_spell_count=result["exact_recipe_spell_count"],
            options=opts,family_count=len(opts),
            preferred_count=sum(o["preferred_physical_item_id"] is not None for o in opts))
    except Exception as exc:
        doc["first_blocker"]={"type":type(exc).__name__,"code":str(exc)[:240]}
    (a.out/"V850_MATERIAL_SCOPE.json").write_text(json.dumps(doc,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("V850",doc["status"],"requests",doc["new_source_requests"],"families",doc.get("family_count"),
          "preferred",doc.get("preferred_count"),"native0","blocker",doc.get("first_blocker"))
    return 0 if doc["status"]=="MATERIAL_SCOPE_PROJECTED" else 2
if __name__=="__main__":raise SystemExit(main())
