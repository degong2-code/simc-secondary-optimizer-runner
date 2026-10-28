#!/usr/bin/env python3
"""v106 lightweight Windows user screen for existing SimC optimizer.

Tkinter only, no new solver or Native logic. One worker subprocess per session:
start/resume reuses the same session key; stop sets the existing v094 cancel
marker and does NOT discard cached valid Native JSON2. Initial beta UI covers
the default representative gear scenario for six source-backed DPS specs.
"""
from __future__ import annotations
import json, os, pathlib, subprocess, sys, tkinter as tk
from tkinter import filedialog,messagebox,scrolledtext,ttk

from v106_user_session_controller import (
    SCHEMA, DEFAULT_ROOT, SUPPORTED, canonical, source_defaults,
    user_scenario, store_session, session_path, cache_only_preflight,
    paths, clear_cancel,
    request_cancel, progress, format_result, selected_rows_from_form)
from v107_optional_items_dialog import select_items
from v108_user_consumable_dialog import select_consumables
from v109_windows_readiness_diagnostic import (
    safe_receipt,archive_receipt,revision_from_official_nightly_archive_name)

DISPLAY={
    ("warrior","fury"):"전사 — 분노",
    ("paladin","retribution"):"성기사 — 징벌",
    ("mage","frost"):"마법사 — 냉기",
    ("hunter","beast_mastery"):"사냥꾼 — 야수",
    ("rogue","subtlety"):"도적 — 잠행",
    ("shaman","elemental"):"주술사 — 정기",
    ("druid","balance"):"드루이드 — 조화",
    ("evoker","devastation"):"기원사 — 황폐"}
# Preserve all 24 existing beta entries; use readable fallbacks for others.
for _key in SUPPORTED:
    DISPLAY.setdefault(_key," / ".join(_key))
SETTINGS=pathlib.Path.home()/"SIMC_Secondary_Optimizer"/"v106_gui_settings.json"

def remembered_settings():
    if not SETTINGS.is_file():return {}
    try:
        data=json.loads(SETTINGS.read_text("utf8"))
        return data if type(data) is dict else {}
    except (ValueError,OSError):return {}

def save_settings(data):
    SETTINGS.parent.mkdir(parents=True,exist_ok=True)
    SETTINGS.write_text(canonical(data)+"\n",encoding="utf8")

