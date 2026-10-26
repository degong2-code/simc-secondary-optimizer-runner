#!/usr/bin/env python3
"""v107 small optional exact-item selection window, no SimC mechanics.

The dialog collects only user-selected special/crafted equipment and options.
The existing v098 input validation and SimC source own item meaning.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import messagebox,ttk
from v106_user_session_controller import selected_rows_from_form,user_scenario

NONTRINKET_SLOTS=("", "head","neck","shoulders","back","chest",
                   "wrists","hands","waist","legs","feet",
                   "finger1","finger2","main_hand","off_hand")
LAYOUTS=(
 ("special_items","특수효과 장비 · 최대 2개",
  ("slot","item_id","bonus_id","redirected_base_stats")),
 ("embellishments","장식 제작장비 · 최대 2개",
  ("slot","item_id","crafted_stats","embellishment","bonus_id")))
LABELS={"slot":"착용 부위","item_id":"아이템 ID","bonus_id":"bonus_id",
        "redirected_base_stats":"촉매 원본 ID",
        "crafted_stats":"제작 스탯 49/36",
        "embellishment":"장식 토큰"}

def select_items(root,existing,base_controls):
    """Return validated form rows on Apply, None on cancel; no Native call."""
    window=tk.Toplevel(root)
    window.title("선택 특수장비·장식 장비 (SimC)")
    window.geometry("870x460")
    window.transient(root)
    window.grab_set()
    area=ttk.Frame(window,padding=12)
    area.pack(fill="both",expand=True)
    ttk.Label(area,text="선택 장비만 입력합니다. 아이템 효과·발동은 SimC가 계산하며, 촉매 원본 효과는 원본 ID와 옵션으로 전달합니다.",
              wraplength=820).pack(anchor="w",pady=(0,6))
    fields={}
    for group,title,names in LAYOUTS:
        frame=ttk.LabelFrame(area,text=title,padding=6)
        frame.pack(fill="x",pady=7)
        heading=ttk.Frame(frame);heading.pack(fill="x")
        for col,k in enumerate(names):
            ttk.Label(heading,text=LABELS[k]).grid(row=0,column=col,sticky="w",padx=3)
            heading.grid_columnconfigure(col,weight=1)
        old=existing.get(group,[])
        rows=[]
        for i in range(2):
            line=ttk.Frame(frame);line.pack(fill="x",pady=2)
            initial=old[i] if i<len(old) else {}
            vars={}
            for col,k in enumerate(names):
                v=tk.StringVar(value=initial.get(k,""))
                vars[k]=v
                if k=="slot":
                    item=ttk.Combobox(line,textvariable=v,state="readonly",
                                      values=NONTRINKET_SLOTS,width=17)
                else:
                    item=ttk.Entry(line,textvariable=v,width=18)
                item.grid(row=0,column=col,sticky="ew",padx=3)
                line.grid_columnconfigure(col,weight=1)
            rows.append(vars)
        fields[group]=rows
    ttk.Label(area,text="특수장비는 실행 시 정확한 Native 정적 L 캐시가 필요합니다. 장식은 최대 2개, 4세트 충돌·중복 슬롯은 실행 전에 차단됩니다.",
              wraplength=820).pack(anchor="w",pady=7)
    result=[None]
    def apply():
        raw={group:[{k:v.get() for k,v in row.items()} for row in rows]
             for group,rows in fields.items()}
        try:
            converted=selected_rows_from_form(
                raw["special_items"],raw["embellishments"])
            user_scenario({**base_controls(),**converted})
        except Exception as exc:
            messagebox.showerror("장비 옵션 확인",str(exc),parent=window)
            return
        result[0]=raw
        window.destroy()
    buttons=ttk.Frame(area);buttons.pack(fill="x")
    ttk.Button(buttons,text="선택 적용",command=apply).pack(side="right",padx=4)
    ttk.Button(buttons,text="닫기",command=window.destroy).pack(
        side="right",padx=4)
    window.wait_window()
    return result[0]
