#!/usr/bin/env python3
"""v113 P1-WEB-1: loopback-only HTTP adapter to EXISTING user/SimC worker.

Thin adapter; no optimizer, SimC mechanics, HTML app, or cloud execution.
The browser loads its per-process token from same-origin /api/v1/bootstrap.
Server listens on 127.0.0.1 only. File paths are never accepted as session IDs.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import secrets
import subprocess
import sys
import threading
import tempfile
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field

import v106_user_session_controller as sessions
import v098_target_user_scenario_bootstrap as bootstrap
import v108_native_consumable_inputs as consumables
import v188_user_choice_metadata as choice_labels
import v196_current_season_user_catalog as ui_catalog
import v193_simc_local_updater as simc_updates
import v148_local_batch_results as batch_view
import v167_product_season_gear_adapter as season_gear
import v208_internal_exact_special_L_hydrator as exact_L
import v212_environment_manifest as environment_manifest

SCHEMA = "v113_local_web_api_p1_v1"
KEY = re.compile(r"[a-f0-9]{20}\Z")
LOCAL_HOST = "127.0.0.1"
WEB_ASSETS = pathlib.Path(__file__).resolve().parent / "webui"
PUBLIC_STATIC = frozenset(("/", "/assets/app.js", "/assets/styles.css"))

class UpdateInstallRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    filename: str = Field(min_length=12,max_length=140)

class UpdateLocalArchiveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    archive_path: str = Field(min_length=8,max_length=4096)

class UserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    controls: dict
    binary: str = Field(min_length=1, max_length=4096)
    revision: str = Field(min_length=7, max_length=40)
    static_cache: str | None = Field(default=None, max_length=4096)
    current_season_product: bool = False

def blocked(exc):
    """Return stable codes, not private absolute paths, talent strings, or tracebacks."""
    if isinstance(exc, (sessions.SessionBlocked, bootstrap.UserScenarioBlocked,
                        sessions.nonchmv_enchant.EnchantChoiceBlocked,
                        exact_L.StaticLBlocked,
                        environment_manifest.EnvironmentBlocked)):
        code = str(exc).split(":", 1)[0].split("\n", 1)[0]
        return HTTPException(422, detail={"code": code})
    # Exact special L is a user-actionable, pre-Native input mismatch.
    # Only these fixed codes escape; arbitrary exception text can expose
    # private paths, options or SimC content and must remain generic.
    reference = bootstrap.oil_mod.reference_path
    if isinstance(exc, reference.ReferenceNativeBlocked):
        if str(exc) in ("SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT",
                        "REFERENCE_FIXED_L_CONSTRAINT_UNRESOLVED"):
            return HTTPException(422, detail={"code": str(exc)})
    if isinstance(exc, reference.statics.BudgetBlocked):
        if str(exc) == "SELECTED_SPECIAL_FLOOR_UNFEASIBLE":
            return HTTPException(422, detail={"code": str(exc)})
    return HTTPException(409, detail={"code": "LOCAL_SESSION_PRECHECK_BLOCKED",
                                       "kind":type(exc).__name__})

class LocalJobs:
    def __init__(self, root):
        self.root = pathlib.Path(root).expanduser().resolve()
        self.lock = threading.Lock()
        self.children = {}
        self.static_lock = threading.Lock()

    def default_static_cache(self, user, requested):
        """Reuse an existing same-PC static cache; never create L or call SimC.

        Optional user-specified paths retain prior behavior and identity.
        The stable app-local file is used only for selected specials; normal
        sessions and old sealed caches are unchanged.
        """
        if requested is not None or not user.get("special_items"):
            return requested
        candidate=exact_L.source_cache(self.root,None)
        return str(candidate) if candidate is not None else None

    def source_catalog_path(self):
        """Use the packaged v213 artifact when present; legacy source remains fallback."""
        candidate=pathlib.Path(__file__).resolve().parents[1]/"data"/"current_season_source_to_catalog.json"
        return candidate if candidate.is_file() else None

    def package_manifest_path(self):
        """Return the exact package-root manifest, never infer from a ZIP filename."""
        candidate=pathlib.Path(__file__).resolve().parents[1]/"V181_PACKAGE_MANIFEST.json"
        return candidate if candidate.is_file() and not candidate.is_symlink() else None

    @staticmethod
    def _write_atomic(path, encoded):
        path=pathlib.Path(path)
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.is_file() and path.read_text(encoding="utf8")==encoded:
            return path
        fd,temp=tempfile.mkstemp(prefix=".environment-manifest-",dir=path.parent)
        try:
            with os.fdopen(fd,"w",encoding="utf8") as stream:
                stream.write(encoded);stream.flush();os.fsync(stream.fileno())
            os.replace(temp,path)
        finally:
            if os.path.exists(temp):os.unlink(temp)
        return path

    @staticmethod
    def _environment_summary(document):
        payload={k:v for k,v in document.items() if k!="manifest_sha256"}
        digest=environment_manifest.sha(
            environment_manifest.canonical(payload).encode("utf8"))
        if digest!=document.get("manifest_sha256"):
            raise environment_manifest.EnvironmentBlocked(
                "ENVIRONMENT_MANIFEST_DIGEST_MISMATCH")
        source=document.get("source_catalog") or {}
        package=document.get("windows_package") or {}
        scope=document.get("product_scope") or {}
        receipt=document.get("v208_start_receipt") or {}
        return {
            "schema":document.get("schema"),
            "status":document.get("status"),
            "manifest_sha256":digest,
            "source_catalog_sha256":source.get("artifact_sha256"),
            "source_catalog_manifest_sha256":source.get("manifest_sha256"),
            "windows_package_status":package.get("status","NOT_PROVIDED"),
            "windows_package_manifest_sha256":package.get("manifest_sha256"),
            "all_specs_ready":scope.get("all_specs_ready"),
            "profile_supplier_coverage":scope.get("profile_supplier_coverage"),
            "dependency_change":document.get("dependency_change"),
            "v208_start_receipt_status":receipt.get("status"),
            "unresolved_dependencies":list(document.get(
                "unresolved_dependencies",[])),
            "native_calls":document.get("native_calls"),
            "network_calls":document.get("network_calls"),
        }

    def _read_environment_summary(self, folder):
        path=pathlib.Path(folder)/"generated"/"environment_manifest.json"
        if not path.is_file():
            return None
        try:
            document=json.loads(path.read_text(encoding="utf8"))
            if type(document) is not dict:
                raise ValueError("ENVIRONMENT_MANIFEST_OBJECT_REQUIRED")
            return self._environment_summary(document)
        except (OSError,ValueError,TypeError,KeyError) as exc:
            raise environment_manifest.EnvironmentBlocked(
                "ENVIRONMENT_MANIFEST_INVALID:"+type(exc).__name__) from exc

    def _verify_environment_dependencies(self, summary, folder=None):
        if not summary:
            return
        source_path=self.source_catalog_path()
        if summary.get("source_catalog_sha256"):
            if source_path is None or folder is None:
                raise environment_manifest.EnvironmentBlocked(
                    "V213_PACKAGED_SOURCE_REMOVED_AFTER_PLAN")
            source_doc,source_sha=environment_manifest.read_json(source_path)
            if source_sha!=summary.get("source_catalog_sha256"):
                raise environment_manifest.EnvironmentBlocked(
                    "V213_SOURCE_CATALOG_CHANGED_AFTER_PLAN")
            try:
                session_identity=json.loads(
                    (pathlib.Path(folder)/"V106_SESSION_IDENTITY.json")
                    .read_text(encoding="utf8"))
            except (OSError,ValueError,TypeError) as exc:
                raise environment_manifest.EnvironmentBlocked(
                    "V213_SESSION_SOURCE_IDENTITY_MISSING") from exc
            bound=session_identity.get("current_season_source_catalog")
            if (type(bound) is not dict or
                bound.get("artifact_sha256")!=source_sha or
                bound.get("manifest_sha256")!=summary.get(
                    "source_catalog_manifest_sha256") or
                bound.get("game_build")!=source_doc.get("game_build") or
                bound.get("simc_revision")!=source_doc.get("simc_revision")):
                raise environment_manifest.EnvironmentBlocked(
                    "V213_SESSION_SOURCE_IDENTITY_MISMATCH")
            package_path=self.package_manifest_path()
            if summary.get("windows_package_status")=="VERIFIED":
                if package_path is None:
                    raise environment_manifest.EnvironmentBlocked(
                        "V213_PACKAGED_SOURCE_REMOVED_AFTER_PLAN")
                package_raw=package_path.read_bytes()
                if bound.get("package_manifest_sha256")!=sessions.sha(package_raw):
                    raise environment_manifest.EnvironmentBlocked(
                        "V181_SESSION_PACKAGE_IDENTITY_MISMATCH")
                package=environment_manifest.verify_windows_package_manifest(
                    package_path,source_path,source_doc,source_sha)
                if package.get("manifest_sha256")!=summary.get(
                        "windows_package_manifest_sha256"):
                    raise environment_manifest.EnvironmentBlocked(
                        "V181_PACKAGE_MANIFEST_CHANGED_AFTER_PLAN")

    def _latest_v208_receipt_path(self, folder):
        pointer=pathlib.Path(folder)/"V208_START_RECEIPT_REF.json"
        if not pointer.is_file():
            return None
        try:
            record=json.loads(pointer.read_text(encoding="utf8"))
            relative=record.get("path")
            if (record.get("schema")!="v113_v208_start_receipt_pointer_v1" or
                type(relative) is not str or not relative or
                pathlib.Path(relative).is_absolute() or
                ".." in pathlib.PurePosixPath(relative.replace("\\","/")).parts):
                raise ValueError("V208_RECEIPT_POINTER_INVALID")
            root=pathlib.Path(folder).resolve()
            target=(root/relative).resolve()
            if not target.is_relative_to(root) or not target.is_file():
                raise ValueError("V208_RECEIPT_POINTER_TARGET_INVALID")
            receipt=json.loads(target.read_text(encoding="utf8"))
            if receipt.get("receipt_sha256")!=record.get("receipt_sha256"):
                raise ValueError("V208_RECEIPT_POINTER_DIGEST_MISMATCH")
            return target
        except (OSError,ValueError,TypeError,KeyError) as exc:
            raise environment_manifest.EnvironmentBlocked(
                "V208_RECEIPT_POINTER_INVALID:"+type(exc).__name__) from exc

    def _record_v208_receipt(self, folder, receipt_info):
        relative=receipt_info.get("path")
        if type(relative) is not str or not relative:
            raise environment_manifest.EnvironmentBlocked(
                "V208_RECEIPT_RELATIVE_PATH_REQUIRED")
        pointer={
            "schema":"v113_v208_start_receipt_pointer_v1",
            "path":relative,
            "receipt_sha256":receipt_info.get("receipt_sha256"),
        }
        encoded=json.dumps(pointer,sort_keys=True,ensure_ascii=False,
                           indent=2,allow_nan=False)+"\n"
        self._write_atomic(pathlib.Path(folder)/"V208_START_RECEIPT_REF.json",encoded)

    def _seal_environment_manifest(self, folder, bootstrap_result,
                                   receipt_path=None):
        generated=pathlib.Path(folder)/"generated"
        bootstrap_path=generated/"v098_bootstrap_result.json"
        encoded_bootstrap=json.dumps(bootstrap_result,sort_keys=True,
            ensure_ascii=False,indent=2,allow_nan=False)+"\n"
        # Persist v098 output even for a legacy package without v213. A later
        # explicit Start still needs the exact bootstrap identity for v208.
        bootstrap.put_once(bootstrap_path,encoded_bootstrap)
        source_path=self.source_catalog_path()
        if source_path is None:
            return {"status":"SOURCE_CATALOG_NOT_PACKAGED",
                    "windows_package_status":"NOT_VERIFIED",
                    "all_specs_ready":bootstrap_result.get("all_specs_ready"),
                    "profile_supplier_coverage":bootstrap_result.get(
                        "profile_supplier_coverage"),
                    "v208_start_receipt_status":"NOT_VERIFIED",
                    "unresolved_dependencies":[
                        "V213_SOURCE_CATALOG_NOT_PACKAGED"],
                    "native_calls":0,"network_calls":0}
        if receipt_path is None:
            receipt_path=self._latest_v208_receipt_path(folder)
        previous_path=generated/"environment_manifest.json"
        result=environment_manifest.compile_from_paths(
            source_path,bootstrap_path,generated,receipt_path,
            package_manifest_path=self.package_manifest_path(),
            previous_manifest_path=(previous_path
                if previous_path.is_file() else None))
        encoded=json.dumps(result,sort_keys=True,ensure_ascii=False,
                          indent=2,allow_nan=False)+"\n"
        self._write_atomic(generated/"environment_manifest.json",encoded)
        return self._environment_summary(result)

    def recent_sessions(self, limit=48):
        """Read-only local session index; no binary hashing, Native or writes.

        A session is listed only when its copied user bytes and sealed v106
        identity agree with its directory hash. No talents, paths, options
        or trinket IDs leave this endpoint; list is advisory, not authorization.
        Start/resume still performs complete current-binary/cache verification.
        """
        if not self.root.is_dir():
            return {"sessions":[],"read_only":True,"native_calls_now":0}
        candidates=[]
        for folder in self.root.iterdir():
            if (not KEY.fullmatch(folder.name) or folder.is_symlink()
                    or not folder.is_dir()):
                continue
            try:
                seal=folder/"V106_SESSION_IDENTITY.json"
                user_file=folder/"user.json"
                if not seal.is_file() or not user_file.is_file():
                    continue
                # An adversarial or corrupted local file must not force
                # unbounded parsing on a frequently visited UI screen.
                if seal.stat().st_size>524288 or user_file.stat().st_size>524288:
                    continue
                identity=json.loads(seal.read_text(encoding="utf8"))
                user=json.loads(user_file.read_text(encoding="utf8"))
                if (type(identity) is not dict or type(user) is not dict
                        or identity.get("schema")!=sessions.SCHEMA
                        or identity.get("user")!=user
                        or sessions.sha(sessions.canonical(identity).encode("utf8"))[:20]
                           !=folder.name):
                    continue
                character=user.get("character")
                target=user.get("target")
                if (type(character) is not dict or type(target) is not dict
                        or type(character.get("class")) is not str
                        or type(character.get("spec")) is not str
                        or (character["class"],character["spec"]) not in
                           sessions.SUPPORTED
                        or type(target.get("ilevel")) is not int
                        or type(identity.get("simc_revision")) is not str
                        or re.fullmatch(r"[0-9a-fA-F]{7,40}",
                                        identity["simc_revision"]) is None
                        or type(identity.get("independent_334",False)) is not bool):
                    continue
                state_file=folder/"V106_WORKER_STATE.json"
                result_file=folder/"V106_USER_RESULT.json"
                status="NOT_STARTED"
                if state_file.is_file():
                    if state_file.stat().st_size>16384:
                        continue
                    recorded=json.loads(state_file.read_text(encoding="utf8"))
                    if (type(recorded) is not dict or
                            recorded.get("schema")!=sessions.SCHEMA or
                            type(recorded.get("status")) is not str):
                        continue
                    status=recorded["status"]
                source=(state_file if state_file.is_file() else seal)
                candidates.append((source.stat().st_mtime,{
                    "session_id":folder.name,
                    "class":character["class"],"spec":character["spec"],
                    "target_ilevel":target["ilevel"],
                    "recorded_status":status,
                    "result_saved":result_file.is_file(),
                    "independent_target334_profile":
                        identity.get("independent_334",False),
                    "updated_unix":int(source.stat().st_mtime)}))
            except (OSError,ValueError,TypeError,KeyError,OverflowError):
                # Corrupt single session is ignored; other sessions survive.
                continue
        candidates.sort(key=lambda item:(-item[0],item[1]["session_id"]))
        return {"sessions":[item for _,item in candidates[:limit]],
                "read_only":True,"native_calls_now":0}

    def folder(self, key):
        if not KEY.fullmatch(key):
            raise HTTPException(404, detail={"code":"SESSION_ID_INVALID"})
        # A key alone is not a user-supplied filesystem path.
        folder = (self.root / key).resolve()
        if not folder.is_relative_to(self.root) or not folder.is_dir():
            raise HTTPException(404, detail={"code":"SESSION_NOT_FOUND"})
        if not (folder / "V106_SESSION_IDENTITY.json").is_file():
            raise HTTPException(404, detail={"code":"SESSION_NOT_FOUND"})
        return folder

    def plan(self, params):
        try:
            user = sessions.user_scenario(params.controls)
            binary = pathlib.Path(params.binary).expanduser().resolve()
            resolved_static=self.default_static_cache(user,params.static_cache)
            # 24 source-independent v147-proven representative archetypes:
            # user-selected target334 gets its own sealed product identity.
            # Legacy sessions and non-334 plans keep the original route.
            ch=user["character"]
            key=(ch["class"],ch["spec"])
            current_season=params.current_season_product
            independent=(not current_season and user["target"]["ilevel"]==334 and
                         key in bootstrap.ARCHETYPES)
            independent_level=(not current_season and user["target"]["ilevel"]!=334 and
                               key in sessions.SUPPORTED)
            source_catalog_path=self.source_catalog_path()
            package_manifest_path=self.package_manifest_path()
            folder = sessions.store_session(user,self.root,binary,params.revision,
                                            resolved_static,
                                            independent_334=independent,
                                            independent_target_level=independent_level,
                                            current_season_product=current_season,
                                            source_catalog_path=(source_catalog_path
                                                if current_season else None),
                                            package_manifest_path=(package_manifest_path
                                                if current_season and source_catalog_path
                                                else None))
            # Session identity binds CACHE CONTENT, not its user-visible
            # path. If the same bytes are passed via a different path later,
            # honor the already-sealed manifest path rather than rewriting
            # immutable generated files or causing a needless new session.
            prior=folder/"generated"/"manifest.json"
            if resolved_static and prior.is_file():
                previous=json.loads(prior.read_text(encoding="utf8"))
                saved=previous.get("static_cache_json")
                if (type(saved) is str and saved!=str(
                        pathlib.Path(resolved_static).resolve())):
                    old=pathlib.Path(saved)
                    if (old.is_file() and
                        sessions.sha(old.read_bytes())==
                        sessions.sha(pathlib.Path(resolved_static).read_bytes())):
                        resolved_static=saved
            bootstrap_result = bootstrap.build(
                user,folder / "generated",binary,params.revision,resolved_static,
                independent_334=independent,
                independent_target_level=independent_level,
                current_season_product=current_season,
                source_catalog_path=source_catalog_path)
            plan=bootstrap_result["plan"]
            environment=(self._seal_environment_manifest(folder,bootstrap_result)
                         if current_season else None)
            return {"session_id":folder.name,"status":"READY_ZERO_NATIVE",
                    "environment_manifest":environment,
                    "native_calls":0,
                    "static_cache_auto_used":bool(
                        resolved_static and params.static_cache is None),
                    "plan":{
                      "class":plan["class"],"spec":plan["spec"],
                      "base_B":plan["base_B"],
                      "fixed_O":plan["fixed_O"],"final_T":plan["final_T"],
                      "native_limit":plan["native_limit"],
                      "native_called":False,
                      "independent_target334_profile":independent,
                      "independent_non334_profile":independent_level,
                      "non334_physical_native_not_yet_observed":(
                          independent_level or
                          (current_season and user["target"]["ilevel"]!=334)),
                      "current_season_product":current_season,
                      "v176_26_of_26_base_physical_native":(
                          current_season and user["target"]["ilevel"]==334)}}
        except Exception as exc:
            raise blocked(exc) from None

    def start_with_internal_special_L(self, params):
        """Explicit /start only: one cached, exact static Native on missing L.

        Never modify an already sealed old static cache/session. The one
        physical SimC probe is separate from the six DPS optimizer calls.
        The ordinary /plan endpoint remains strictly zero Native.
        """
        user=sessions.user_scenario(params.controls)
        hydrated=None
        prepared_params=params
        if params.current_season_product and user["special_items"]:
            binary=pathlib.Path(params.binary).expanduser().resolve()
            with self.static_lock:
                source=self.default_static_cache(user,params.static_cache)
                try:
                    hydrated=exact_L.hydrate(
                        user,self.root,binary,params.revision,
                        existing=source,
                        source_catalog_path=self.source_catalog_path())
                except Exception as exc:
                    raise blocked(exc) from None
                prepared_params=params.model_copy(update={
                    "static_cache":hydrated["static_cache_path"]})
        prepared=self.plan(prepared_params)
        folder=self.folder(prepared["session_id"])
        if hydrated:
            receipt_info=exact_L.write_start_receipt(
                folder,hydrated["start_receipt"])
            self._record_v208_receipt(folder,receipt_info)
            bootstrap_path=folder/"generated"/"v098_bootstrap_result.json"
            bootstrap_result=json.loads(bootstrap_path.read_text(encoding="utf8"))
            environment=self._seal_environment_manifest(
                folder,bootstrap_result,folder/receipt_info["path"])
        else:
            environment=prepared.get("environment_manifest")
        # The environment manifest is sealed before the optimizer worker is
        # launched, so Start never outruns its exact v213/v208 provenance.
        response=self.launch(folder)
        if hydrated:
            response["static_L_start_receipt"]=receipt_info
        response["environment_manifest"]=environment
        response["static_L_native_calls_this_start"]=(
            hydrated["native_new_calls"] if hydrated else 0)
        response["static_L_reused_exact_variants"]=(
            hydrated["cache_reused"] if hydrated else 0)
        return response

    def args_for_existing(self, folder):
        """Recover binary/options from self-generated manifest, verify v106 identity."""
        m = folder / "generated" / "manifest.json"
        if not m.is_file():
            raise HTTPException(409,detail={"code":"SESSION_MANIFEST_MISSING"})
        try:
            manifest = json.loads(m.read_text(encoding="utf8"))
            user = json.loads((folder / "user.json").read_text(encoding="utf8"))
            recorded = json.loads((folder / "V106_SESSION_IDENTITY.json").read_text(
                encoding="utf8"))
            binary = pathlib.Path(manifest["native_binary"]).resolve()
            rev = manifest["native_revision"]
            static = manifest["static_cache_json"]
            # A manually staged, internal ordinary-gear variant may be
            # resumed under its own sealed identity. Browser planning still
            # creates DEFAULT variants only; never infer one from user gear.
            variant = recorded.get("ordinary_variant")
            key, check = sessions.session_key(
                user,binary,rev,static,ordinary_variant=variant,
                independent_334=recorded.get("independent_334",False),
                independent_target_level=recorded.get("independent_target_level",False),
                current_season_product=bool(recorded.get("current_season_product",False)))
            if key != folder.name or check != recorded:
                raise sessions.SessionBlocked("SESSION_BINARY_REVISION_OR_CACHE_DRIFT")
            return binary,rev,static
        except HTTPException:
            raise
        except Exception as exc:
            raise blocked(exc) from None

    def is_active(self, folder):
        key = folder.name
        child = self.children.get(key)
        if child is not None and child.poll() is None:
            return True
        # Never CREATE lock files during GET/status; status is read-only.
        # A worker can survive an HTTP server restart: check an existing
        # OS lock rather than trusting the persisted RUNNING status.
        if not (folder / "V106_WORKER.lock").is_file():
            return False
        try:
            with sessions.worker_lock(folder):
                return False
        except sessions.SessionBlocked:
            return True

    def status(self, folder):
        item = sessions.progress(folder)
        p = sessions.paths(folder)
        return {"session_id":folder.name,"active":self.is_active(folder),
                "cancel_requested":p["cancel"].exists(),
                "progress":item,
                "result_ready":p["final"].is_file(),
                "environment_manifest":self._read_environment_summary(folder)}

    def inputs(self, folder):
        """Restore locally sealed user form/SimC paths, read-only and without Native.

        No binary hashing on every page refresh: actual identity and executable
        checks still belong to start/resume and the v106 session controller.
        """
        try:
            recorded = json.loads((folder / "V106_SESSION_IDENTITY.json").read_text(
                encoding="utf8"))
            user = json.loads((folder / "user.json").read_text(encoding="utf8"))
            manifest = json.loads((folder / "generated" / "manifest.json").read_text(
                encoding="utf8"))
            if (recorded.get("schema") != sessions.SCHEMA or
                user != recorded.get("user") or
                manifest.get("native_revision") != recorded.get("simc_revision") or
                not isinstance(manifest.get("native_binary"), str) or
                not manifest["native_binary"] or
                not isinstance(manifest.get("static_cache_json"), (str, type(None)))):
                raise sessions.SessionBlocked("SESSION_INPUTS_OR_MANIFEST_DRIFT")
            return {"schema": "v116_local_session_inputs_read_only_v1",
                    "session_id": folder.name, "user": user,
                    "binary": manifest["native_binary"],
                    "revision": recorded["simc_revision"],
                    "static_cache": manifest["static_cache_json"],
                    "current_season_product":bool(
                        recorded.get("current_season_product",False)),
                    "native_called": False}
        except Exception as exc:
            raise blocked(exc) from None

    def launch(self, folder, *, cache_only=False):
        with self.lock:
            if self.is_active(folder):
                raise HTTPException(409,detail={"code":"SESSION_ALREADY_RUNNING"})
            try:
                # Verify the sealed package/source identity before spawning a worker.
                environment=self._read_environment_summary(folder)
                self._verify_environment_dependencies(environment,folder)
                binary, rev, static = self.args_for_existing(folder)
                if cache_only:
                    sessions.cache_only_preflight(folder)
                else:
                    # Already-resolved identical manifest/user: real worker
                    # owns preparing/running without creating a new identity.
                    sessions.clear_cancel(folder)
                cmd = [sys.executable,
                       str(pathlib.Path(sessions.__file__).resolve()),
                       "--session",str(folder),"--binary",str(binary),
                       "--revision",rev]
                if static: cmd.extend(["--static-cache",str(static)])
                if cache_only: cmd.append("--cache-only")
                log = sessions.paths(folder)["log"]
                with log.open("a",encoding="utf8",buffering=1) as stream:
                    stream.write("\n=== V113 LOCAL API CACHE_ONLY ===\n"
                                 if cache_only else
                                 "\n=== V113 LOCAL API START / RESUME ===\n")
                    stream.flush()
                    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name=="nt" else 0
                    process = subprocess.Popen(cmd, stdin=subprocess.DEVNULL,
                             stdout=stream, stderr=subprocess.STDOUT,
                             creationflags=flags,
                             env={**os.environ,"PYTHONIOENCODING":"utf-8"})
                self.children[folder.name] = process
            except HTTPException:
                raise
            except Exception as exc:
                raise blocked(exc) from None
        return {"session_id":folder.name,
                "status":"CACHE_ONLY_WORKER_STARTED" if cache_only else "WORKER_STARTED",
                "native_attempt_ceiling_cumulative":6,
                "new_native_execution_permitted":not cache_only,
                "environment_manifest":environment}

    def cancel(self, folder):
        with self.lock:
            if not self.is_active(folder):
                raise HTTPException(409,detail={"code":"SESSION_NOT_RUNNING"})
            sessions.request_cancel(folder)
            return {"session_id":folder.name,
                    "status":"CANCEL_REQUESTED_AFTER_CURRENT_NATIVE"}

    def result(self, folder):
        path = sessions.paths(folder)["final"]
        if not path.is_file():
            raise HTTPException(404,detail={"code":"RESULT_NOT_READY"})
        try:
            data=json.loads(path.read_text(encoding="utf8"))
            text=sessions.format_result(data)
            return {"session_id":folder.name,
                    "status":data["status"],
                    "native_calls_cumulative":data["native_calls_cumulative"],
                    "cache_hits_this_run":data["cache_hits_this_run"],
                    "base_B":data["base_B"],"final_T":data["final_T"],
                    "user_result":data["user_result"],
                    "display_text":text}
        except Exception as exc:
            raise blocked(exc) from None

def create_app(*,root=None, token=None, batch_root=None, update_root=None,
               update_platform=None):
    jobs=LocalJobs(root or sessions.DEFAULT_ROOT)
    updater=simc_updates.SimCManager(
        update_root or (jobs.root.parent/"simc-managed"),platform=update_platform)
    snapshots=(pathlib.Path(batch_root).expanduser().resolve() if batch_root
               else pathlib.Path.home()/"SIMC_Secondary_Optimizer"/"v147_batch")
    key=token or secrets.token_urlsafe(32)
    app=FastAPI(title="SIMC Secondary Optimizer LOCAL API",
                version="113.0",openapi_url=None,docs_url=None,redoc_url=None)
    app.state.jobs=jobs
    app.state.simc_updates=updater

    @app.middleware("http")
    async def localhost_firewall(request: Request, call_next):
        raw_host=request.headers.get("host","")
        try:
            parsed=urlsplit("http://" + raw_host)
            valid_host=(parsed.hostname==LOCAL_HOST and
                        parsed.username is None and parsed.password is None and
                        parsed.path=="" and parsed.query=="" and parsed.fragment=="")
            port=parsed.port
        except ValueError:
            valid_host=False;port=None
        peer=request.client.host if request.client else None
        # 127.0.0.1 binding is enforced again in main(); this is a separate
        # DNS rebinding / non-loopback client defense.
        if not valid_host or peer not in ("127.0.0.1","::1","testclient"):
            return JSONResponse({"detail":{"code":"LOOPBACK_ONLY"}},403)
        expected_origin="http://" + raw_host
        origin=request.headers.get("origin")
        if origin is not None and origin != expected_origin:
            return JSONResponse({"detail":{"code":"FOREIGN_ORIGIN_BLOCKED"}},403)
        if request.headers.get("sec-fetch-site")=="cross-site":
            return JSONResponse({"detail":{"code":"CROSS_SITE_BLOCKED"}},403)
        if request.url.path not in ("/api/v1/health","/api/v1/bootstrap") and request.url.path not in PUBLIC_STATIC:
            if not secrets.compare_digest(
                request.headers.get("x-simc-local-token",""), key):
                return JSONResponse({"detail":{"code":"LOCAL_TOKEN_REQUIRED"}},403)
        if request.method in ("POST","PUT","PATCH","DELETE"):
            ct=request.headers.get("content-type","").split(";",1)[0].strip().lower()
            if ct!="application/json":
                return JSONResponse({"detail":{"code":"JSON_CONTENT_TYPE_REQUIRED"}},415)
            length=request.headers.get("content-length")
            if length:
                try:
                    large=int(length)>131072
                except ValueError:
                    return JSONResponse({"detail":{"code":"CONTENT_LENGTH_INVALID"}},400)
                if large:
                    return JSONResponse({"detail":{"code":"PAYLOAD_TOO_LARGE"}},413)
        response = await call_next(request)
        # No inline scripts, remote resources, or browser-side file/network APIs.
        # Token and local user output should not be cached by browser/proxy.
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self' data:; "
            "base-uri 'none'; form-action 'self'; frame-ancestors 'none'")
        return response

    @app.get("/")
    def index():
        return FileResponse(WEB_ASSETS / "index.html",media_type="text/html")

    @app.get("/assets/app.js")
    def browser_js():
        return FileResponse(WEB_ASSETS / "app.js",media_type="text/javascript")

    @app.get("/assets/styles.css")
    def browser_styles():
        return FileResponse(WEB_ASSETS / "styles.css",media_type="text/css")

    def updates_action(operation):
        # Downloads and managed-pointer changes require explicit browser POST.
        # A currently running SimC worker must not switch the UI's active binary.
        if any(jobs.is_active(jobs.root/sid) for sid in tuple(jobs.children)):
            raise HTTPException(409,detail={"code":"ACTIVE_SIMC_JOB_UPDATE_BLOCKED"})
        try:
            return operation()
        except simc_updates.UpdateBlocked as exc:
            raise HTTPException(422,detail={"code":str(exc)}) from None
        except (OSError,TimeoutError,ValueError,subprocess.SubprocessError) as exc:
            raise HTTPException(409,detail={"code":"OFFICIAL_SIMC_UPDATE_UNAVAILABLE",
                                           "kind":type(exc).__name__}) from None

    @app.get("/api/v1/simc-updates/status")
    def simc_update_status():
        return updates_action(updater.status)

    @app.post("/api/v1/simc-updates/check")
    def simc_update_check():
        return updates_action(updater.check)

    @app.post("/api/v1/simc-updates/install")
    def simc_update_install(request:UpdateInstallRequest):
        return updates_action(lambda:updater.install(request.filename))

    @app.post("/api/v1/simc-updates/install-local")
    def simc_update_install_local(request:UpdateLocalArchiveRequest):
        return updates_action(lambda:updater.install_local(request.archive_path))

    @app.post("/api/v1/simc-updates/rollback")
    def simc_update_rollback():
        return updates_action(updater.rollback)

    @app.get("/api/v1/season-option-catalog")
    def season_option_catalog():
        """Local, read-only versioned source catalogue; no Native or approvals."""
        try:
            source_path=jobs.source_catalog_path()
            return ui_catalog.public_options(source_path) if source_path else ui_catalog.public_options()
        except (ui_catalog.CatalogBlocked, OSError, ValueError, KeyError,
                AssertionError) as exc:
            return {"schema":ui_catalog.SCHEMA,
                    "status":"SOURCE_OPTION_CATALOG_UNAVAILABLE",
                    "detail_code":type(exc).__name__,
                    "proven_native_input_choices":{},
                    "enchant_candidates":{"total":0,"groups":{},
                                          "items":[],"selectable_count":0},
                    "native_calls_now":0,"new_approval_granted":False}

    @app.get("/api/v1/options")
    def options():
        return {
            "food":["source_default",*sorted(consumables.SUPPORTED["food"])],
            "potion":["source_default",*sorted(consumables.SUPPORTED["potion"])],
            "augmentation":["source_default",*sorted(consumables.SUPPORTED["augmentation"])],
            "diamond_id":[0,*sorted(consumables.DIAMONDS)],
            "omnium_talents":["source_default",*sorted(consumables.OMNIUM_PRESETS)],
            "display_labels":choice_labels.labels(),
            "embellishments":choice_labels.public_embellishments()
        }

    @app.get("/api/v1/season-gear")
    def current_season_gear():
        """User-facing seasonal effect choices; plain items stay internal."""
        try:
            return season_gear.public_options(season_gear.read())
        except (season_gear.GearBlocked, ValueError, OSError, KeyError) as exc:
            return {"schema":season_gear.SCHEMA,
                    "status":"SEASON_GEAR_CATALOG_UNAVAILABLE",
                    "choices":{k:[] for k in ("trinket","special_effect_gear_candidate","selectable_stat_craft")},
                    "count":0,"manual_exact_id_allowed":False,
                    "manual_exact_id_exception":"CRAFTED_EQUIPMENT_VARIANTS_ONLY",
                    "ordinary_equipment_user_selectable":False,
                    "full_season_completeness_confirmed":False,
                    "native_calls_now":0}

    @app.get("/api/v1/native-batches")
    def native_batches():
        return {"schema":batch_view.SCHEMA,
                "batches":batch_view.find_batches(snapshots),
                "native_calls_now":0,
                "mode":"LOCAL_COPIED_REPORT_READ_ONLY"}

    @app.get("/api/v1/native-batches/{batch_id}/results")
    def native_batch_results(batch_id: str):
        try:
            return batch_view.view_batch(snapshots,batch_id)
        except batch_view.BatchViewBlocked as exc:
            # Do not return original path, source profile or raw SimC JSON.
            raise HTTPException(422,detail={"code":str(exc).split(":",1)[0]}) from None

    @app.get("/api/v1/sessions")
    def recent_sessions():
        return jobs.recent_sessions()

    @app.get("/api/v1/health")
    def health():
        return {"schema":SCHEMA,"mode":"LOCAL_ONLY",
                "native_called_by_health":False,"supported_dps":len(sessions.SUPPORTED)}

    @app.get("/api/v1/bootstrap")
    def browser_bootstrap():
        return {"schema":SCHEMA,"session_token":key,
                "supported":[{"class":cl,"spec":spec}
                             for cl,spec in sessions.SUPPORTED],
                "local_only":True}

    @app.get("/api/v1/defaults")
    def defaults():
        # Compact v146 starters and season representative catalog now serve
        # all 26 DPS without legacy complete source .simc fixtures.
        # A plan for the 24 new cases selects the independent path only at
        # target334; non-334 retains a separate historical source-backed route.
        archetypes=[]
        for pair in sessions.SUPPORTED:
            controls=sessions.standard_controls(pair)
            scope=("SOURCE_INDEPENDENT_SEASON_CATALOG"
                   if pair in bootstrap.PURE_PRODUCT_SPECS else
                   "SOURCE_INDEPENDENT_TARGET334_VALIDATED_BATCH")
            archetypes.append({"class":pair[0],"spec":pair[1],**controls,
                               "representative_scope":scope})
        return {"archetypes":archetypes,
                "unavailable_missing_legacy_fixtures":[]}

    @app.post("/api/v1/sessions/plan")
    def plan(request: UserRequest):
        return jobs.plan(request)

    @app.post("/api/v1/sessions/start")
    def start(request: UserRequest):
        return jobs.start_with_internal_special_L(request)

    @app.post("/api/v1/sessions/{session_id}/resume")
    def resume(session_id: str):
        return jobs.launch(jobs.folder(session_id))

    @app.post("/api/v1/sessions/{session_id}/cache-only")
    def cache_only(session_id: str):
        return jobs.launch(jobs.folder(session_id),cache_only=True)

    @app.post("/api/v1/sessions/{session_id}/cancel")
    def cancel(session_id: str):
        return jobs.cancel(jobs.folder(session_id))

    @app.get("/api/v1/sessions/{session_id}/status")
    def status(session_id: str):
        return jobs.status(jobs.folder(session_id))

    @app.get("/api/v1/sessions/{session_id}/inputs")
    def inputs(session_id: str):
        return jobs.inputs(jobs.folder(session_id))

    @app.get("/api/v1/sessions/{session_id}/result")
    def result(session_id: str):
        return jobs.result(jobs.folder(session_id))
    return app

def main(argv=None):
    import argparse
    p=argparse.ArgumentParser(description="P1-WEB-2 local HTML webapp with existing SimC engine")
    p.add_argument("--host",default=LOCAL_HOST,choices=[LOCAL_HOST])
    p.add_argument("--port",type=int,default=8765)
    p.add_argument("--batch-root",type=pathlib.Path,
                   help="Optional relocated v147_batch directory; read-only Native results, never cache relocation")
    p.add_argument("--open-browser",action="store_true",
                   help="Open local browser only after this own Uvicorn server starts")
    args=p.parse_args(argv)
    if not 1024<=args.port<=65535:
        p.error("PORT_MUST_BE_1024_TO_65535")
    import uvicorn
    url=f"http://{LOCAL_HOST}:{args.port}/"
    print("SIMC_LOCAL_WEB "+url,flush=True)
    app=create_app(batch_root=args.batch_root)
    if not args.open_browser:
        # Preserve original CLI behavior, sockets and Native/session inputs.
        uvicorn.run(app,host=LOCAL_HOST,port=args.port,
                    proxy_headers=False,access_log=False)
        return
    # Check THIS server's started flag; never open a different process's
    # occupant of port 8765 if our bind fails. No network or Native checks.
    import time
    import webbrowser
    server=uvicorn.Server(uvicorn.Config(
        app,host=LOCAL_HOST,port=args.port,
        proxy_headers=False,access_log=False))
    def open_when_started():
        for _ in range(150):
            if server.started:
                webbrowser.open(url,new=2)
                return
            if server.should_exit:
                return
            time.sleep(0.1)
    threading.Thread(target=open_when_started,daemon=True).start()
    server.run()

if __name__=="__main__":
    main()