class UserWindow:
    def __init__(self,root):
        self.root=root;root.title("SimC CHMV 최적화 — DPS 26개 경로 베타")
        root.geometry("890x760")
        self.proc=None;self.log_handle=None;self.folder=None
        self.running_cache_only=False
        self.last_progress=None;self.last_log=None
        self.ui={}
        self.advanced_rows={"special_items":[],"embellishments":[]}
        self.consumable_choices={
            "flask":"source_default","food":"source_default",
            "potion":"source_default","augmentation":"source_default",
            "diamond_id":0,"omnium_talents":"source_default"}
        self.cfg=remembered_settings()
        self._draw()
        self._defaults()
        root.after(450,self._poll)
        root.protocol("WM_DELETE_WINDOW",self._close)

    def _draw(self):
        outer=ttk.Frame(self.root,padding=14)
        outer.pack(fill="both",expand=True)
        ttk.Label(outer,text="목표 레벨 CHMV 최적화",
                  font=("",16,"bold")).grid(row=0,column=0,columnspan=4,
                  sticky="w",pady=(0,8))
        ttk.Label(outer,text="DPS 26개 경로(기존 24개 소스 기반 베타 + 조화·황폐 독립 생성) · 목표 CHMV 절댓값 · 95% 비교",
                  wraplength=840).grid(row=1,column=0,columnspan=4,sticky="w")
        self.spec=tk.StringVar(value=DISPLAY[("paladin","retribution")])
        self.vars={}
        self._label(outer,2,0,"직업 / 전문화")
        combo=ttk.Combobox(outer,textvariable=self.spec,state="readonly",
                           values=[DISPLAY[x] for x in SUPPORTED],width=30)
        combo.grid(row=2,column=1,columnspan=3,sticky="ew",padx=6,pady=4)
        combo.bind("<<ComboboxSelected>>",lambda _e:self._new_specialization())

        self._entry(outer,3,0,"종족","race",rowspan=1)
        self._entry(outer,4,0,"특성 코드","talents")
        self._entry(outer,5,0,"장신구 1 ID","trinket1")
        self._entry(outer,5,2,"장신구 2 ID","trinket2")
        self._entry(outer,6,0,"목표 ilvl","ilevel",default="334")
        self._entry(outer,6,2,"수동 최종 T (선택)","final_T")
        self._entry(outer,7,0,"대상 수","targets",default="1")
        self._entry(outer,7,2,"전투 길이 (초)","duration",default="300")
        self.oil_main=tk.BooleanVar(value=True)
        self.oil_off=tk.BooleanVar(value=False)
        self.raid=tk.BooleanVar(value=True)
        ttk.Checkbutton(outer,text="주무기 기름",variable=self.oil_main
                        ).grid(row=8,column=0,sticky="w",pady=4)
        ttk.Checkbutton(outer,text="보조무기 기름 (쌍수 전용)",variable=self.oil_off
                        ).grid(row=8,column=1,sticky="w",pady=4)
        ttk.Checkbutton(outer,text="공대 버프",variable=self.raid
                        ).grid(row=8,column=2,sticky="w",pady=4)
        ttk.Button(outer,text="특수장비·장식 선택…",command=self._advanced
                   ).grid(row=8,column=3,sticky="ew",padx=3)
        ttk.Separator(outer,orient="horizontal").grid(row=9,column=0,
                        columnspan=4,sticky="ew",pady=8)
        self._entry(outer,10,0,"SimC 실행 파일","binary",
                    default=self.cfg.get("binary",""))
        ttk.Button(outer,text="찾기",command=self._browse).grid(
                   row=10,column=3,sticky="e")
        self._entry(outer,11,0,"SimC Git SHA (7~40자리)","revision",
                    default=self.cfg.get("revision",""))
        ttk.Button(outer,text="배포 .7z에서 SHA 읽기",
                   command=self._revision_archive).grid(
                   row=11,column=3,sticky="e")
        self._entry(outer,12,0,"정적 캐시 (특수장비)","static_cache",
                    default=self.cfg.get("static_cache",""))
        ttk.Button(outer,text="찾기",command=self._browse_cache).grid(
            row=12,column=3,sticky="e")
        ttk.Label(outer,text="SimC 바이너리와 revision은 최초 한 번만 등록. 선택 특수장비에는 정확한 Native 고정 L 캐시가 필요.",
                  wraplength=850).grid(row=13,column=0,columnspan=4,sticky="w")
        self.start_btn=ttk.Button(outer,text="실행 / 동일 설정 재개",
                                  command=self.start)
        self.start_btn.grid(row=14,column=0,columnspan=2,sticky="ew",pady=9,padx=3)
        self.cancel_btn=ttk.Button(outer,text="취소 요청 (현재 SimC 1건 완료 후)",
                                   command=self.cancel,
                                   state="disabled")
        self.cancel_btn.grid(row=14,column=2,sticky="ew",pady=9,padx=3)
        ttk.Button(outer,text="결과 폴더",command=self.open_folder).grid(
                   row=14,column=3,sticky="ew",pady=9,padx=3)
        self.status=tk.StringVar(value="준비 — 기본 6회 Native 탐색, 동일 설정은 캐시 재사용")
        ttk.Label(outer,textvariable=self.status,wraplength=850).grid(
                   row=15,column=0,columnspan=4,sticky="w")
        self.bar=ttk.Progressbar(outer,maximum=100,mode="determinate")
        self.bar.grid(row=16,column=0,columnspan=4,sticky="ew",pady=(6,6))
        ttk.Label(outer,text="진행 로그 / 관측 결과",font=("",10,"bold")
                  ).grid(row=17,column=0,columnspan=4,sticky="w")
        self.display=scrolledtext.ScrolledText(outer,height=17,wrap="word")
        self.display.grid(row=18,column=0,columnspan=4,sticky="nsew",pady=5)
        ttk.Button(outer,text="음식·물약·증강 룬·다이아몬드·Omnium 선택…",
                   command=self._consumables).grid(
                   row=19,column=0,columnspan=4,sticky="ew",pady=4)
        ttk.Label(outer,text="영약 F=165는 고정. Omnium Folio는 검증된 원본 전체 조합만 선택 가능.",
                  wraplength=850).grid(row=20,column=0,columnspan=4,sticky="w")
        ttk.Button(outer,text="Windows 실행 환경 진단 (Native 0회) · ZIP 생성",
                   command=self._readiness).grid(
                   row=21,column=0,columnspan=4,sticky="ew",pady=4)
        self.cache_btn=ttk.Button(outer,
            text="완료된 결과 캐시 검증 (Native 0회 · 6/6 재사용)",
            command=lambda:self.start(cache_only=True))
        self.cache_btn.grid(row=22,column=0,columnspan=4,sticky="ew",pady=4)
        outer.grid_rowconfigure(18,weight=1)
        for i in (1,3):outer.grid_columnconfigure(i,weight=1)

    def _label(self,area,row,col,text):
        ttk.Label(area,text=text).grid(row=row,column=col,sticky="w",padx=(0,4))
    def _entry(self,area,row,col,text,key,default="",rowspan=1):
        self._label(area,row,col,text)
        v=tk.StringVar(value=default);self.vars[key]=v
        ttk.Entry(area,textvariable=v,width=34).grid(row=row,column=col+1,
                   sticky="ew",padx=4,pady=3,rowspan=rowspan)

    def _selected(self):
        inv={v:k for k,v in DISPLAY.items()}
        return inv[self.spec.get()]

    def _defaults(self):
        source=source_defaults(self._selected())
        self.vars["race"].set(source["race"])
        self.vars["talents"].set(source["talents"])
        self.vars["trinket1"].set(str(source["trinket_ids"][0]))
        self.vars["trinket2"].set(str(source["trinket_ids"][1]))
        self.oil_main.set(True)
        self.oil_off.set("off_hand" in source["oil_hands"])
        self.status.set("기본 대표 무기 구성: "+source["weapon_form"]+
                        " · 캐시 보존을 위해 동일 설정은 동일 세션 사용")

    def _new_specialization(self):
        self.advanced_rows={"special_items":[],"embellishments":[]}
        self._defaults()

    def _consumables(self):
        result=select_consumables(self.root,self.consumable_choices)
        if result is not None:
            self.consumable_choices=result
            self.status.set("소모품·Omnium·다이아몬드 선택 반영 · 영약 F=165/보석 J=138 불변")

    def _advanced(self):
        result=select_items(self.root,self.advanced_rows,self._base_controls)
        if result is not None:
            self.advanced_rows=result
            rows=selected_rows_from_form(
                result["special_items"],result["embellishments"])
            self.status.set(
                "장비 선택: 특수 "+str(len(rows["special_items"]))+
                "개, 장식 "+str(len(rows["embellishments"]))+
                "개 · Native 정확한 정적 L 정책 유지")

    def _readiness(self):
        try:
            user=self._user()
            binary=self.vars["binary"].get().strip()
            revision=self.vars["revision"].get().strip()
            cache=self.vars["static_cache"].get().strip() or None
            receipt=safe_receipt(user,binary,revision,cache)
        except Exception as exc:
            # No Native is ever requested by diagnostics.
            receipt={"schema":"v109_windows_p1_readiness_no_native_v1",
                     "status":"BLOCKED_NO_NATIVE","new_native_calls":0,
                     "blocker_class":type(exc).__name__,
                     "blocker_code":str(exc).split(":",1)[0]}
        bundle=archive_receipt(receipt,open_folder=True)
        if receipt["status"]=="PASS_ZERO_NATIVE_PLAN_ONLY":
            self.status.set("진단 PASS (Native 0회) · 실제 Windows SimC는 아직 미검증")
            messagebox.showinfo("실행 준비 점검",
                "내부 프로필·CHMV·6회 상한 점검 통과.\n"
                "단, 바이너리의 실제 revision과 Windows SimC 실행 가능 여부는"
                " 아직 검증하지 않았습니다.\n\n"
                "진단 ZIP을 이 채팅에 첨부해 주세요.\n"+str(bundle))
        else:
            self.status.set("환경 진단 BLOCKED · Native 0회")
            messagebox.showwarning("실행 준비 점검",
                "실행 전 차단: "+receipt.get("blocker_code","UNKNOWN")+
                "\n\n민감 설정을 제외한 진단 ZIP을 이 채팅에 첨부해 주세요.\n"+
                str(bundle))

    def _revision_archive(self):
        archive=filedialog.askopenfilename(
            title="선택한 simc.exe를 추출한 공식 nightly .7z 압축파일",
            filetypes=[("Official SimC nightly","*.7z"),("All files","*.*")])
        if not archive:return
        try:
            revision=revision_from_official_nightly_archive_name(archive)
        except ValueError as exc:
            messagebox.showerror("빌드 파일명 형식 확인",str(exc))
            return
        self.vars["revision"].set(revision)
        self.status.set("revision 파일명에서 추출: "+revision+
                        " · 선택한 simc.exe가 같은 압축파일에서 나온 것인지 확인 필요")

    def _browse_cache(self):
        p=filedialog.askopenfilename(title="Native 정적 아이템 캐시 선택",
          filetypes=[("JSON","*.json"),("All files","*.*")])
        if p:self.vars["static_cache"].set(p)

    def _browse(self):
        p=filedialog.askopenfilename(title="SimC 실행 파일 선택",
          filetypes=[("SimulationCraft executable","*.exe"),("All files","*.*")])
        if p:self.vars["binary"].set(p)

    def _base_controls(self):
        cl,sp=self._selected()
        raw={"class":cl,"spec":sp,"race":self.vars["race"].get().strip(),
             "talents":self.vars["talents"].get().strip(),
             "ilevel":int(self.vars["ilevel"].get()),
             "final_T":(int(self.vars["final_T"].get())
                         if self.vars["final_T"].get().strip() else None),
             "trinket_ids":[int(self.vars["trinket1"].get()),
                            int(self.vars["trinket2"].get())],
             "oil_hands":([ "main_hand"] if self.oil_main.get() else [])+
                         (["off_hand"] if self.oil_off.get() else []),
             "targets":int(self.vars["targets"].get()),
             "duration_seconds":int(self.vars["duration"].get()),
             "raid_buffs":self.raid.get()}
        return raw

    def _user(self):
        chosen=selected_rows_from_form(
            self.advanced_rows.get("special_items",[]),
            self.advanced_rows.get("embellishments",[]))
        return user_scenario({**self._base_controls(),**chosen,
                              "consumable_choices":self.consumable_choices})

    def _write(self,value):
        self.display.delete("1.0","end")
        self.display.insert("end",value)
        self.display.see("end")

    def start(self,cache_only=False):
        if self.proc is not None and self.proc.poll() is None:
            messagebox.showwarning("진행 중","기존 실행을 먼저 취소하거나 완료해야 해.")
            return
        try:
            user=self._user()
            binary=pathlib.Path(self.vars["binary"].get()).expanduser().resolve()
            revision=self.vars["revision"].get().strip()
            static_text=self.vars["static_cache"].get().strip()
            static_cache=(pathlib.Path(static_text).expanduser().resolve()
                          if static_text else None)
            if cache_only:
                folder,_=session_path(user,DEFAULT_ROOT,binary,revision,static_cache)
                cache_only_preflight(folder)
            else:
                folder=store_session(user,DEFAULT_ROOT,binary,revision,static_cache)
            self.folder=folder
            clear_cancel(folder)
            save_settings({"binary":str(binary),"revision":revision,
                           "static_cache":str(static_cache) if static_cache else ""})
            log=paths(folder)["log"]
            self.log_handle=open(log,"a",encoding="utf8",buffering=1)
            self.log_handle.write("\n=== V112 CACHE ONLY / NO NEW NATIVE ===\n"
                                  if cache_only else
                                  "\n=== V106 USER RUN / RESUME ===\n")
            flags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0
            cmd=[sys.executable,str(pathlib.Path(__file__).resolve().parent/
                 "v106_user_session_controller.py"),
                 "--session",str(folder),"--binary",str(binary),
                 "--revision",revision]
            if static_cache:cmd.extend(["--static-cache",str(static_cache)])
            if cache_only:cmd.append("--cache-only")
            self.proc=subprocess.Popen(
                cmd,
                stdout=self.log_handle,stderr=subprocess.STDOUT,
                creationflags=flags,
                env={**os.environ,"PYTHONIOENCODING":"utf-8"})
            self.running_cache_only=bool(cache_only)
            self.start_btn.configure(state="disabled")
            self.cache_btn.configure(state="disabled")
            self.cancel_btn.configure(state="disabled" if cache_only else "normal")
            self.status.set(("완료된 Native 캐시 6건 검증 (새 Native 0회): " if cache_only
                             else "Native 실행 시작 / 재개: ")+folder.name)
        except Exception as exc:
            self.status.set("실행 전 차단: "+str(exc))
            messagebox.showerror("입력 또는 환경 확인",str(exc))
            if self.log_handle:
                self.log_handle.close();self.log_handle=None

    def cancel(self):
        if self.proc is None or self.proc.poll() is not None:return
        request_cancel(self.folder)
        self.status.set("취소 요청됨 — 진행 중인 SimC 1건은 끝까지 실행 후 다음 후보부터 중단")
        self.cancel_btn.configure(state="disabled")

    def _poll(self):
        try:
            if self.folder is not None:
                p=progress(self.folder)
                self.bar["value"]=p["progress_percent"]
                running=self.proc is not None and self.proc.poll() is None
                if running:
                    self.status.set(
                        f"실행 중 · {p['completed_jobs']}/{p['planned_jobs']} 후보"
                        f" · Native 누적 {p['native_attempts']}"
                        f" · 캐시 {p['cache_hits']}")
                # When idle, retain the PASS / BLOCKED message instead of
                # erasing it every 450 ms with old durable progress.
                log=paths(self.folder)["log"]
                if log.is_file():
                    with log.open("rb") as f:
                        f.seek(0,2);f.seek(max(0,f.tell()-7500))
                        txt=f.read().decode("utf8",errors="replace")
                    if txt!=self.last_log and running:
                        self._write(txt)
                        self.last_log=txt
                if self.proc is not None and not running:
                    exitcode=self.proc.returncode
                    self.proc=None
                    self.start_btn.configure(state="normal")
                    self.cache_btn.configure(state="normal")
                    self.cancel_btn.configure(state="disabled")
                    if self.log_handle:
                        self.log_handle.close();self.log_handle=None
                    out=paths(self.folder)["final"]
                    if exitcode==0 and out.is_file():
                        data=json.loads(out.read_text("utf8"))
                        self._write(format_result(data)+
                           "\n\n결과 폴더: "+str(self.folder))
                        self.status.set("캐시 6/6 검증 · 신규 Native 0회"
                                        if self.running_cache_only else
                                        "완료 · 기존 SimC Native 및 95% 결과 확인")
                    else:
                        self.status.set("부분 중단 또는 오류 · 로그 확인 후 동일 설정으로 재개 가능")
                        if log.is_file():
                            self._write(log.read_text("utf8")[-7500:])
        except Exception as exc:
            self.status.set("진행 표시 오류: "+str(exc))
        self.root.after(450,self._poll)

    def open_folder(self):
        try:
            p=self.folder if self.folder else DEFAULT_ROOT
            p.mkdir(parents=True,exist_ok=True)
            if os.name=="nt":os.startfile(str(p))
            else:messagebox.showinfo("결과 폴더",str(p))
        except Exception as exc:messagebox.showerror("폴더 열기 실패",str(exc))

    def _close(self):
        if self.proc is not None and self.proc.poll() is None:
            if not messagebox.askyesno("실행 중","작업 취소를 요청하고 창을 닫을까?"):
                return
            request_cancel(self.folder)
        self.root.destroy()

def main():
    root=tk.Tk()
    UserWindow(root)
    root.mainloop()
if __name__=="__main__":main()
