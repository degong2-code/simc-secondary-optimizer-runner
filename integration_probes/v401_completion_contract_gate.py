"""v401: stdlib-only validator of 78 completion contracts.

Checks structural consistency and recorded evidence references, NOT actual
external GitHub Actions execution or SimC success. A human or future review
must inspect real artifacts before asserting PASS.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import re

ROOT=pathlib.Path(__file__).resolve().parents[1]
REGISTRY=pathlib.Path("docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json")
GENERATED=pathlib.Path("docs/development/78_ELEMENT_STATUS_GENERATED.md")
TRACKER=pathlib.Path("docs/development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md")
SCHEMA="simc_78_element_completion_contract_v401"
ALL_IDS=tuple(prefix+str(i) for prefix,end in
              (("A",11),("B",12),("C",14),("D",9),
               ("E",9),("F",7),("G",10),("H",6))
              for i in range(1,end+1))
AXES=("generic","current_source","product_integration","historical")
STATES={"PASS","PENDING","NOT_APPLICABLE"}
KINDS={
    "generic":{"CURRENT_SOURCE_REAL","GENERALIZATION_REGRESSION"},
    "current_source":{"CURRENT_SOURCE_REAL"},
    "product_integration":{"PRODUCT_INTEGRATION_REAL"},
    "historical":{"HISTORICAL_SCOPED"}
}

class ContractInvalid(ValueError): pass

def need(ok,code):
    if not ok: raise ContractInvalid(code)

def validate(data,root=ROOT):
    need(type(data) is dict and data.get("schema")==SCHEMA,
         "CONTRACT_SCHEMA_INVALID")
    policy=data.get("policy")
    need(type(policy) is dict,"POLICY_MISSING")
    need(policy.get("full_product_e2e") in ("PENDING","PASS"),
         "FINAL_PRODUCT_E2E_STATUS_INVALID")
    evidence=data.get("evidence")
    need(type(evidence) is dict,"EVIDENCE_CATALOG_MISSING")
    for key,proof in evidence.items():
        need(type(key) is str and re.fullmatch(r"[a-z0-9_]+",key)
             and type(proof) is dict,"EVIDENCE_ENTRY_INVALID")
        need(proof.get("kind") in (
            "CURRENT_SOURCE_REAL","GENERALIZATION_REGRESSION",
            "PRODUCT_INTEGRATION_REAL","PRODUCT_E2E_REAL",
            "HISTORICAL_SCOPED","POLICY_DECISION"),
            "EVIDENCE_KIND_INVALID:"+key)
        note=proof.get("note")
        need(type(note) is str and note.startswith("docs/development/")
             and all(x not in (".","..") for x in
                     pathlib.PurePosixPath(note).parts)
             and (root/note).is_file(),
             "EVIDENCE_NOTE_NOT_FOUND:"+key)
        url=proof.get("actions_run")
        need(type(url) is str and re.fullmatch(
            r"https://github\.com/degong2-code/"
            r"simc-secondary-optimizer-runner/actions/runs/[1-9][0-9]*",
            url) is not None,"ACTIONS_RECEIPT_URL_REQUIRED:"+key)
        sha=proof.get("tested_sha")
        need(type(sha) is str and re.fullmatch(r"[a-f0-9]{40}",sha),
             "TESTED_COMMIT_SHA_REQUIRED:"+key)
        supports=proof.get("supports")
        need(type(supports) is list and bool(supports) and
             len(supports)==len(set(supports)) and
             all(type(eid) is str and eid in ALL_IDS for eid in supports),
             "EVIDENCE_SUPPORTED_ELEMENT_IDS_INVALID:"+key)
    entries=data.get("elements")
    need(type(entries) is list and len(entries)==78,
         "EXACTLY_78_CONTRACTS_REQUIRED")
    need([row.get("id") if type(row) is dict else None for row in entries]
         ==list(ALL_IDS),"ELEMENT_IDS_EXACT_AND_ORDER_REQUIRED")
    for row in entries:
        eid=row["id"]
        need(set(row)=={"id","name","scope","acceptance",*AXES},
             "CONTRACT_FIELDS_INVALID:"+eid)
        need(type(row["name"]) is str and row["name"].strip()
             and type(row["acceptance"]) is str and row["acceptance"].strip()
             and row["scope"] in ("BASE","USER","RUN","OPTION",
                                  "BASE+USER","BASE+RUN"),
             "ELEMENT_DETAILS_INVALID:"+eid)
        for axis in AXES:
            dim=row[axis]
            need(type(dim) is dict and set(dim) in (
                {"state","evidence"},{"state","evidence","reason"}),
                "AXIS_FIELDS_INVALID:"+eid+":"+axis)
            state=dim["state"]
            refs=dim["evidence"]
            need(state in STATES and type(refs) is list
                 and len(set(refs))==len(refs)
                 and all(type(key) is str and key in evidence for key in refs),
                 "AXIS_STATE_OR_REFERENCES_INVALID:"+eid+":"+axis)
            if state=="PASS":
                need(bool(refs),"PASS_WITHOUT_EVIDENCE:"+eid+":"+axis)
                kinds={evidence[key]["kind"] for key in refs}
                need(KINDS[axis].issubset(kinds),
                     "PASS_MISSING_REQUIRED_EVIDENCE_KIND:"+eid+":"+axis)
                need(all(eid in evidence[key]["supports"] for key in refs),
                     "EVIDENCE_NOT_SCOPED_TO_ELEMENT:"+eid+":"+axis)
                need(not dim.get("reason"),"PASS_CANNOT_HAVE_NA_REASON")
            elif state=="PENDING":
                need(not refs and not dim.get("reason"),
                     "PENDING_MUST_NOT_CLAIM_EVIDENCE:"+eid+":"+axis)
            else:
                reason=dim.get("reason")
                need(type(reason) is str and len(reason.strip())>=40,
                     "NA_REQUIRES_CONCRETE_REASON:"+eid+":"+axis)
                need(bool(refs) and any(
                    evidence[key]["kind"]=="POLICY_DECISION" for key in refs),
                     "NA_NEEDS_POLICY_EVIDENCE:"+eid+":"+axis)
        if row["generic"]["state"]=="PASS":
            need(row["current_source"]["state"]=="PASS",
                 "GENERIC_NEEDS_CURRENT_ZERO_SOURCE:"+eid)
        if row["product_integration"]["state"]=="PASS":
            need(row["generic"]["state"] in ("PASS","NOT_APPLICABLE")
                 and row["current_source"]["state"] in ("PASS","NOT_APPLICABLE"),
                 "PRODUCT_READY_WITH_MISSING_GENERIC_OR_SOURCE:"+eid)
    prefix=policy.get("a7_may_be_next_only_after_generic_review_of")
    need(prefix==["A4","A5","A6"],"GENERIC_REVIEW_GATE_CHANGED")
    unresolved=[key for key in prefix if
                entries[ALL_IDS.index(key)]["generic"]["state"]=="PENDING"]
    expected=unresolved[0] if unresolved else "A7"
    need(policy.get("next_review")==expected,
         "NEXT_REVIEW_SKIPPED_GENERIC_VALIDATION:"+expected)
    if unresolved:
        row_a7=entries[ALL_IDS.index("A7")]
        need(all(row_a7[k]["state"]=="PENDING"
                 for k in ("generic","current_source","product_integration")),
             "A7_PREMATURE_VERIFIED_CLAIM_BEFORE_A4_A6_GENERIC")
    if policy["full_product_e2e"]=="PASS":
        need(all(complete(row) for row in entries),
             "FINAL_E2E_CANNOT_PASS_WHILE_ELEMENTS_INCOMPLETE")
        refs=policy.get("final_e2e_evidence")
        need(type(refs) is list and bool(refs) and any(
            key in evidence and evidence[key]["kind"]=="PRODUCT_E2E_REAL"
            for key in refs),"FINAL_E2E_ORIGINAL_EVIDENCE_REQUIRED")
    return entries

def complete(row):
    return all(row[axis]["state"] in ("PASS","NOT_APPLICABLE") for axis in
               ("generic","current_source","product_integration"))

def legacy_badge(row):
    if row["generic"]["state"]=="PASS":
        # A1–A3 identify the active expansion/season; A4+ are scoped
        # source/feature generalization, not a second season discovery.
        return ("ENGINE_AUTODISCOVERY_PASS" if row["id"] in ("A1","A2","A3")
                else "ENGINE_GENERALIZATION_PASS")
    if row["current_source"]["state"]=="PASS":
        return "READY_SCOPED — CURRENT"
    if row["historical"]["state"]=="PASS": return "READY_SCOPED — HISTORY"
    return "PENDING_SCOPE"

def check_tracker(data,root=ROOT):
    lines=[line for line in (root/TRACKER).read_text(encoding="utf8").splitlines()
           if re.match(r"^\| \*\*[A-H][1-9][0-9]* ",line)]
    need(len(lines)==78,"TRACKER_EXACTLY_78_ROWS_REQUIRED")
    for line,row in zip(lines,data["elements"]):
        cells=[s.strip() for s in line.strip().strip("|").split("|")]
        need(len(cells)==7,"TRACKER_COLUMNS_INVALID")
        need(cells[0]=="**"+row["id"]+" "+row["name"]+"**"
             and cells[1]==row["scope"] and cells[2]==row["acceptance"],
             "TRACKER_IDENTITIES_OR_ACCEPTANCE_DRIFT:"+row["id"])
        need(cells[6].startswith("**"+legacy_badge(row)),
             "TRACKER_STATUS_CONTRADICTS_CONTRACT:"+row["id"])
    return True

def render(data):
    entries=data["elements"]
    n_generic=sum(e["generic"]["state"]=="PASS" for e in entries)
    n_source=sum(e["current_source"]["state"]=="PASS" for e in entries)
    n_hist=sum(e["historical"]["state"]=="PASS" for e in entries)
    n_product=sum(e["product_integration"]["state"]=="PASS" for e in entries)
    done=sum(complete(e) for e in entries)
    lines=[
        "# SIMC 78개 요소 완료 계약 — 자동 생성",
        "",
        "> 상태 정본: [78_ELEMENT_COMPLETION_CONTRACTS.json]"
        "(78_ELEMENT_COMPLETION_CONTRACTS.json). 수동 편집 금지. 생성 명령: "
        "python integration_probes/v401_completion_contract_gate.py --write.",
        "",
        "> 각 축의 PASS는 전체 제품 완료가 아닙니다. 역사 실행은 범용성이나 현재 시즌 검증을 대체하지 않습니다.",
        "",
        f"- 범용 기능 PASS: **{n_generic}/78**",
        f"- 현재 원본 검증 PASS: **{n_source}/78** (범용 PASS와 중복 집계 가능)",
        f"- 개별 제품 통합 PASS: **{n_product}/78**",
        f"- 역사적 범위 PASS: **{n_hist}/78**",
        f"- 세 축을 모두 완료한 요소: **{done}/78**",
        f"- 최종 제품 E2E: **{data['policy']['full_product_e2e']}**",
        f"- 다음 검토 요소: **{data['policy']['next_review']}** "
        + ("(A4~A6 범용 검증 완료 후 A7 진입)"
           if data["policy"]["next_review"]=="A7" else
           "(A4~A6 범용성 미검증을 A7로 미루지 않음)"),
        "",
        "| ID | 기능 | 적용 | 범용성 | 현재 원본 | 제품 통합 | 역사 증거 | 요소 완료 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in entries:
        state=[row[axis]["state"] for axis in AXES]
        lines.append("| "+" | ".join([
            row["id"],row["name"],row["scope"],*state,
            "COMPLETE" if complete(row) else "INCOMPLETE"
        ])+" |")
    lines.extend(["","## 검증된 축의 원본·회귀 영수증",""])
    for row in entries:
        refs=[]
        for axis in AXES:
            if row[axis]["state"]=="PASS":
                for key in row[axis]["evidence"]:
                    if key not in refs:refs.append(key)
        if refs:
            links=[]
            for key in refs:
                proof=data["evidence"][key]
                path=proof["note"].removeprefix("docs/development/")
                links.append("["+proof["kind"]+"]("+path+") "
                             "([실행]("+proof["actions_run"]+"))")
            lines.append("- **"+row["id"]+"**: "+", ".join(links))
    return "\n".join(lines)+"\n"

def run(argv=None):
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check",action="store_true")
    mode.add_argument("--write",action="store_true")
    args=parser.parse_args(argv)
    data=json.loads((ROOT/REGISTRY).read_text(encoding="utf8"))
    entries=validate(data)
    check_tracker(data)
    out=render(data)
    dest=ROOT/GENERATED
    if args.write:dest.write_text(out,encoding="utf8",newline="\n")
    else:
        need(dest.is_file() and
             dest.read_text(encoding="utf8")==out,
             "GENERATED_STATUS_DOCUMENT_STALE")
    counts={axis:sum(e[axis]["state"]=="PASS" for e in entries)
            for axis in AXES}
    print("V401_COMPLETION_CONTRACT_VALID",
          "items",len(entries),"axis_PASS",counts,
          "next",data["policy"]["next_review"],
          "full_E2E",data["policy"]["full_product_e2e"])
    return 0

if __name__=="__main__":raise SystemExit(run())
