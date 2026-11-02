"""v211 uses the same source classifiers on a *new* season/build.

Only synthetic source bytes: no Native, no Wago HTTP, no old v202/v206
evidence, no new-season approval or real current-season G/J/F/O.
"""
from __future__ import annotations

import copy
import json
import pathlib
import tempfile
import unittest

from runner import v211_enchant_source_effect_classification as v
from tests.test_v211_enchant_source_effect_classification import ENUMS

BUILD="12.2.0.99999"
REV="b"*40

FILE_PATHS={
 "permanent_enchant.inc":"engine/dbc/generated/permanent_enchant.inc",
 "spell_item_enchantment.inc":"engine/dbc/generated/spell_item_enchantment.inc",
 "spelltext_data.inc":"engine/dbc/generated/spelltext_data.inc",
 "data_enums.hh":"engine/dbc/data_enums.hh",
 "unique_gear.cpp":"engine/player/unique_gear_newseason.cpp",
 "enchants.cpp":"engine/item/enchants.cpp"}


def fixture_source():
    mods=[
      (91001,"enchant_ring__new_haste",5,36,0),
      (91002,"enchant_weapon__new_proc",3,1234567,0)]
    generated={
        "permanent_enchant.inc":
            "// Permanent enchants, wow build "+BUILD+"\n"+
            "\n".join(
                f'{{ {id}, 2, {4 if id==91001 else 2}, 0x{0x800 if id==91001 else 0:x}, 0x1f, "{token}" }},'
                for id,token,*_ in mods)+"\n",
        "spell_item_enchantment.inc":
            "// SpellItemEnchantment, wow build "+BUILD+"\n"+
            "\n".join(
                f'{{ {id}, 0, -7, 0, 80, 120, 0, 0, 0, '
                f'{{ {typ}, 0, 0 }}, {{ 0, 0, 0 }}, '
                f'{{ {prop}, 0, 0 }}, '
                f'{{ 0.8623f, 0.0000f, 0.0000f }}, 0, "New {id}" }},'
                for id,token,typ,prop,_ in mods)+"\n",
        "spelltext_data.inc":
            '// SpellText, wow build '+BUILD+'\n'+
            '{ 1234567, "Occasionally grants haste when striking.", 0, 0 },\n',
        "data_enums.hh":ENUMS,
        "unique_gear.cpp":
            'register_special_effect( { 1234567 }, enchants::stat_weapon_enchant );\n',
        "enchants.cpp":
            'case ITEM_ENCHANTMENT_STAT: break;\n'
            'case ITEM_ENCHANTMENT_EQUIP_SPELL: break;\n'
            'passive_enchant += 1;\n'}
    rows=[]
    for id,token,*_ in mods:
        inv=0x800 if id==91001 else 0
        rows.append({"enchant_id":id,"simc_token":token,
                     "quality_rank":2,
                     "item_class":4 if id==91001 else 2,
                     "inventory_type_mask":inv,
                     "item_subclass_mask":31,
                     "inventory_type_options":[i for i in range(1,31)
                                               if inv&(1<<i)],
                     "user_selectable":False})
    season={
        "schema":v.V191_SCHEMA,
        "source_first":True,"automatic_ui_promotion":False,
        "native_calls":0,"network_calls_by_compiler":0,
        "simc_revision":REV,"game_build":BUILD,
        "enchants":{"current_season":{
            "count":len(rows),"highest_rank_candidates":rows}}}
    return season,generated


def put_sources(folder,generated):
    manifest={"schema":v.FRESH_SOURCE_SCHEMA,
              "game_build":BUILD,"simc_revision":REV,
              "files":{}}
    for key,plain in generated.items():
        raw=plain.encode("utf8")
        (folder/key).write_bytes(raw)
        manifest["files"][key]={
            "source_path":FILE_PATHS[key],"size_bytes":len(raw),
            "sha256":v.sha256(raw),"git_blob_sha1":v.git_blob_sha(raw)}
    return manifest


