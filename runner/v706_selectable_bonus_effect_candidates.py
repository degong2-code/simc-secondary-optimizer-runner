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
    # ITEM_BONUS_SOCKET=6 in the pinned SimC data_enums.hh.
    # Preserve exact raw values, not a socket eligibility decision.
    socket_rows=defaultdict(list)
    bonus_types=defaultdict(set)
    nested_bonus=defaultdict(set)
    for row in rows(paths["ItemBonus"],"ItemBonus"):
        kind=positive(row["Type"])
        bonus=positive(row["ParentItemBonusListID"])
        if bonus:bonus_types[bonus].add(kind)
        if kind==50 and bonus:
            child=positive(row["Value_0"])
            if child:nested_bonus[child].add(bonus)
        if kind==6 and bonus:
            socket_rows[bonus].append({k:row.get(k) for k in
                ("ID","Type","Value_0","Value_1","Value_2")})
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
    # Reuse the same nested bonus relations, without reparsing the CSV.
    socket_links={b:{b} for b in socket_rows}
    queue=deque((b,b) for b in socket_rows)
    count=len(queue)
    while queue:
        child,original=queue.popleft()
        for parent in nested_bonus.get(child,()):
            linked=socket_links.setdefault(parent,set())
            if original in linked:continue
            linked.add(original);count+=1
            need(count<=MAX_PROPAGATED_LINKS,"BONUS_SOCKET_NESTED_LINK_LIMIT")
            queue.append((parent,original))
    groups=defaultdict(set)
    socket_groups=defaultdict(set)
    for row in rows(paths["ItemBonusListGroupEntry"],"ItemBonusListGroupEntry"):
        bonus=positive(row["ItemBonusListID"])
        group=positive(row["ItemBonusListGroupID"])
        if group and bonus in effects:groups[group].add(bonus)
        if group and bonus in socket_links:socket_groups[group].add(bonus)
    parents=defaultdict(set)
    by_tree=defaultdict(set)
    root_effect_nodes=defaultdict(dict)
    socket_by_tree=defaultdict(set)
    for row in rows(paths["ItemBonusTreeNode"],"ItemBonusTreeNode"):
        tree=positive(row["ParentItemBonusTreeID"])
        child=positive(row["ChildItemBonusTreeID"])
        bonus=positive(row["ChildItemBonusListID"])
        group=positive(row["ChildItemBonusListGroupID"])
        if not tree:continue
        if child:parents[child].add(tree)
        if bonus in effects:by_tree[tree].add(bonus)
        if group in groups:by_tree[tree].update(groups[group])
        if bonus in socket_links:socket_by_tree[tree].add(bonus)
        if group in socket_groups:socket_by_tree[tree].update(socket_groups[group])
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
    socket_queue=deque((tree,bonus) for tree,bs in socket_by_tree.items() for bonus in bs)
    count=len(socket_queue)
    need(count<=MAX_PROPAGATED_LINKS,"BONUS_SOCKET_TREE_LINK_LIMIT")
    while socket_queue:
        child,bonus=socket_queue.popleft()
        for parent in parents[child]:
            if bonus not in socket_by_tree[parent]:
                socket_by_tree[parent].add(bonus);count+=1
                need(count<=MAX_PROPAGATED_LINKS,"BONUS_SOCKET_TREE_LINK_LIMIT")
                socket_queue.append((parent,bonus))
    by_item=defaultdict(set)
    socket_by_item=defaultdict(set)
    direct_roots=defaultdict(dict)
    for row in rows(paths["ItemXBonusTree"],"ItemXBonusTree"):
        iid=positive(row["ItemID"])
        if iid not in wanted:continue
        tree=positive(row["ItemBonusTreeID"])
        if socket_by_tree.get(tree):
            socket_by_item[iid].update(socket_by_tree[tree])
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
            "socket_bonus_source_only":{
                "status":"POTENTIAL_SOCKET_BONUS_LINKS_OBSERVED",
                "type":6,"items":[{"item_id":i,
                    "candidate_bonus_list_ids":sorted(bs)}
                    for i,bs in sorted(socket_by_item.items())],
                "bonus_lists":[{"bonus_id":b,"source_bonus_ids":sorted(socket_links[b]),
                    "bonus_types":sorted(bonus_types[b]),
                    "socket_rows":[{"source_bonus_id":original,**r}
                                   for original in sorted(socket_links[b])
                                   for r in socket_rows[original]]}
                    for b in sorted({b for bs in socket_by_item.values() for b in bs})],
                "applicability_verified":False,"automatic_bonus_attachment":False},
            "bonus_type_23_reviewed":True,
            "nested_apply_bonus_reviewed":True,
            "context_free_effect_bonus_candidates":resolved,
            "context_free_effect_bonus_candidate_count":len(resolved),
            "conditional_or_mixed_bonus_candidate_count":len(by_item)-len(resolved),
            "itemlevel_and_acquisition_admission_verified":False,
            "automatic_bonus_attachment":False,
            "full_season_completeness_confirmed":False,"native_calls":0}


