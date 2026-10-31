#!/usr/bin/env python3
"""v211: source-derived classification of all 38 current-season SimC enchants.

Reads the exact v191 candidate list and source-pinned SimC DBC, spell text,
and Midnight effect-registration files. This is a metadata compiler only:
no Native calls, no proc/effect reimplementation, no UI promotion.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path

SCHEMA="v211_current_season_enchant_effect_classification_v1"
SIMC_COMMIT="710c2408bfd3ae4df71b8cd55cdf01f63fd6c926"
MAX_SOURCE=10_000_000
STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")
SOURCE_PINS={
 "permanent_enchant.inc":("engine/dbc/generated/permanent_enchant.inc",86347,
                          "2321ad985ab4ee960a5a3a80d41b25db9fb2b8af"),
 "spell_item_enchantment.inc":("engine/dbc/generated/spell_item_enchantment.inc",1093702,
                               "7262db77d57d3c041a561de4d3d404431685a7ff"),
 "spelltext_data.inc":("engine/dbc/generated/spelltext_data.inc",3971792,
                       "0197c596fd5dfddbe04a1d7284ec9025d51d3bf3"),
 "data_enums.hh":("engine/dbc/data_enums.hh",75791,
                  "23e5af4d5c407aef6092225030019757c9fa3354"),
 "unique_gear_midnight.cpp":("engine/player/unique_gear_midnight.cpp",243844,
                             "9bb01bff903f22c3332f9cb6464ed72c0cae27ea"),
 "enchants.cpp":("engine/item/enchants.cpp",19322,
                 "4876fc816c275844ad6da9be3ca026cdb4a52090"),
}
PERM_ROW=re.compile(r'^\s*\{\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(0x[0-9a-fA-F]+)\s*,\s*(0x[0-9a-fA-F]+)\s*,\s*"([^"]+)"\s*\},?\s*$')
DBC_ROW=re.compile(
 r'^\s*\{\s*(\d+)\s*,\s*(\d+)\s*,\s*(-?\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,'
 r'\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,'
 r'\s*\{([^}]*)\}\s*,\s*\{([^}]*)\}\s*,\s*\{([^}]*)\}\s*,\s*\{([^}]*)\}\s*,'
 r'\s*(\d+)\s*,\s*"([^"]*)"\s*\},?\s*$')
SPELLTEXT_ROW=re.compile(r'^\s*\{\s*(\d+)\s*,\s*("(?:\\.|[^"\\])*")')
ENUM_ROW=re.compile(r'^\s*(ITEM_ENCHANTMENT_[A-Z0-9_]+|ITEM_MOD_[A-Z0-9_]+)\s*=\s*(-?\d+)')
class SourceBlocked(ValueError):pass
def need(ok,code):
    if not ok:raise SourceBlocked(code)
def canonical(obj):
    return json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":"))
def sha256(raw):
    return hashlib.sha256(raw).hexdigest()
def git_blob_sha(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()
def read_bytes(path):
    p=Path(path)
    need(p.is_file() and 0<p.stat().st_size<=MAX_SOURCE,
         "SIMC_SOURCE_FILE_MISSING_OR_SIZE_INVALID:"+p.name)
    return p.read_bytes()
def load_pinned_sources(folder):
    out={};receipt={}
    for name,(relative,size,blob) in SOURCE_PINS.items():
        raw=read_bytes(Path(folder)/name)
        need(len(raw)==size,"SIMC_SOURCE_SIZE_DRIFT:"+name)
        actual=git_blob_sha(raw)
        need(actual==blob,"SIMC_SOURCE_GIT_BLOB_DRIFT:"+name)
        try:out[name]=raw.decode("utf8")
        except UnicodeError as e:raise SourceBlocked("SIMC_SOURCE_NON_UTF8:"+name) from e
        receipt[name]={"path":relative,"size_bytes":len(raw),
                       "git_blob_sha1":actual,"sha256":sha256(raw)}
    return out,receipt
def build_from_header(text,label):
    m=re.search(r"wow build (\d+\.\d+\.\d+\.\d+)", "\n".join(text.splitlines()[:5]))
    need(m is not None,"SIMC_SOURCE_BUILD_HEADER_MISSING:"+label)
    return m.group(1)
def parse_permanent(text):
    # The full historical SimC DBC array may repeat an enchant ID across
    # different item masks/tokens. Preserve all rows and match the exact
    # v191 token+rank+class+mask identity; never assume ID alone is unique.
    rows={}
    for line in text.splitlines():
        if not line.lstrip().startswith("{"):continue
        m=PERM_ROW.fullmatch(line)
        need(m is not None,"SIMC_PERMANENT_ENCHANT_ROW_UNPARSED")
        eid,rank,item_class,inv,sub,token=m.groups()
        row={"enchant_id":int(eid),"quality_rank":int(rank),
             "item_class":int(item_class),"inventory_type_mask":int(inv,16),
             "item_subclass_mask":int(sub,16),"token":token}
        rows.setdefault(row["enchant_id"],[]).append(row)
    return rows
def ints(raw):
    return [int(x.strip(),0) for x in raw.split(",")]
def floats(raw):
    return [float(x.strip().removesuffix("f")) for x in raw.split(",")]
def parse_dbc_rows(text,target_ids):
    rows={}
    for line in text.splitlines():
        if not line.lstrip().startswith("{"):continue
        m=DBC_ROW.fullmatch(line)
        need(m is not None,"SIMC_ITEM_ENCHANTMENT_ROW_UNPARSED")
        vals=m.groups()
        eid=int(vals[0])
        if eid not in target_ids:continue
        row={"id":eid,"id_gem":int(vals[1]),"id_scaling":int(vals[2]),
             "min_scaling_level":int(vals[3]),"max_scaling_level":int(vals[4]),
             "min_ilevel":int(vals[5]),"max_ilevel":int(vals[6]),
             "req_skill":int(vals[7]),"req_skill_value":int(vals[8]),
             "ench_type":ints(vals[9]),"ench_amount":ints(vals[10]),
             "ench_prop":ints(vals[11]),"ench_coeff":floats(vals[12]),
             "id_spell":int(vals[13]),"dbc_name":vals[14]}
        need(eid not in rows,"SIMC_ITEM_ENCHANTMENT_DUPLICATE_ID")
        rows[eid]=row
    need(set(rows)==set(target_ids),
         "SIMC_ITEM_ENCHANTMENT_TARGET_COVERAGE_MISMATCH")
    return rows
def parse_enums(text):
    out={}
    for line in text.splitlines():
        m=ENUM_ROW.match(line)
        if m:out[m.group(1)]=int(m.group(2))
    required={
      "ITEM_ENCHANTMENT_EQUIP_SPELL":3,"ITEM_ENCHANTMENT_STAT":5,
      "ITEM_MOD_AGILITY":3,"ITEM_MOD_STRENGTH":4,"ITEM_MOD_INTELLECT":5,
      "ITEM_MOD_STAMINA":7,"ITEM_MOD_CRIT_RATING":32,
      "ITEM_MOD_HASTE_RATING":36,"ITEM_MOD_VERSATILITY_RATING":40,
      "ITEM_MOD_MASTERY_RATING":49,"ITEM_MOD_SPEED_RATING":61,
      "ITEM_MOD_LEECH_RATING":62,"ITEM_MOD_AVOIDANCE_RATING":63,
      "ITEM_MOD_STRENGTH_AGILITY_INTELLECT":71}
    need(all(out.get(k)==v for k,v in required.items()),
         "SIMC_ENCHANT_OR_ITEM_MOD_ENUM_DRIFT")
    return out
def parse_spelltexts(text):
    out={}
    for line in text.splitlines():
        m=SPELLTEXT_ROW.match(line)
        if not m:continue
        try:value=json.loads(m.group(2))
        except ValueError as e:raise SourceBlocked("SIMC_SPELLTEXT_STRING_INVALID") from e
        out[int(m.group(1))]=value
    return out
def resolve_spelltext(spell_id,spelltexts):
    value=spelltexts.get(spell_id)
    for _ in range(4):
        if not isinstance(value,str):return None
        m=re.fullmatch(r"\$@spelldesc(\d+)",value.strip())
        if not m:return value
        value=spelltexts.get(int(m.group(1)))
    return value if isinstance(value,str) else None
def parse_custom_handlers(text):
    # Only direct Midnight register_special_effect() bindings are recorded.
    source=re.sub(r"//[^\n]*","",text)
    found={}
    for match in re.finditer(r"register_special_effect\s*\((.*?)\)\s*;",source,re.S):
        args=match.group(1);depth=0;split=-1
        for i,ch in enumerate(args):
            if ch=="{":depth+=1
            elif ch=="}":depth-=1
            elif ch=="," and depth==0:
                split=i;break
        if split<0:continue
        first=args[:split];rest=args[split+1:]
        handler=re.search(r"(?:[A-Za-z_]\w*::)?([A-Za-z_]\w*)\s*(?:,|$)",rest.strip())
        if not handler:continue
        name=handler.group(1)
        for value in re.findall(r"\b\d{6,7}\b",first):
            eid=int(value)
            if eid in found:need(found[eid]==name,"SIMC_SPECIAL_EFFECT_HANDLER_CONFLICT")
            found[eid]=name
    return found
MODS={
 3:("agility","PRIMARY_ATTRIBUTE"),4:("strength","PRIMARY_ATTRIBUTE"),
 5:("intellect","PRIMARY_ATTRIBUTE"),6:("spirit","NON_CHMV_STAT"),
 7:("stamina","NON_CHMV_STAT"),32:("crit_rating","CHMV_SECONDARY_RATING"),
 36:("haste_rating","CHMV_SECONDARY_RATING"),
 40:("versatility_rating","CHMV_SECONDARY_RATING"),
 49:("mastery_rating","CHMV_SECONDARY_RATING"),
 61:("speed_rating","TERTIARY_RATING"),
 62:("leech_rating","TERTIARY_RATING"),
 63:("avoidance_rating","TERTIARY_RATING"),
 71:("strength_agility_intellect","PRIMARY_ATTRIBUTE_HYBRID")}
def spell_role(text,handler):
    low=(text or "").lower()
    if handler=="eyes_of_the_eagle":return "CRIT_EFFECTIVENESS_PASSIVE"
    if handler=="stat_weapon_enchant":
        if "critical strike" in low:return "TEMPORARY_CRIT_RATING_PROC"
        if "haste" in low:return "TEMPORARY_HASTE_RATING_PROC"
        if "mastery" in low:return "TEMPORARY_MASTERY_RATING_PROC"
        if "versatility" in low:return "TEMPORARY_VERSATILITY_RATING_PROC"
        if "$pri" in low or "primary" in low:return "TEMPORARY_PRIMARY_STAT_PROC"
    if handler=="rite_of_the_hashey" or "random secondary stat" in low:
        return "ADAPTIVE_TEMPORARY_SECONDARY_RATING_PROC"
    if handler in ("strength_of_halazzi","flames_of_the_sindorei"):
        return "DAMAGE_PROC"
    if "barrier" in low:return "ABSORB_OR_DEFENSIVE_PROC"
    if "mana pool" in low:return "MANA_UTILITY"
    if "skyriding" in low:return "TRAVEL_UTILITY"
    if "health whenever you defeat" in low:return "OUTDOOR_HEAL_UTILITY"
    if "movement speed whenever" in low:return "OUTDOOR_MOVEMENT_UTILITY"
    if text:return "SIMC_DBC_SPELL_EFFECT"
    return "SIMC_SPELL_TEXT_UNRESOLVED"
def verify_evidence(path,kind):
    data=json.loads(Path(path).read_text("utf8"))
    if kind=="8025":
        need(data.get("schema")=="v202_one_exact_enchant_source_evidence_v1"
             and data.get("status")=="VERIFIED_IN_TWO_NATIVE_PAIR_PROFILES_NOT_UI_PROMOTED"
             and data.get("enchant_id")==8025
             and data.get("static_enchant_E")=={
                "crit_rating":0,"haste_rating":30,"mastery_rating":0,
                "versatility_rating":0},
             "V202_8025_NATIVE_EVIDENCE_DRIFT")
        return {"status":"MEASURED_ONE_LINUX_FROST_334_PROFILE",
                "static_E":dict(data["static_enchant_E"]),
                "ui_selectable":False,"source_file":"data/v202_verified_enchant_8025_source.json"}
    need(data.get("schema")=="v206_one_eyes_of_eagle_nonchmv_native_rating_scope_v1"
         and data.get("status")=="PASS_EAGLE_7967_ONE_WINDOWS_PROFILE_STATIC_E_ZERO"
         and data.get("static_CHMV_E")==dict.fromkeys(STATS,0),
         "V206_7967_NATIVE_EVIDENCE_DRIFT")
    return {"status":"MEASURED_ZERO_ONE_WINDOWS_PALADIN_334_PROFILE",
            "static_E":dict(data["static_CHMV_E"]),
            "ui_selectable":True,"source_file":"data/v206_eagle_7967_windows_E0_proof.json"}
def classify_row(candidate,dbc,enums,spelltexts,handlers,evidence):
    stat_type=enums["ITEM_ENCHANTMENT_STAT"]
    equip_type=enums["ITEM_ENCHANTMENT_EQUIP_SPELL"]
    static=[];spells=[];unknown=[]
    for idx,(typ,amount,prop,coeff) in enumerate(zip(
            dbc["ench_type"],dbc["ench_amount"],dbc["ench_prop"],dbc["ench_coeff"])):
        if typ==0:continue
        if typ==stat_type:
            mod=MODS.get(prop)
            need(mod is not None,"CURRENT_SEASON_ITEM_MOD_UNCLASSIFIED:"+str(prop))
            name,category=mod
            static.append({"component_index":idx+1,"item_mod_id":prop,
                           "item_mod":name,"category":category,
                           "dbc_amount":amount,"scaling_id":dbc["id_scaling"],
                           "coefficient":coeff})
        elif typ==equip_type:
            text=resolve_spelltext(prop,spelltexts)
            handler=handlers.get(prop)
            spells.append({"component_index":idx+1,"driver_spell_id":prop,
                           "source_description":text,
                           "simc_custom_handler":handler,
                           "handler_status":("REGISTERED_IN_PINNED_MIDNIGHT_SOURCE"
                               if handler else
                               "NO_CUSTOM_MIDNIGHT_HANDLER_FOUND_GENERIC_DBC_PATH_NOT_CERTIFIED"),
                           "effect_role":spell_role(text,handler)})
        else:
            unknown.append({"component_index":idx+1,"enchant_type_id":typ,
                            "item_mod_or_spell_id":prop,"amount":amount,
                            "coefficient":coeff})
    chmv=[x for x in static if x["category"]=="CHMV_SECONDARY_RATING"]
    if candidate["enchant_id"]==7967:
        family="crit_effectiveness"
        summary="치명타 효과 강화; 치명타 rating 증가와 별개"
    elif chmv:
        names=sorted({x["item_mod"] for x in chmv})
        family="static_chmv_rating_"+("_".join(names))
        summary="정적 CHMV rating: "+", ".join(names)
    elif static and spells:
        family="static_nonchmv_plus_simc_spell"
        summary="정적 비CHMV 스탯 + SimC 주문 효과"
    elif static:
        family="static_nonchmv_item_mod"
        summary="정적 비CHMV 스탯: "+", ".join(sorted({x["item_mod"] for x in static}))
    elif spells:
        family="simc_spell_effect"
        summary="SimC 주문/발동 효과"
    else:
        family="unclassified_source_effect"
        summary="원본 효과 분류 미확정"
    dynamic=[x for x in spells if x["effect_role"] in (
        "TEMPORARY_CRIT_RATING_PROC","TEMPORARY_HASTE_RATING_PROC",
        "TEMPORARY_MASTERY_RATING_PROC","TEMPORARY_VERSATILITY_RATING_PROC",
        "ADAPTIVE_TEMPORARY_SECONDARY_RATING_PROC")]
    eid=candidate["enchant_id"]
    native=evidence.get(eid,{"status":"NOT_MEASURED","static_E":None,
                             "ui_selectable":False,"source_file":None})
    return {
      "token":candidate["token"],"enchant_id":eid,
      "dbc_name":dbc["dbc_name"],"quality_rank":candidate["quality_rank"],
      "kind":candidate["token"].split("__",1)[0].replace("enchant_",""),
      "item_class":candidate["item_class"],
      "inventory_type_mask":candidate["inventory_type_mask"],
      "item_subclass_mask":candidate["item_subclass_mask"],
      "static_components":static,"spell_effects":spells,
      "unknown_components":unknown,
      "effect_family":family,"effect_summary":summary,
      "static_chmv_rating_present_in_dbc":bool(chmv),
      "static_chmv_stats":sorted({x["item_mod"] for x in chmv}),
      "dynamic_chmv_proc_present_in_spell_text":bool(dynamic),
      "dynamic_chmv_proc_roles":sorted({x["effect_role"] for x in dynamic}),
      "simc_effect_owner":"SIMC",
      "simc_effect_reimplemented":False,
      "simc_custom_handlers":sorted({x["simc_custom_handler"] for x in spells
                                     if x["simc_custom_handler"]}),
      "simc_generic_or_unregistered_spell_count":sum(
          not x["simc_custom_handler"] for x in spells),
      "native_E_evidence":native,
      "budget_policy":("STATIC_E_REQUIRES_EXACT_MATCHED_NATIVE_PROFILE_AND_IS_FIXED_INSIDE_G"
                       if chmv else
                       "NO_STATIC_CHMV_COMPONENT_IN_DBC_ROW; DYNAMIC_EFFECTS_STAY_WITH_SIMC"),
      "selection_status":("EXISTING_EAGLE_ONE_SCOPE_USER_CHOICE" if eid==7967 else
                          "DEVELOPER_ONLY_EXACT_SCOPE" if eid==8025 else
                          "LOCKED_NO_GENERAL_USER_ADMISSION"),
      "effect_source_status":("DBC_STAT_AND_SPELLTEXT_SOURCE_CLASSIFIED"
                              if not unknown else "UNKNOWN_DBC_COMPONENT_REVIEW_REQUIRED")
    }
def compile_catalog(candidates,source_dir,proof_8025,proof_7967):
    need(candidates.get("schema")=="v196_source_first_enchant_candidates_v1"
         and candidates.get("status")=="SOURCE_OBSERVED_NOT_NATIVE_BUDGET_VERIFIED"
         and candidates.get("simc_commit")==SIMC_COMMIT
         and candidates.get("season_game_build")=="12.1.5.70575"
         and candidates.get("user_selectable") is False,
         "V191_ENCHANT_CANDIDATE_SOURCE_DRIFT")
    need(type(candidates.get("rows")) is list and len(candidates["rows"])==38,
         "V191_ENCHANT_CANDIDATE_COUNT_INVALID")
    sources,source_receipt=load_pinned_sources(source_dir)
    builds={name:build_from_header(sources[name],name)
            for name in ("permanent_enchant.inc","spell_item_enchantment.inc",
                         "spelltext_data.inc")}
    need(set(builds.values())=={"12.1.5.70575"},
         "SIMC_GENERATED_ENCHANT_BUILD_MISMATCH")
    permanent=parse_permanent(sources["permanent_enchant.inc"])
    ids={r["enchant_id"] for r in candidates["rows"]}
    need(len(ids)==38,"V191_ENCHANT_IDS_DUPLICATE")
    for row in candidates["rows"]:
        matches=[source for source in permanent.get(row["enchant_id"],[])
                 if source["token"]==row["token"]
                 and source["quality_rank"]==row["quality_rank"]
                 and source["item_class"]==row["item_class"]
                 and source["inventory_type_mask"]==row["inventory_type_mask"]
                 and source["item_subclass_mask"]==row["item_subclass_mask"]]
        need(len(matches)==1,
             "V191_CANDIDATE_VS_PINNED_PERMANENT_SOURCE_DRIFT:"+str(row["enchant_id"]))
    dbc=parse_dbc_rows(sources["spell_item_enchantment.inc"],ids)
    enums=parse_enums(sources["data_enums.hh"])
    spelltexts=parse_spelltexts(sources["spelltext_data.inc"])
    handlers=parse_custom_handlers(sources["unique_gear_midnight.cpp"])
    evidence={
      8025:verify_evidence(proof_8025,"8025"),
      7967:verify_evidence(proof_7967,"7967")}
    rows=[classify_row(r,dbc[r["enchant_id"]],enums,spelltexts,handlers,evidence)
          for r in sorted(candidates["rows"],key=lambda x:x["enchant_id"])]
    need(len(rows)==38 and len({x["enchant_id"] for x in rows})==38,
         "V211_CLASSIFICATION_COVERAGE_INVALID")
    need(sum(x["static_chmv_rating_present_in_dbc"] for x in rows)==8,
         "V211_STATIC_CHMV_SOURCE_COUNT_DRIFT")
    need(sum(x["selection_status"]=="EXISTING_EAGLE_ONE_SCOPE_USER_CHOICE"
             for x in rows)==1 and
         sum(x["selection_status"]=="DEVELOPER_ONLY_EXACT_SCOPE" for x in rows)==1,
         "V211_SELECTION_BOUNDARY_DRIFT")
    need(not any(x["unknown_components"] for x in rows),
         "V211_UNKNOWN_DBC_EFFECT_COMPONENT")
    return {
      "schema":SCHEMA,
      "status":"SOURCE_CLASSIFIED_NOT_GENERAL_NATIVE_ACCEPTANCE_OR_UI_PROMOTION",
      "season_game_build":candidates["season_game_build"],
      "simc_commit":SIMC_COMMIT,
      "source_files":source_receipt,
      "candidate_source_artifact_id":candidates["source_artifact_id"],
      "counts":{"total":38,"static_chmv_rating":8,
                "static_nonchmv_only_or_mixed":sum(
                    bool(x["static_components"]) and
                    not x["static_chmv_rating_present_in_dbc"] for x in rows),
                "spell_effects":sum(bool(x["spell_effects"]) for x in rows),
                "native_E_measured":2,"user_selectable_existing_scope":1,
                "developer_only_exact_scope":1,"locked":36},
      "native_calls":0,"network_calls_by_classifier":0,
      "automatic_ui_promotion":False,
      "simc_effect_reimplemented":False,
      "rows":rows,
      "limitations":[
        "DBC static component classification is not a generalized exact Native E measurement.",
        "enchant_id 8025 E=haste30 is one Linux Frost ilvl334 finger1 profile only.",
        "enchant_id 7967 E=0 is one Windows Retribution Paladin ilvl334 finger1 profile only.",
        "The other six static CHMV ring enchants have no exact Native E measurement.",
        "Spell descriptions and custom registration identify SimC-owned effect semantics, not independent proof of all proc acceptance or mechanics.",
        "Weapon subclass mask zero does not certify exact hand/weapon eligibility.",
        "All 37 choices other than existing one-scope Eagle remain non-user-selectable; 8025 remains developer-only."
      ]
    }
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidates",type=Path,required=True)
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--proof-8025",type=Path,required=True)
    p.add_argument("--proof-7967",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args(argv)
    try:
        out=compile_catalog(json.loads(a.candidates.read_text("utf8")),
                            a.source_dir,a.proof_8025,a.proof_7967)
    except (OSError,ValueError,KeyError) as e:
        print("V211_SOURCE_CLASSIFICATION_BLOCKED",str(e))
        return 3
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True,
                                ensure_ascii=False)+"\n",encoding="utf8")
    print("V211_ENCHANT_SOURCE_CLASSIFICATION_PASS",
          json.dumps(out["counts"],sort_keys=True),
          "NATIVE_0","NO_UI_PROMOTION",flush=True)
    return 0
if __name__=="__main__":raise SystemExit(main())
