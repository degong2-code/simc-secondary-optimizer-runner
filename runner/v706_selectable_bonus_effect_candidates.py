#!/usr/bin/env python3
"""Source-only potential bonus-effect links; never infer obtainable variants.

A shared tree or group does not establish applicability. Retain exact
candidate item, bonus list and effect IDs; the original CSVs own conditions.
No SimC effect emulation, automatic bonus attachment, Native or budget edits.
"""
from collections import defaultdict, deque
import csv
from pathlib import Path

SCHEMA="v706_selectable_bonus_effect_candidates_v1"
COLUMNS={
    "ItemXBonusTree":("ItemID","ItemBonusTreeID"),
    "ItemBonusTreeNode":("ParentItemBonusTreeID","ChildItemBonusTreeID",
                         "ChildItemBonusListID","ChildItemBonusListGroupID"),
    "ItemBonusListGroupEntry":("ItemBonusListGroupID","ItemBonusListID"),
    "ItemBonus":("ParentItemBonusListID","Type","Value_0"),
}
MAX_BYTES={"ItemXBonusTree":12_000_000,"ItemBonusTreeNode":5_000_000,
           "ItemBonusListGroupEntry":32_000_000,"ItemBonus":64_000_000}
MAX_ROWS=2_000_000
MAX_PROPAGATED_LINKS=2_000_000
MAX_ITEMS=30000

class BonusReviewBlocked(ValueError):pass

def need(ok,code):
    if not ok:raise BonusReviewBlocked(code)

def positive(value):
    try:return max(int(value),0)
    except (TypeError,ValueError):
        raise BonusReviewBlocked("BONUS_SOURCE_NUMERIC_FIELD_INVALID")

def rows(path,table):
    p=Path(path)
    need(p.is_file() and not p.is_symlink() and
         0<p.stat().st_size<=MAX_BYTES[table],"BONUS_SOURCE_SIZE:"+table)
    with p.open(encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream)
        need(set(COLUMNS[table])<=set(reader.fieldnames or ()),
             "BONUS_SOURCE_COLUMNS:"+table)
        for i,row in enumerate(reader):
            need(i<MAX_ROWS,"BONUS_SOURCE_ROW_LIMIT:"+table)
            yield row

def discover(item_ids,paths):
    wanted=set(item_ids)
    need(0<len(wanted)<=MAX_ITEMS and all(type(i) is int and i>0
         for i in wanted),"BONUS_REVIEW_ITEM_SCOPE_INVALID")
    need(set(paths)==set(COLUMNS),"BONUS_REVIEW_TABLE_SET_INVALID")
    # Scan only effect-adding bonus rows. 23 is SimC ADD_ITEM_EFFECT.
    effects=defaultdict(set)
    for row in rows(paths["ItemBonus"],"ItemBonus"):
        if positive(row["Type"])!=23:continue
        bonus=positive(row["ParentItemBonusListID"])
        effect=positive(row["Value_0"])
        if bonus and effect:effects[bonus].add(effect)
    groups=defaultdict(set)
    for row in rows(paths["ItemBonusListGroupEntry"],"ItemBonusListGroupEntry"):
        bonus=positive(row["ItemBonusListID"])
        group=positive(row["ItemBonusListGroupID"])
        if group and bonus in effects:groups[group].add(bonus)
    parents=defaultdict(set)
    by_tree=defaultdict(set)
    for row in rows(paths["ItemBonusTreeNode"],"ItemBonusTreeNode"):
        tree=positive(row["ParentItemBonusTreeID"])
        child=positive(row["ChildItemBonusTreeID"])
        bonus=positive(row["ChildItemBonusListID"])
        group=positive(row["ChildItemBonusListGroupID"])
        if not tree:continue
        if child:parents[child].add(tree)
        if bonus in effects:by_tree[tree].add(bonus)
        if group in groups:by_tree[tree].update(groups[group])
    # Reverse propagation avoids repeatedly traversing shared trees for
    # each item. The pair set makes cycles harmless and bounds the work.
    pending=deque((t,b) for t,bs in by_tree.items() for b in bs)
    links=len(pending)
    need(links<=MAX_PROPAGATED_LINKS,"BONUS_TREE_LINK_LIMIT")
    while pending:
        child,bonus=pending.popleft()
        for parent in parents[child]:
            if bonus not in by_tree[parent]:
                by_tree[parent].add(bonus)
                links+=1
                need(links<=MAX_PROPAGATED_LINKS,"BONUS_TREE_LINK_LIMIT")
                pending.append((parent,bonus))
    by_item=defaultdict(set)
    for row in rows(paths["ItemXBonusTree"],"ItemXBonusTree"):
        iid=positive(row["ItemID"])
        if iid not in wanted:continue
        tree=positive(row["ItemBonusTreeID"])
        if tree in by_tree and by_tree[tree]:
            by_item[iid].update(by_tree[tree])
    return {"schema":SCHEMA,
            "status":"POTENTIAL_BONUS_EFFECT_LINKS_OBSERVED",
            "reviewed_item_count":len(wanted),
            "candidate_item_count":len(by_item),
            "items":[{"item_id":i,"bonus_effects":[
                {"bonus_id":b,"item_effect_ids":sorted(effects[b])}
                for b in sorted(bs)],
                "applicable_variant_verified":False}
                for i,bs in sorted(by_item.items())],
            "bonus_type_23_reviewed":True,
            "nested_apply_bonus_reviewed":False,
            "automatic_bonus_attachment":False,
            "full_season_completeness_confirmed":False,"native_calls":0}