def reconcile_effect_options(review,source_rows,*,season_id):
    """Prepare exact effect-only SimC input candidates from scoped source rows.

    Called by the existing sealed season review, not by user-facing UI.
    No item names, expansion IDs or season-specific item/bonus IDs in policy.
    Preserve acquisition uncertainty and never silently replace a mixed list.
    """
    need(review.get("schema")==SCHEMA and type(season_id) is int and season_id>0,
         "BONUS_OPTION_SOURCE_SCOPE_INVALID")
    need(type(source_rows) is list and len(source_rows)<=MAX_ITEMS,
         "BONUS_OPTION_SOURCE_ROWS_INVALID")
    by_id={}
    for row in source_rows:
        iid=row.get("item_id")
        need(type(iid) is int and iid>0 and iid not in by_id,
             "BONUS_OPTION_DUPLICATE_OR_INVALID_ITEM")
        by_id[iid]=row
    resolved={r["item_id"]:r for r in review.get("context_free_effect_bonus_candidates",[])}
    options=[];pending=[]
    for item in review["items"]:
        iid=item["item_id"]
        row=by_id.get(iid)
        if row is None:
            pending.append({"item_id":iid,"reason":"NO_SCOPED_PHYSICAL_SOURCE_ROW"})
            continue
        if iid not in resolved:
            pending.append({"item_id":iid,"reason":"CONDITIONAL_OR_MIXED_EFFECT_BONUS"})
            continue
        if row.get("direct_item_effect_record") is not False:
            pending.append({"item_id":iid,"reason":"DIRECT_OR_UNKNOWN_EFFECT_SOURCE_REQUIRES_MERGE"})
            continue
        origins=[]
        for origin in row.get("acquisition_sources",[]):
            if (origin.get("source") in ("raid_journal","mplus_journal")
                    and type(origin.get("journal_encounter_id")) is int
                    and origin["journal_encounter_id"]>0
                    and type(origin.get("journal_instance_id")) is int
                    and origin["journal_instance_id"]>0
                    and type(origin.get("display_season_id")) is int
                    and origin["display_season_id"] in (0,season_id)):
                origins.append(origin)
        if not origins:
            pending.append({"item_id":iid,"reason":"NO_SCOPED_JOURNAL_ORIGIN"})
            continue
        proof=resolved[iid]
        bonuses=proof["bonus_ids"]
        need(bool(bonuses) and all(type(b) is int and b>0 for b in bonuses),
             "BONUS_OPTION_IDS_INVALID")
        # This is the source-level required option, not an entire equipped
        # variant. Preserve all effect IDs and exact original acquisition
        # conditions for the later normal catalogue/selected profile join.
        options.append({"item_id":iid,"name":row["name"],"inventory_type":row["slot"],
            "required_options":{"bonus_id":"/".join(map(str,bonuses))},
            "bonus_effects":proof["bonus_effects"],
            "acquisition_sources":origins,
            "conflicting_source_occurrences":row.get("conflicting_source_occurrences",[]),
            "explicit_current_season_origin":any(o["display_season_id"]==season_id for o in origins),
            "source_input_only":True,
            "itemlevel_and_acquisition_admission_verified":False})
    return {"effect_option_candidates":options,
            "effect_option_candidate_count":len(options),
            "effect_option_pending":pending}
