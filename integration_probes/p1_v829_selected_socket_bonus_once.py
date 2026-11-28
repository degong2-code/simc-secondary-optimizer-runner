"""One actual selected v113 Build, no F/O/DPS; observe bonus-only Native."""
import argparse,json,tempfile,pathlib
from p1_v769_incremental_environment_once import (
    BUILD,REV,EphemeralActionsCredentials,digest)
import v113_local_web_api as web

def main():
    parser=argparse.ArgumentParser()
    for arg in ("simc","identity","out"):
        parser.add_argument("--"+arg,type=pathlib.Path,required=True)
    args=parser.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    report={"schema":"p1_v829_selected_actual_socket_bonus_once_v1",
            "status":"STARTED","game_build":BUILD,"simc_revision":REV,
            "selected_special_gem_id":240983,"requested_socket_total":5,
            "dps_native_calls":0,"game_socket_legal_verified":False,
            "environment_installed":False}
    def save():
        raw=json.dumps(report,sort_keys=True,ensure_ascii=True,allow_nan=False)
        (out/"V829_SELECTED_SOCKET_BONUS.json").write_text(raw+"\n","utf8")
        print("V829_RECEIPT "+raw,flush=True)
    try:
        binary=args.simc.resolve(strict=True)
        identity=json.loads(args.identity.read_text("utf-8-sig"))
        if (identity["game_build"]!=BUILD or identity["source_commit"]!=REV
                or digest(binary)!=identity["binary_sha256"]):
            raise RuntimeError("V829_PINNED_BINARY_IDENTITY_DRIFT")
        report["binary_sha256"]=identity["binary_sha256"]
        save()
        with tempfile.TemporaryDirectory(prefix="v829-") as tmp:
            root=pathlib.Path(tmp)/"runs";root.mkdir()
            credentials=EphemeralActionsCredentials()
            if credentials.load() is None:raise RuntimeError("V829_SOURCE_CREDENTIALS_MISSING")
            app=web.create_app(root=root,token="v829-local-only",
                               source_credential_store=credentials)
            env=app.state.jobs.build_season_environment(
                game_build=BUILD,target_ilevel=334,native_G_binary=str(binary),
                auto_native_F_requested=False,auto_native_O_requested=False,
                existing_special_gem_id=240983,source_target_socket_count=5,
                simc_revision_hint=REV)
            comp=env.get("source_compilation") or {}
            progress=env.get("zero_history_build") or {}
            report.update(environment_installed=env.get("environment_installed") is True,
                new_native_calls=env.get("native_calls"),
                G_native_status=(env.get("native_G_numeric_source") or {}).get("status"),
                layout=comp.get("physical_gem_layout_unadmitted"),
                selected_socket_bonus_native=comp.get("selected_socket_bonus_native"),
                source_supported_socket_candidate=progress.get("source_supported_socket_candidate"),
                requires=progress.get("requires"))
            save()
            proof=report["selected_socket_bonus_native"] or {}
            if proof.get("status")!="EXACT_SIMC_SOCKET_BONUS_STATIC_BOUND":
                raise RuntimeError("V829_ACTUAL_SELECTED_BONUS_NATIVE_PROOF_PENDING")
            if (proof["new_native_calls"]!=1 or report["layout"]["socket_total"]!=5
                    or report["layout"]["ordinary_count"]!=4):
                raise RuntimeError("V829_ACTUAL_SELECTED_SCOPE_DRIFT")
            report["status"]="PASS_ACTUAL_SELECTED_SOCKET_BONUS_STATIC_NOT_INSTALLED"
            save()
        return 0
    except Exception as exc:
        report["status"]="BLOCKED_ACTUAL_SELECTED_SOCKET_BONUS"
        report["first_blocker"]=str(exc).split(":",1)[0].split("\n",1)[0][:200]
        save()
        return 2

if __name__=="__main__":
    raise SystemExit(main())
