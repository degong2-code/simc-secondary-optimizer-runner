#!/usr/bin/env python3
"""v108 optional controls: SimC-native food/potion/augment, two safe diamonds.

Flask F cannot be changed until an exact alternative static F vector is
source verified. Omnium Folio is separate from augmentation: not selected.
"""
import tkinter as tk
from tkinter import ttk
from v108_native_consumable_inputs import SUPPORTED,DIAMONDS,OMNIUM_PRESETS

SOURCE_DEFAULT="source_default"
FIELDS=("food","potion","augmentation")
LABELS={"food":"음식","potion":"물약","augmentation":"증강 룬"}

def select_consumables(root,existing):
    win=tk.Toplevel(root)
    win.title("소모품·특수 다이아몬드 (SimC)")
    win.transient(root);win.grab_set()
    win.geometry("680x440")
    f=ttk.Frame(win,padding=15);f.pack(fill="both",expand=True)
    ttk.Label(f,text="직업별 기본값을 유지하거나 검증된 SimC 토큰을 선택하세요.",
              wraplength=535).pack(anchor="w",pady=5)
    controls={}
    for key in FIELDS:
        row=ttk.Frame(f);row.pack(fill="x",pady=5)
        ttk.Label(row,text=LABELS[key],width=14).pack(side="left")
        v=tk.StringVar(value=existing[key])
        ttk.Combobox(row,textvariable=v,state="readonly",width=38,
                     values=(SOURCE_DEFAULT,*sorted(SUPPORTED[key]))).pack(
                     side="left",fill="x",expand=True)
        controls[key]=v
    row=ttk.Frame(f);row.pack(fill="x",pady=5)
    ttk.Label(row,text="에버송 다이아몬드",width=14).pack(side="left")
    d=tk.StringVar(value="source_default" if existing["diamond_id"]==0
                   else str(existing["diamond_id"]))
    ttk.Combobox(row,textvariable=d,state="readonly",width=38,
                 values=("source_default","240983","240967")).pack(
                 side="left",fill="x",expand=True)
    r=ttk.Frame(f);r.pack(fill="x",pady=5)
    ttk.Label(r,text="Omnium Folio",width=14).pack(side="left")
    folio=tk.StringVar(value=existing["omnium_talents"])
    ttk.Combobox(r,textvariable=folio,state="readonly",width=64,
                 values=("source_default",*sorted(OMNIUM_PRESETS))).pack(
                 side="left",fill="x",expand=True)
    ttk.Label(f,text="영약은 현재 전문화의 Native 확인된 F=165 기본값으로 고정합니다.",
              wraplength=540).pack(anchor="w",pady=5)
    ttk.Label(f,text="Omnium은 증강 룬과 별개입니다. 검증된 SimC 원본의 전체 5행 조합만 선택 가능하며, 임의 조합은 미지원입니다.",
              wraplength=540).pack(anchor="w",pady=5)
    out=[None]
    def save():
        out[0]={"flask":"source_default",
                **{k:v.get() for k,v in controls.items()},
                "diamond_id":0 if d.get()=="source_default" else int(d.get()),
                "omnium_talents":folio.get()}
        win.destroy()
    btn=ttk.Frame(f);btn.pack(fill="x",pady=10)
    ttk.Button(btn,text="적용",command=save).pack(side="right",padx=3)
    ttk.Button(btn,text="취소",command=win.destroy).pack(side="right",padx=3)
    win.wait_window()
    return out[0]
