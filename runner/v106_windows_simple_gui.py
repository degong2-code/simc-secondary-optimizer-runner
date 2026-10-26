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
    user_scenario, store_session, paths, clear_cancel,
    request_cancel, progress, format_result)

DISPLAY={
    ("warrior","fury"):"전사 — 분노",
    ("paladin","retribution"):"성기사 — 징벌",
    ("mage","frost"):"마법사 — 냉기",
    ("hunter","beast_mastery"):"사냥꾼 — 야수",
    ("rogue","subtlety"):"도적 — 잠행",
    ("shaman","elemental"):"주술사 — 정기"}
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
        self.root=root;root.title("SimC CHMV 최적화 — DPS 6개 전문화 베타")
        root.geometry("890x760")
        self.proc=None;self.log_handle=None;self.folder=None
        self.last_progress=None;self.last_log=None
        self.ui={}
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
        ttk.Label(outer,text="현재 지원: 딜러 6개 전문화 · 대표 장비 내부 자동 생성 · 결과는 관측상 최고와 95% 비교",
                  wraplength=840).grid(row=1,column=0,columnspan=4,sticky="w")
        self.spec=tk.StringVar(value=DISPLAY[("paladin","retribution")])
        self.vars={}
        self._label(outer,2,0,"직업 / 전문화")
        combo=ttk.Combobox(outer,textvariable=self.spec,state="readonly",
                           values=[DISPLAY[x] for x in SUPPORTED],width=30)
        combo.grid(row=2,column=1,columnspan=3,sticky="ew",padx=6,pady=4)
        combo.bind("<<ComboboxSelected>>",lambda _e:self._defaults())

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
        ttk.Separator(outer,orient="horizontal").grid(row=9,column=0,
                        columnspan=4,sticky="ew",pady=8)
        self._entry(outer,10,0,"SimC 실행 파일","binary",
                    default=self.cfg.get("binary",""))
        ttk.Button(outer,text="찾기",command=self._browse).grid(
                   row=10,column=3,sticky="e")
        self._entry(outer,11,0,"SimC revision","revision",
                    default=self.cfg.get("revision",""))
        ttk.Label(outer,text="SimC 바이너리와 revision은 최초 한 번만 등록. 변경 시 별도 세션으로 보관.",
                  wraplength=850).grid(row=12,column=0,columnspan=4,sticky="w")
        self.start_btn=ttk.Button(outer,text="실행 / 동일 설정 재개",
                                  command=self.start)
        self.start_btn.grid(row=13,column=0,columnspan=2,sticky="ew",pady=9,padx=3)
        self.cancel_btn=ttk.Button(outer,text="취소",command=self.cancel,
                                   state="disabled")
        self.cancel_btn.grid(row=13,column=2,sticky="ew",pady=9,padx=3)
        ttk.Button(outer,text="결과 폴더",command=self.open_folder).grid(
                   row=13,column=3,sticky="ew",pady=9,padx=3)
        self.status=tk.StringVar(value="준비 — 기본 6회 Native 탐색, 동일 설정은 캐시 재사용")
        ttk.Label(outer,textvariable=self.status,wraplength=850).grid(
                   row=14,column=0,columnspan=4,sticky="w")
        self.bar=ttk.Progressbar(outer,maximum=100,mode="determinate")
        self.bar.grid(row=15,column=0,columnspan=4,sticky="ew",pady=(6,6))
        ttk.Label(outer,text="진행 로그 / 관측 결과",font=("",10,"bold")
                  ).grid(row=16,column=0,columnspan=4,sticky="w")
        self.display=scrolledtext.ScrolledText(outer,height=17,wrap="word")
        self.display.grid(row=17,column=0,columnspan=4,sticky="nsew",pady=5)
        ttk.Label(outer,text="베타 범위: 기본 대표 장비·기본 소모품 사용. 특수장비·장식·소모품 자유 선택 UI는 후속 단계.",
                  wraplength=850).grid(row=18,column=0,columnspan=4,sticky="w")
        outer.grid_rowconfigure(17,weight=1)
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

    def _browse(self):
        p=filedialog.askopenfilename(title="SimC 실행 파일 선택",
          filetypes=[("SimulationCraft executable","*.exe"),("All files","*.*")])
        if p:self.vars["binary"].set(p)

    def _user(self):
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
        return user_scenario(raw)

    def _write(self,value):
        self.display.delete("1.0","end")
        self.display.insert("end",value)
        self.display.see("end")

    def start(self):
        if self.proc is not None and self.proc.poll() is None:
            messagebox.showwarning("진행 중","기존 실행을 먼저 취소하거나 완료해야 해.")
            return
        try:
            user=self._user()
            binary=pathlib.Path(self.vars["binary"].get()).expanduser().resolve()
            revision=self.vars["revision"].get().strip()
            folder=store_session(user,DEFAULT_ROOT,binary,revision)
            self.folder=folder
            clear_cancel(folder)
            save_settings({"binary":str(binary),"revision":revision})
            log=paths(folder)["log"]
            self.log_handle=open(log,"a",encoding="utf8",buffering=1)
            self.log_handle.write("\n=== V106 USER RUN / RESUME ===\n")
            flags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0
            self.proc=subprocess.Popen(
                [sys.executable,str(pathlib.Path(__file__).resolve().parent/
                   "v106_user_session_controller.py"),
                 "--session",str(folder),"--binary",str(binary),
                 "--revision",revision],
                stdout=self.log_handle,stderr=subprocess.STDOUT,
                creationflags=flags)
            self.start_btn.configure(state="disabled")
            self.cancel_btn.configure(state="normal")
            self.status.set("Native 실행 시작 / 재개: "+folder.name)
        except Exception as exc:
            self.status.set("실행 전 차단: "+str(exc))
            messagebox.showerror("입력 또는 환경 확인",str(exc))
            if self.log_handle:
                self.log_handle.close();self.log_handle=None

    def cancel(self):
        if self.proc is None or self.proc.poll() is not None:return
        request_cancel(self.folder)
        self.status.set("취소 요청됨 — 진행 중 Native 취소 처리를 기다리는 중")
        self.cancel_btn.configure(state="disabled")

    def _poll(self):
        try:
            if self.folder is not None:
                p=progress(self.folder)
                self.bar["value"]=p["progress_percent"]
                running=self.proc is not None and self.proc.poll() is None
                self.status.set(
                    ("실행 중" if running else p["status"])+
                    f" · {p['completed_jobs']}/{p['planned_jobs']} 후보"
                    f" · Native 누적 {p['native_attempts']}"
                    f" · 캐시 {p['cache_hits']}")
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
                    self.cancel_btn.configure(state="disabled")
                    if self.log_handle:
                        self.log_handle.close();self.log_handle=None
                    out=paths(self.folder)["final"]
                    if exitcode==0 and out.is_file():
                        data=json.loads(out.read_text("utf8"))
                        self._write(format_result(data)+
                           "\n\n결과 폴더: "+str(self.folder))
                        self.status.set("완료 · 기존 SimC Native 및 95% 결과 확인")
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