class NewSeasonV211Tests(unittest.TestCase):
    def test_new_build_variable_rows_and_zero_old_native_e_or_ui(self):
        with tempfile.TemporaryDirectory() as d:
            folder=pathlib.Path(d)
            season,generated=fixture_source()
            manifest=put_sources(folder,generated)
            result=v.compile_fresh_season(season,folder,manifest)
        self.assertEqual(result["simc_commit"],REV)
        self.assertEqual(result["season_game_build"],BUILD)
        self.assertEqual(result["counts"]["total"],2)
        self.assertEqual(result["counts"]["static_chmv_rating"],1)
        self.assertEqual(result["counts"]["spell_effects"],1)
        self.assertEqual(result["counts"]["native_E_measured"],0)
        self.assertEqual(result["counts"]["locked"],2)
        self.assertFalse(result["automatic_ui_promotion"])
        self.assertFalse(result["source_retrieval_independently_authenticated_here"])
        self.assertEqual(result["native_calls"],0)
        self.assertEqual({r["selection_status"] for r in result["rows"]},
            {"LOCKED_PENDING_CURRENT_SEASON_ITEM_EFFECT_PROOF"})
        self.assertTrue(all(r["native_E_evidence"]["static_E"] is None
                            for r in result["rows"]))
        self.assertEqual(result["rows"][0]["static_chmv_stats"],
                         ["haste_rating"])
        self.assertEqual(result["rows"][1]["dynamic_chmv_proc_roles"],
                         ["TEMPORARY_HASTE_RATING_PROC"])

    def test_wrong_build_raw_file_hash_and_manifest_commit_are_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            folder=pathlib.Path(d)
            season,generated=fixture_source()
            manifest=put_sources(folder,generated)
            altered=copy.deepcopy(manifest)
            altered["simc_revision"]="a"*40
            with self.assertRaisesRegex(v.SourceBlocked,
                                        "MANIFEST_BUILD_OR_FILES_INVALID"):
                v.compile_fresh_season(season,folder,altered)
            (folder/"data_enums.hh").write_text(ENUMS+"// changed\n")
            with self.assertRaisesRegex(v.SourceBlocked,
                                        "SOURCE_BYTES_OR_GIT_BLOB_CHANGED"):
                v.compile_fresh_season(season,folder,manifest)
            (folder/"data_enums.hh").write_text(ENUMS)
            (folder/"spelltext_data.inc").write_text(
                generated["spelltext_data.inc"].replace(BUILD,"12.1.5.70575"))
            fixed=copy.deepcopy(manifest)
            raw=(folder/"spelltext_data.inc").read_bytes()
            fixed["files"]["spelltext_data.inc"].update({
                "sha256":v.sha256(raw),"git_blob_sha1":v.git_blob_sha(raw)})
            with self.assertRaisesRegex(v.SourceBlocked,
                                        "GENERATED_BUILD_DRIFT"):
                v.compile_fresh_season(season,folder,fixed)

    def test_prior_enchant_ids_do_not_inherit_old_user_approval(self):
        with tempfile.TemporaryDirectory() as d:
            folder=pathlib.Path(d)
            season,generated=fixture_source()
            season["enchants"]["current_season"]["highest_rank_candidates"][0][
                "enchant_id"]=7967
            generated["permanent_enchant.inc"]=generated["permanent_enchant.inc"].replace(
                "91001","7967")
            generated["spell_item_enchantment.inc"]=generated["spell_item_enchantment.inc"].replace(
                "91001","7967")
            manifest=put_sources(folder,generated)
            result=v.compile_fresh_season(season,folder,manifest)
        item=result["rows"][0]
        self.assertEqual(item["enchant_id"],7967)
        self.assertEqual(item["selection_status"],
                         "LOCKED_PENDING_CURRENT_SEASON_ITEM_EFFECT_PROOF")
        self.assertIsNone(item["native_E_evidence"]["static_E"])
        self.assertFalse(item["native_E_evidence"]["ui_selectable"])
        self.assertEqual(result["counts"]["user_selectable_existing_scope"],0)

    def test_fresh_cli_outputs_two_unapproved_entries(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d); src=root/"sources";src.mkdir()
            season,generated=fixture_source()
            manifest=put_sources(src,generated)
            p=root/"v191.json";p.write_text(json.dumps(season))
            m=root/"manifest.json";m.write_text(json.dumps(manifest))
            out=root/"v211.json"
            code=v.main(["--fresh-v191",str(p),"--fresh-source-dir",
                         str(src),"--fresh-manifest",str(m),"--out",str(out)])
            self.assertEqual(code,0)
            doc=json.loads(out.read_text())
            self.assertEqual(doc["counts"]["total"],2)
            self.assertFalse(doc["automatic_ui_promotion"])
            self.assertEqual(doc["counts"]["native_E_measured"],0)

    def test_cannot_self_authorize_candidate_using_source_flag(self):
        with tempfile.TemporaryDirectory() as d:
            folder=pathlib.Path(d)
            season,generated=fixture_source()
            manifest=put_sources(folder,generated)
            season["enchants"]["current_season"][
                "highest_rank_candidates"][0]["user_selectable"]=True
            with self.assertRaisesRegex(v.SourceBlocked,
                                        "ID_TOKEN_MASK_OR_OPTION_INVALID"):
                v.compile_fresh_season(season,folder,manifest)


if __name__=="__main__": unittest.main()
