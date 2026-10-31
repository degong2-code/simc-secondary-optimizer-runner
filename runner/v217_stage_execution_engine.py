#!/usr/bin/env python3
"""Reusable receipt-backed Stage Execution Engine; feature-agnostic."""
from __future__ import annotations
import ast, hashlib, json, os, pathlib, re, tempfile

SCHEMA="v217_reusable_stage_execution_receipt_v1"
FINGERPRINT_SCHEMA="v217_python_module_dependency_fingerprint_v1"
STAGE_ID=re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z")
MAX_RECEIPT_BYTES=1_000_000
MAX_CODE_MODULES=256

class StageExecutionBlocked(ValueError): pass

def need(condition,code):
    if not condition: raise StageExecutionBlocked(code)

def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def module_dependency_fingerprint(entry_paths):
    """Hash transitive local Python imports; non-code data is declared separately."""
    entries=[pathlib.Path(p).expanduser().resolve() for p in entry_paths]
    need(bool(entries),"STAGE_CODE_ENTRY_REQUIRED")
    root=entries[0].parent
    need(all(p.is_file() and not p.is_symlink() and p.parent==root for p in entries),
         "STAGE_CODE_ENTRY_INVALID")
    def local_module(name):
        if not name:return None
        if name.startswith("runner."):name=name[7:]
        parts=name.split(".")
        if any(not p.isidentifier() for p in parts):return None
        source=root.joinpath(*parts).with_suffix(".py")
        package=root.joinpath(*parts,"__init__.py")
        if source.is_file() and not source.is_symlink():return source.resolve()
        if package.is_file() and not package.is_symlink():return package.resolve()
        return None
    pending=list(entries);visited={}
    while pending:
        path=pending.pop()
        if path in visited:continue
        need(path.is_file() and not path.is_symlink() and path.is_relative_to(root),
             "STAGE_CODE_DEPENDENCY_PATH_INVALID")
        raw=path.read_bytes()
        try:tree=ast.parse(raw.decode("utf8"),filename=str(path))
        except (UnicodeDecodeError,SyntaxError) as exc:
            raise StageExecutionBlocked("STAGE_CODE_DEPENDENCY_PARSE_FAILED:"+type(exc).__name__) from exc
        visited[path]=digest(raw)
        need(len(visited)<=MAX_CODE_MODULES,"STAGE_CODE_DEPENDENCY_CLOSURE_TOO_LARGE")
        imports=set()
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node,ast.ImportFrom) and node.level==0 and node.module:
                imports.add(node.module)
                imports.update(node.module+"."+alias.name for alias in node.names
                               if alias.name!="*")
        for name in sorted(imports):
            candidate=local_module(name)
            if candidate is not None and candidate not in visited:pending.append(candidate)
    files={p.relative_to(root).as_posix():v
           for p,v in sorted(visited.items(),key=lambda row:row[0].as_posix())}
    payload={"schema":FINGERPRINT_SCHEMA,"files":files}
    return {**payload,"sha256":digest(canonical(payload).encode("utf8")),
            "module_count":len(files)}

def _safe_paths(root,stage_id,outputs):
    need(type(stage_id) is str and STAGE_ID.fullmatch(stage_id),"STAGE_ID_INVALID")
    need(type(outputs) is dict and bool(outputs),"STAGE_OUTPUTS_OBJECT_REQUIRED")
    supplied=pathlib.Path(root).expanduser()
    need(not supplied.is_symlink(),"STAGE_ROOT_SYMLINK_BLOCKED")
    base=supplied.resolve()
    need(base.is_dir(),"STAGE_ROOT_INVALID")
    paths={}
    for name,relative in outputs.items():
        need(type(name) is str and STAGE_ID.fullmatch(name) is not None and
             type(relative) is str and bool(relative) and
             re.match(r"^[A-Za-z]:",relative) is None,"STAGE_OUTPUT_ENTRY_INVALID")
        rel=pathlib.PurePosixPath(relative.replace("\\","/"))
        need(not rel.is_absolute() and all(x not in ("",".","..") for x in rel.parts),
             "STAGE_OUTPUT_PATH_INVALID")
        target=base.joinpath(*rel.parts)
        need(target.resolve(strict=False).is_relative_to(base),
             "STAGE_OUTPUT_PATH_ESCAPES_ROOT")
        current=base
        for part in rel.parts[:-1]:
            current=current/part
            need(not current.is_symlink(),"STAGE_OUTPUT_PARENT_SYMLINK_BLOCKED")
        need(not target.is_symlink(),"STAGE_OUTPUT_SYMLINK_BLOCKED")
        paths[name]=(rel.as_posix(),target)
    receipt_dir=base/".stage_receipts"
    need(not receipt_dir.is_symlink(),"STAGE_RECEIPT_DIRECTORY_SYMLINK_BLOCKED")
    receipt=receipt_dir/(stage_id+".json")
    need(not receipt.is_symlink(),"STAGE_RECEIPT_SYMLINK_BLOCKED")
    return paths,receipt

