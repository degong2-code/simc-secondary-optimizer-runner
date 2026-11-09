#!/usr/bin/env python3
"""Explicit DK runeforge weapon enchant_id selection. SimC owns effects/DPS."""
from __future__ import annotations

# IDs observed in pinned DK SimC sources and public SimC runeforge docs.
# User choice only, not automatic seasonal registration or an effect Gate.
RUNE_IDS=frozenset((3368,3370,3847,6241,6242,6244,6245))
HANDS=("main_hand","off_hand")
DUAL_FORMS=frozenset(("dual_one_hand","dual_two_hand"))

def check_input(*,selection,class_name,weapon_form,need):
    if selection is None:return {}
    need(type(selection) is dict and bool(selection),
         "DK_RUNEFORGE_NONEMPTY_SELECTION_REQUIRED")
    need(class_name=="deathknight","DK_RUNEFORGE_CLASS_ONLY")
    need(set(selection)<=set(HANDS),"DK_RUNEFORGE_WEAPON_HAND_UNKNOWN")
    need("off_hand" not in selection or weapon_form in DUAL_FORMS,
         "DK_RUNEFORGE_OFFHAND_REQUIRES_DUAL_WEAPON")
    need(all(type(v) is int and 0<v<10_000_000
             for v in selection.values()),"DK_RUNEFORGE_ID_INVALID")
    return {hand:selection[hand] for hand in HANDS if hand in selection}

def normalize(*,selection,class_name,weapon_form,need,admitted_ids=RUNE_IDS):
    chosen=check_input(selection=selection,class_name=class_name,
                       weapon_form=weapon_form,need=need)
    need(set(chosen.values())<=set(admitted_ids),
         "DK_RUNEFORGE_ID_UNSUPPORTED")
    return chosen

def apply(*,rows,selection,class_name,weapon_form,need,
          admitted_ids=RUNE_IDS):
    """Edit the user-selected weapon item option, never G/J/F/O/B/T."""
    chosen=normalize(selection=selection,class_name=class_name,
                     weapon_form=weapon_form,need=need,
                     admitted_ids=admitted_ids)
    for hand,enchant_id in chosen.items():
        row=rows.get(hand)
        need(type(row) is dict and row.get("slot")==hand and
             type(row.get("item_id")) is int and row["item_id"]>0,
             "DK_RUNEFORGE_REPRESENTATIVE_WEAPON_REQUIRED")
        options=row.get("options")
        need(type(options) is dict,"DK_RUNEFORGE_WEAPON_OPTIONS_REQUIRED")
        prior=options.get("enchant_id")
        need("enchant" not in options and
             (prior is None or (type(prior) is str and
              prior.isdecimal() and int(prior) in (RUNE_IDS|set(admitted_ids)))),
             "DK_RUNEFORGE_OTHER_ENCHANT_CONFLICT")
        options["enchant_id"]=str(enchant_id)
    return chosen
