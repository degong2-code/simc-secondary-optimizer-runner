"""One actual pinned source profile, only one gem differs. No season Build."""
import argparse,json,pathlib,tempfile,hashlib
from urllib.request import Request,urlopen
import v278_sealed_simc_consumable_native_pair as pair
import v269_simc_chmv_effect_snapshot as snapshot
import v229_simc_only_source_seed as seed

REV="9933ffb946fb55b1fa66657b848f519ac19006e1"
BUILD="12.1.5.70961"
BIN_SHA="4f4472ac8687d029cd7d6041741f44aa98750ea1b3e953dfa7002dee1f38879f"
PROFILE_PATH="profiles/MID2/MID2_Paladin_Retribution.simc"
PROFILE_BLOB="864e857c5d8cdbaa5b03939f077fcb657a4784aa"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--simc",type=pathlib.Path,required=True)
    parser.add_argument("--out",type=pathlib.Path,required=True)
    args=parser.parse_args()
    out=args.out.resolve()
    out.mkdir(parents=True,exist_ok=True)
    doc={"schema":"p1_v826_special_gem_actual_source_profile_pair_v1",
         "status":"STARTED","game_build":BUILD,"simc_revision":REV,
         "binary_sha256":BIN_SHA,"source_profile_blob_sha1":PROFILE_BLOB,
         "source_profile_path":PROFILE_PATH,"full_environment_builds":0,
         "wago_calls":0,"dps_optimizer_calls":0,"native_calls":0,
         "cases":[],"game_socket_legal_verified":False,"user_selectable":False}
    def save():
        (out/"V826_SPECIAL_GEM_PAIR.json").write_text(
            json.dumps(doc,indent=2,sort_keys=True,allow_nan=False)+"\n","utf8")
    save()
    try:
        binary=args.simc.resolve(strict=True)
        if pair.file_sha(binary)!=BIN_SHA:
            raise RuntimeError("V826_PINNED_BINARY_SHA_DRIFT")
        req=Request(seed.RAW_BASE+REV+"/"+PROFILE_PATH,headers={"User-Agent":"SIMC-Secondary-source-profile-test"})
        with urlopen(req,timeout=60) as res:
            raw=res.read(30000)
        if seed.git_blob(raw)!=PROFILE_BLOB:
            raise RuntimeError("V826_PINNED_PROFILE_BLOB_DRIFT")
        active=raw.decode("utf8")
        head=[l for l in active.splitlines() if l.startswith("head=")]
        marker=",gem_id=240983"
        if (len(head)!=1 or ",id=271465," not in head[0] or
                "13750" not in head[0] or marker not in head[0] or active.count(marker)!=1):
            raise RuntimeError("V826_SOURCE_HEAD_LAYOUT_DRIFT")
        base=active.replace(marker,"",1)
        source_identity=pair.sha(raw)
        doc["source_profile_sha256"]=source_identity
        doc["head_source_row"]=head[0]
        doc["only_changed_option"]="head.gem_id=240983"
        with tempfile.TemporaryDirectory(prefix="v826-",dir=out) as td:
            root=pathlib.Path(td)
            results=[]
            for variant,profile in (("baseline",base),("active",active)):
                case=pair.run_case(stage_root=root,profile=profile.rstrip()+"\n",
                    source_identity=source_identity,binary=binary,binary_sha256=BIN_SHA,
                    revision=REV,variant=variant,timeout_seconds=180)
                receipt=case["receipt"]
                doc["native_calls"]+=case["new_native_calls"]
                doc["cases"].append({"variant":variant,"status":receipt["status"],
                    "input_sha256":receipt["input_sha256"],
                    "native_json2_sha256":receipt["native_json2_sha256"],
                    "native_returncode":receipt["native_returncode"]})
                save()
                if receipt["status"]!="NATIVE_JSON2_CAPTURED":
                    doc["simc_log_excerpt"]=(pair.log_excerpt(case["folder"]) or "").replace(str(root),"<PROBE_ROOT>")
                    raise RuntimeError("V826_NATIVE_SOURCE_PROFILE_FAILED")
                data=(case["folder"]/"native.json").read_bytes()
                if pair.sha(data)!=receipt["native_json2_sha256"]:
                    raise RuntimeError("V826_NATIVE_JSON2_SHA_DRIFT")
                results.append(snapshot._gem_native_player(data,REV))
            left,bg,bs=results[0];right,ag,ast=results[1]
            if left!=right or set(bg)!=set(ag) or "head" not in bg:
                raise RuntimeError("V826_PLAYER_GEAR_IDENTITY_DRIFT")
            for slot in bg:
                before=bg[slot]["encoded_item"];after=ag[slot]["encoded_item"]
                if (after.replace(marker,"",1)!=before if slot=="head" else after!=before):
                    raise RuntimeError("V826_ACTUAL_ENCODED_GEAR_DRIFT:"+slot)
            if marker not in ag["head"]["encoded_item"]:
                raise RuntimeError("V826_SPECIAL_GEM_NOT_OBSERVED")
            doc["actual_head_before"]=bg["head"]["encoded_item"]
            doc["actual_head_after"]=ag["head"]["encoded_item"]
            doc["buffed_CHMV_delta_observed"]={k:round(ast[k]-bs[k],6) for k in snapshot.STATS}
            # JSON2 gear fields may be sparse; retain observations, never
            # fabricate a numeric zero from absent fields.
            doc["head_static_CHMV_before"]={k:bg["head"].get(k) for k in snapshot.STATS}
            doc["head_static_CHMV_after"]={k:ag["head"].get(k) for k in snapshot.STATS}
            doc["status"]="PASS_ACTUAL_SPECIAL_GEM_PROFILE_PAIR_NOT_ADMITTED"
            save()
        return 0
    except Exception as exc:
        doc["status"]="BLOCKED_ACTUAL_SPECIAL_GEM_PROFILE_PAIR"
        doc["first_blocker"]=str(exc).split("\n",1)[0][:300]
        save()
        return 2
    finally:
        print("V826_SPECIAL_GEM_PAIR "+json.dumps(doc,ensure_ascii=True,sort_keys=True),flush=True)

if __name__=="__main__":
    raise SystemExit(main())
