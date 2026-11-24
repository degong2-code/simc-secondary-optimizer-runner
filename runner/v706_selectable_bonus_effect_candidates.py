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
# SimC item_bonus_type enum: DESC=4, ADD_ITEM_EFFECT=23, APPLY_BONUS=50.
# Other rows may affect scaling, CHMV, sockets or applicability; do not
# automatically serialize mixed lists as effect-only options.
EFFECT_ONLY_TYPES=frozenset((4,23))
NODE_CONTEXT_FIELDS=("ItemContext","ChildItemLevelSelectorID",
    "IblGroupPointsModSetID","MinMythicPlusLevel","MaxMythicPlusLevel",
    "ItemCreationContextGroupID","Flags")

class BonusReviewBlocked(ValueError):pass

def need(ok,code):
    if not ok:raise BonusReviewBlocked(code)

def positive(value):
    try:return max(int(value),0)
    except (TypeError,ValueError):
        raise BonusReviewBlocked("BONUS_SOURCE_NUMERIC_FIELD_INVALID")

def valid_raw_table(raw,table):
    """One bounded header validator shared by live and diagnostic acquisition."""
    if not isinstance(raw,bytes) or not 0<len(raw)<=MAX_BYTES[table]:
        return False
    try:
        end=raw.find(b"\n",0,65536)
        if end<0:end=min(len(raw),65536)
        header=raw[:end].decode("utf-8-sig").rstrip("\r")
        return set(COLUMNS[table])<=set(next(csv.reader([header])))
    except (UnicodeError,csv.Error,IndexError,StopIteration):
        return False


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
    bonus_types=defaultdict(set)
    nested_bonus=defaultdict(set)
    for row in rows(paths["ItemBonus"],"ItemBonus"):
        kind=positive(row["Type"])
        bonus=positive(row["ParentItemBonusListID"])
        if bonus:bonus_types[bonus].add(kind)
        if kind==50 and bonus:
            child=positive(row["Value_0"])
            if child:nested_bonus[child].add(bonus)
        if kind!=23:continue
        effect=positive(row["Value_0"])
        if bonus and effect:effects[bonus].add(effect)
    # Nested APPLY_BONUS is a discovery relationship only. Propagate
    # reachable effects, but never treat an inherited list as a standalone
    # unconditional effect-only variant. Pair dedup handles cycles.
    queue=deque((b,e) for b,es in effects.items() for e in es)
    nested_links=len(queue)
    while queue:
        child,effect=queue.popleft()
        for parent in nested_bonus.get(child,()):
            if effect in effects[parent]:continue
            effects[parent].add(effect)
            nested_links+=1
            need(nested_links<=MAX_PROPAGATED_LINKS,"BONUS_NESTED_LINK_LIMIT")
            queue.append((parent,effect))
    groups=defaultdict(set)
    for row in rows(paths["ItemBonusListGroupEntry"],"ItemBonusListGroupEntry"):
        bonus=positive(row["ItemBonusListID"])
        group=positive(row["ItemBonusListGroupID"])
        if group and bonus in effects:groups[group].add(bonus)
    parents=defaultdict(set)
    by_tree=defaultdict(set)
    root_effect_nodes=defaultdict(dict)
    for row in rows(paths["ItemBonusTreeNode"],"ItemBonusTreeNode"):
        tree=positive(row["ParentItemBonusTreeID"])
        child=positive(row["ChildItemBonusTreeID"])
        bonus=positive(row["ChildItemBonusListID"])
        group=positive(row["ChildItemBonusListGroupID"])
        if not tree:continue
        if child:parents[child].add(tree)
        if bonus in effects:by_tree[tree].add(bonus)
        if group in groups:by_tree[tree].update(groups[group])
        # A direct root leaf with an effect-only list and explicit zero
        # values in ALL known context fields is a bounded safe serializer
        # candidate. Missing/unknown fields, groups, mixed rows, child
        # paths and nested apply remain review-only, not inferred zero.
        if (bonus in effects and not child and not group
                and bonus_types[bonus]<=EFFECT_ONLY_TYPES
                and 23 in bonus_types[bonus]
                and row.get("ID","").isdigit()
                and int(row["ID"])>0
                and row.get("ChildItemBonusTreeID")=="0"
                and row.get("ChildItemBonusListGroupID")=="0"
                and all(row.get(k)=="0" for k in NODE_CONTEXT_FIELDS)):
            root_effect_nodes[tree].setdefault(bonus,set()).add(int(row["ID"]))
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
    direct_roots=defaultdict(dict)
    for row in rows(paths["ItemXBonusTree"],"ItemXBonusTree"):
        iid=positive(row["ItemID"])
        if iid not in wanted:continue
        tree=positive(row["ItemBonusTreeID"])
        if tree in by_tree and by_tree[tree]:
            by_item[iid].update(by_tree[tree])
            for bonus,nodes in root_effect_nodes.get(tree,{}).items():
                direct_roots[iid].setdefault(bonus,[]).append({
                    "root_tree_id":tree,"node_ids":sorted(nodes)})
    # All potential effect lists for the item must be covered by direct
    # context-free leaves. If any conditional alternatives exist, preserve
    # the item for later resolution without auto-selecting a partial list.
    resolved=[]
    for iid,bonuses in sorted(by_item.items()):
        proof=direct_roots.get(iid,{})
        if set(proof)!=bonuses:continue
        resolved.append({"item_id":iid,"bonus_ids":sorted(bonuses),
            "source_basis":"DIRECT_ROOT_CONTEXT_FREE_EFFECT_ONLY_LISTS",
            "bonus_effects":[{"bonus_id":b,"item_effect_ids":sorted(effects[b]),
                "roots":sorted(proof[b],key=lambda x:x["root_tree_id"])}
                for b in sorted(bonuses)],
            "variant_source_conditions_resolved":True})
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
            "nested_apply_bonus_reviewed":True,
            "context_free_effect_bonus_candidates":resolved,
            "context_free_effect_bonus_candidate_count":len(resolved),
            "conditional_or_mixed_bonus_candidate_count":len(by_item)-len(resolved),
            "itemlevel_and_acquisition_admission_verified":False,
            "automatic_bonus_attachment":False,
            "full_season_completeness_confirmed":False,"native_calls":0}
