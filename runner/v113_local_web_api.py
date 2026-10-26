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
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

import v106_user_session_controller as sessions
import v098_target_user_scenario_bootstrap as bootstrap

SCHEMA = "v113_local_web_api_p1_v1"
KEY = re.compile(r"[a-f0-9]{20}\Z")
LOCAL_HOST = "127.0.0.1"

class UserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    controls: dict
    binary: str = Field(min_length=1, max_length=4096)
    revision: str = Field(min_length=7, max_length=40)
    static_cache: str | None = Field(default=None, max_length=4096)

def blocked(exc):
    """Return stable codes, not private absolute paths, talent strings, or tracebacks."""
    if isinstance(exc, (sessions.SessionBlocked, bootstrap.UserScenarioBlocked)):
        code = str(exc).split(":", 1)[0].split("\n", 1)[0]
        return HTTPException(422, detail={"code": code})
    return HTTPException(409, detail={"code": "LOCAL_SESSION_PRECHECK_BLOCKED",
                                       "kind":type(exc).__name__})

class LocalJobs:
    def __init__(self, root):
        self.root = pathlib.Path(root).expanduser().resolve()
        self.lock = threading.Lock()
        self.children = {}

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
            folder = sessions.store_session(user,self.root,binary,params.revision,
                                            params.static_cache)
            plan = bootstrap.build(user,folder / "generated",binary,
                                   params.revision,params.static_cache)["plan"]
            return {"session_id":folder.name,"status":"READY_ZERO_NATIVE",
                    "native_calls":0,"plan":{
                      "class":plan["class"],"spec":plan["spec"],
                      "base_B":plan["base_B"],
                      "fixed_O":plan["fixed_O"],"final_T":plan["final_T"],
                      "native_limit":plan["native_limit"],
                      "native_called":False}}
        except Exception as exc:
            raise blocked(exc) from None

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
            key, check = sessions.session_key(user,binary,rev,static)
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
        # A worker can survive an HTTP server restart; OS lock, not the
        # persisted RUNNING string, is authoritative for live activity.
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
                "result_ready":p["final"].is_file()}

    def launch(self, folder, *, cache_only=False):
        with self.lock:
            if self.is_active(folder):
                raise HTTPException(409,detail={"code":"SESSION_ALREADY_RUNNING"})
            try:
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
                "new_native_limit":0 if cache_only else 6}

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

def create_app(*,root=None, token=None):
    jobs=LocalJobs(root or sessions.DEFAULT_ROOT)
    key=token or secrets.token_urlsafe(32)
    app=FastAPI(title="SIMC Secondary Optimizer LOCAL API",
                version="113.0",openapi_url=None,docs_url=None,redoc_url=None)
    app.state.jobs=jobs

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
        if request.url.path not in ("/api/v1/health","/api/v1/bootstrap"):
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
        return await call_next(request)

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
        return {"archetypes":[{"class":cl,"spec":sp,
                               **sessions.standard_controls((cl,sp))}
                              for cl,sp in sessions.SUPPORTED]}

    @app.post("/api/v1/sessions/plan")
    def plan(request: UserRequest):
        return jobs.plan(request)

    @app.post("/api/v1/sessions/start")
    def start(request: UserRequest):
        prepared=jobs.plan(request)
        folder=jobs.folder(prepared["session_id"])
        return jobs.launch(folder)

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

    @app.get("/api/v1/sessions/{session_id}/result")
    def result(session_id: str):
        return jobs.result(jobs.folder(session_id))
    return app

def main(argv=None):
    import argparse
    p=argparse.ArgumentParser(description="P1-WEB-1 local HTTP API, no UI yet")
    p.add_argument("--host",default=LOCAL_HOST,choices=[LOCAL_HOST])
    p.add_argument("--port",type=int,default=8765)
    args=p.parse_args(argv)
    if not 1024<=args.port<=65535:
        p.error("PORT_MUST_BE_1024_TO_65535")
    import uvicorn
    print(f"SIMC_LOCAL_API http://{LOCAL_HOST}:{args.port}/api/v1/health",
          flush=True)
    uvicorn.run(create_app(),host=LOCAL_HOST,port=args.port,
                proxy_headers=False,access_log=False)

if __name__=="__main__":
    main()
