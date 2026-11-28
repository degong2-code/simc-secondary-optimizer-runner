#!/usr/bin/env python3
"""One actual replay of v847 compact relations with only missing SpellEffect."""
import argparse,json,hashlib
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
import v217_stage_execution_engine as stages
import v281_consumable_simc_relation as spells
import v848_embellishment_recipe_source as engine
from p1_v847_embellishment_source_once import reuse

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--prior",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);root=a.root.resolve()
    doc={"status":"SOURCE_PENDING","native_calls":0,"new_source_requests":0}
    try:
        raw=a.prior.read_bytes()
        engine.need(hashlib.sha256(raw).hexdigest()==
            "2ee25f3824fc7925ab7fa90b910ee17b987374fd2a51b2986a26e256ab343b44",
            "V847_PRIOR_SHA_DRIFT")
        prior=json.loads(raw)
        build=prior["game_build"]; rev=prior["simc_revision"]; exp=prior["expansion_id"]
        engine.need(prior["status"]=="EXACT_CRAFTING_REAGENT_EFFECT_RELATIONS_OBSERVED",
                    "V847_PRIOR_NOT_COMPLETE")
        paths,stamp=reuse(root,"fresh-wago-db2",("ItemSparse","Item","CraftingData","receipt"),
                         prior["reused_receipts"]["wago"])
        engine.need(json.loads(paths["receipt"].read_text("utf8"))["build"]==build,
                    "WAGO_BUILD_DRIFT")
        url="https://wago.tools/db2/SpellEffect/csv?"+urlencode({"build":build,"locale":"enUS"})
        # No preserved SpellEffect file in the v847 artifacts. This is a
        # source-only experiment; product path must consume v281's sealed
        # raw output, never download another SpellEffect.
        rel="source/v848_research_SpellEffect.csv"
        def execute():
            doc["new_source_requests"]+=1
            req=Request(url,headers={"User-Agent":"SIMC-Secondary-RecipeSource/1.0",
                                     "Accept":"text/csv"})
            with urlopen(req,timeout=75) as response:
                engine.need(response.status==200,"SPELL_EFFECT_HTTP")
                with (root/rel).open("wb") as target:
                    size=0
                    while True:
                        chunk=response.read(262144)
                        if not chunk:break
                        size+=len(chunk)
                        engine.need(size<=spells.SPELL_EFFECT_SIZE_LIMIT,"SPELL_EFFECT_SIZE")
                        target.write(chunk)
            engine.need(size>0,"SPELL_EFFECT_EMPTY")
        def validate(files):
            with files["raw"].open(encoding="utf-8-sig") as f:
                return {"SpellID","Effect","EffectMiscValue_0","DifficultyID","EffectIndex"}<=set(f.readline().strip().split(","))
        receipt=stages.execute_stage(root=root,stage_id="v848-research-recipe-spell-effect",
            stage_version="same-build-raw-v1",inputs={"game_build":build,"source_url":url},
            outputs={"raw":rel},execute=execute,validate=validate)
        paths["SpellEffect"]=root/rel
        result=engine.recipe_outputs(prior["matches"],paths,game_build=build,
                                     simc_revision=rev,expansion_id=exp)
        doc.update(result,spell_effect_receipt_sha256=receipt["receipt_sha256"],
                   reused_wago_receipt_sha256=stamp,prior_sha256=hashlib.sha256(raw).hexdigest())
    except Exception as e:
        doc["first_blocker"]={"type":type(e).__name__,"code":str(e)[:240]}
    (a.out/"V848_RECIPE_OUTPUT_SOURCE.json").write_text(
        json.dumps(doc,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("V848",doc["status"],"requests",doc["new_source_requests"],
          "exact recipes",doc.get("exact_recipe_spell_count"),
          "pending",doc.get("pending_recipe_spell_count"),"outputs",doc.get("exact_output_item_count"),
          "native0","blocker",doc.get("first_blocker"))
    return 0 if doc.get("exact_recipe_spell_count",0)>0 else 2
if __name__=="__main__":raise SystemExit(main())