def _atomic_write(path,raw):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    need(not path.parent.is_symlink() and not path.is_symlink(),
         "STAGE_RECEIPT_SYMLINK_BLOCKED")
    if path.is_file() and path.read_bytes()==raw:return False
    fd,tmp=tempfile.mkstemp(prefix=".v217-stage-",dir=path.parent)
    try:
        with os.fdopen(fd,"wb") as stream:
            stream.write(raw);stream.flush();os.fsync(stream.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    return True

def _seal(payload):
    return {**payload,"receipt_sha256":digest(canonical(payload).encode("utf8"))}

def _read_receipt(path):
    need(path.is_file() and not path.is_symlink() and
         path.stat().st_size<=MAX_RECEIPT_BYTES,"STAGE_RECEIPT_MISSING_OR_TOO_LARGE")
    try:doc=json.loads(path.read_text(encoding="utf8"))
    except (OSError,ValueError,TypeError) as exc:
        raise StageExecutionBlocked("STAGE_RECEIPT_INVALID:"+type(exc).__name__) from exc
    need(type(doc) is dict and doc.get("schema")==SCHEMA,"STAGE_RECEIPT_SCHEMA_INVALID")
    payload={k:v for k,v in doc.items() if k!="receipt_sha256"}
    need(doc.get("receipt_sha256")==digest(canonical(payload).encode("utf8")),
         "STAGE_RECEIPT_DIGEST_INVALID")
    return doc

def _input_sha(stage_id,version,inputs):
    need(type(version) is str and bool(version.strip()),"STAGE_VERSION_REQUIRED")
    need(type(inputs) is dict,"STAGE_INPUT_FINGERPRINTS_OBJECT_REQUIRED")
    return digest(canonical({"schema":SCHEMA,"stage_id":stage_id,
                             "stage_version":version,"inputs":inputs}).encode("utf8"))

def _check_identity(receipt,stage_id,version,input_sha,paths):
    need(receipt.get("stage_id")==stage_id and receipt.get("stage_version")==version
         and receipt.get("input_fingerprint")==input_sha,
         "STAGE_INPUT_FINGERPRINT_MISMATCH")
    need(receipt.get("output_paths")=={n:p for n,(p,_) in paths.items()},
         "STAGE_OUTPUT_CONTRACT_MISMATCH")

def _snapshot(paths):
    records={};total=0
    for name,(relative,path) in paths.items():
        need(path.is_file() and not path.is_symlink(),
             "STAGE_OUTPUT_MISSING_OR_INVALID:"+name)
        size=path.stat().st_size
        records[name]={"path":relative,"size":size,"sha256":digest(path.read_bytes())}
        total+=size
    return records,total

def _verify_outputs(receipt,paths):
    expected=receipt.get("outputs")
    need(type(expected) is dict and set(expected)==set(paths),
         "STAGE_OUTPUT_RECEIPT_SET_INVALID")
    actual,total=_snapshot(paths)
    need(actual==expected,"STAGE_OUTPUT_HASH_MISMATCH")
    return total

def _summary(receipt,status,executed,recovered,writes,total):
    return {"schema":SCHEMA,"stage_id":receipt["stage_id"],
            "stage_version":receipt["stage_version"],"status":status,
            "executed":executed,"reused":status=="REUSED_VERIFIED",
            "recovered":recovered,"input_fingerprint":receipt["input_fingerprint"],
            "receipt_sha256":receipt["receipt_sha256"],
            "output_count":len(receipt["outputs"]),"output_bytes":total,
            "receipt_writes":writes,"output_paths":receipt["output_paths"]}

def verify_stage(*,root,stage_id,stage_version,inputs,outputs):
    paths,receipt_path=_safe_paths(root,stage_id,outputs)
    receipt=_read_receipt(receipt_path)
    need(receipt.get("status")=="COMPLETE","STAGE_NOT_COMPLETE")
    _check_identity(receipt,stage_id,stage_version,
                    _input_sha(stage_id,stage_version,inputs),paths)
    total=_verify_outputs(receipt,paths)
    return _summary(receipt,"REUSED_VERIFIED",False,False,0,total)

def execute_stage(*,root,stage_id,stage_version,inputs,outputs,execute,validate=None):
    """Reuse only verified artifacts; recover complete interrupted writes safely."""
    paths,receipt_path=_safe_paths(root,stage_id,outputs)
    input_sha=_input_sha(stage_id,stage_version,inputs)
    output_paths={n:p for n,(p,_) in paths.items()}
    writes=0
    if receipt_path.is_file():
        receipt=_read_receipt(receipt_path)
        _check_identity(receipt,stage_id,stage_version,input_sha,paths)
        status=receipt.get("status")
        if status=="COMPLETE":
            total=_verify_outputs(receipt,paths)
            return {**_summary(receipt,"REUSED_VERIFIED",False,False,0,total),
                    "result":None}
        need(status=="RUNNING","STAGE_RECEIPT_STATUS_INVALID")
        recovered=False
        if validate is not None:
            try:
                _snapshot(paths)
                recovered=validate({n:p for n,(_,p) in paths.items()}) is True
            except Exception:recovered=False
        if recovered:
            records,total=_snapshot(paths)
            sealed=_seal({"schema":SCHEMA,"stage_id":stage_id,
                "stage_version":stage_version,"input_fingerprint":input_sha,
                "output_paths":output_paths,"outputs":records,"status":"COMPLETE",
                "recovered_from_interruption":True})
            _atomic_write(receipt_path,(canonical(sealed)+"\n").encode("utf8"))
            return {**_summary(sealed,"RECOVERED_VERIFIED",False,True,1,total),
                    "result":None}
        # RUNNING proves these declared outputs were absent before this stage.
        for _,path in paths.values():
            need(not path.is_symlink(),"STAGE_OUTPUT_SYMLINK_BLOCKED")
            if path.exists():
                need(path.is_file(),"STAGE_PARTIAL_OUTPUT_NOT_REGULAR_FILE")
                path.unlink()
    else:
        need(not any(path.exists() for _,path in paths.values()),
             "STAGE_OUTPUTS_EXIST_WITHOUT_RECEIPT")
    intent=_seal({"schema":SCHEMA,"stage_id":stage_id,"stage_version":stage_version,
                  "input_fingerprint":input_sha,"output_paths":output_paths,
                  "status":"RUNNING"})
    _atomic_write(receipt_path,(canonical(intent)+"\n").encode("utf8"));writes+=1
    result=execute()
    output_files={n:p for n,(_,p) in paths.items()}
    if validate is not None:
        need(validate(output_files) is True,"STAGE_OUTPUT_VALIDATION_FAILED")
    records,total=_snapshot(paths)
    sealed=_seal({"schema":SCHEMA,"stage_id":stage_id,"stage_version":stage_version,
                  "input_fingerprint":input_sha,"output_paths":output_paths,
                  "outputs":records,"status":"COMPLETE",
                  "recovered_from_interruption":False})
    _atomic_write(receipt_path,(canonical(sealed)+"\n").encode("utf8"));writes+=1
    return {**_summary(sealed,"EXECUTED_AND_SEALED",True,False,writes,total),
            "result":result}
