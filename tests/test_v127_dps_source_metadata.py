"""P1 v127 declarative six-spec source registry. Offline, Native 0."""
from __future__ import annotations
import dataclasses,hashlib,pathlib,sys,tempfile,unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v101_common_representative_equipment as common
import v103_source_observed_weapon_types as weapon
import v104_shared_pinned_rogue_shaman_composer as old_shared
import v127_dps_source_metadata as data

class SourceRegistry(unittest.TestCase):
    @staticmethod
    def need(valid,code):
        if not valid:raise ValueError(code)

    def test_exact_six_spec_source_metadata_and_pinned_git_blobs(self):
        self.assertTrue(data.validate())
        self.assertTrue(common.validate_source_registry())
        self.assertEqual(set(data.BY_SPEC),set(weapon.EXECUTABLE_SOURCES))
        self.assertEqual(len(data.BY_SPEC),7)
        self.assertEqual(set(common.ARCHETYPES),set(data.BY_SPEC))
        self.assertEqual(set(common.CLASS_TIER_ITEMS),
                         {"warrior","paladin","mage","hunter","rogue","shaman"})
        for record in data.SOURCE_BACKED:
            with self.subTest(key=record.key):
                full=ROOT/"integration_probes"/"fixtures"/record.source_fixture
                self.assertTrue(full.is_file())
                content=full.read_bytes()
                sha=hashlib.sha1(
                    b"blob "+str(len(content)).encode("ascii")+b"\0"+content
                ).hexdigest()
                self.assertEqual(sha,record.source_git_blob)
                filename,producer,form,F=common.ARCHETYPES[record.key]
                self.assertTrue(callable(producer))
                self.assertEqual((filename,form,F),
                     (record.source_fixture,record.weapon_form,
                      record.flask_vector()))
                self.assertEqual(common.CLASS_TIER_ITEMS[record.key[0]],
                                 record.tier_ids())
                self.assertEqual(common.FIFTH_TIER[record.key],
                                 record.fifth_replacement())
                self.assertEqual(record.armor_family,
                                 common.CLASS_ARMOR[record.character_class])

    def test_every_producer_still_emits_same_source_backed_gear_inputs(self):
        for record in data.SOURCE_BACKED:
            with self.subTest(key=record.key),tempfile.TemporaryDirectory() as td:
                text,cfg,rows,groups,form,F=common.source_backed_gear(
                    record.key,pathlib.Path(td),334,self.need)
                self.assertEqual((cfg["character"]["class"],
                                  cfg["character"]["spec"]),record.key)
                self.assertEqual(form,record.weapon_form)
                self.assertEqual(F,record.flask_vector())
                self.assertEqual({k:rows[k]["item_id"] for k,v
                                  in groups.items() if v=="tier"},
                                 {slot:id_ for slot,id_ in record.tier_five
                                  if slot!=record.fifth_ordinary[0]})
                self.assertEqual(rows[record.fifth_ordinary[0]]["item_id"],
                                 record.fifth_ordinary[1])
                self.assertEqual(sum(F.values()),165)
                self.assertIn("actions=",text)

    def test_unknown_specialization_remains_not_enabled(self):
        with self.assertRaisesRegex(data.SourceMetadataBlocked,
                                    "REGISTERED_ARCHETYPE_NOT_SOURCE_BACKED"):
            data.get(("priest","shadow"))
        self.assertNotIn(("priest","shadow"),common.ARCHETYPES)
        self.assertNotIn(("evoker","devastation"),common.ARCHETYPES)

    def test_metadata_provenance_and_weapon_change_fail_closed(self):
        existing=data.SOURCE_BACKED[0]
        for change,error in (
            ({"source_git_blob":"f"*40},"REGISTERED_SOURCE_PROVENANCE_DRIFT"),
            ({"weapon_form":"ranged"},"REGISTERED_WEAPON_SOURCE_DRIFT"),
            ({"tier_five":tuple(existing.tier_five[:4])},
             "REGISTERED_FIVE_TIER_NOT_SOURCE_BACKED"),
            ({"flask_F":(0,0,0,0)},"REGISTERED_FLASK_STATIC_F_DRIFT")):
            with self.subTest(change=change):
                bad=dataclasses.replace(existing,**change)
                rows=(bad,)+data.SOURCE_BACKED[1:]
                with mock.patch.object(data,"SOURCE_BACKED",rows), \
                     mock.patch.object(data,"BY_SPEC",
                                       {item.key:item for item in rows}):
                    with self.assertRaisesRegex(data.SourceMetadataBlocked,error):
                        data.validate()

    def test_source_provider_contract_drift_is_not_silent(self):
        old=old_shared.PROFILES[("rogue","subtlety")]
        with mock.patch.dict(old,{"source_sha":"f"*40}):
            with self.assertRaisesRegex(data.SourceMetadataBlocked,
                                        "V104_LEGACY_PRODUCER_METADATA_DRIFT"):
                common.validate_source_registry()
        original=data.SOURCE_BACKED[-1]
        altered=dataclasses.replace(original,armor_family="plate")
        with mock.patch.object(data,"SOURCE_BACKED",
                               data.SOURCE_BACKED[:-1]+(altered,)), \
             mock.patch.object(data,"BY_SPEC",
                  {**data.BY_SPEC,altered.key:altered}):
            with self.assertRaisesRegex(data.SourceMetadataBlocked,
                                        "REGISTERED_ARMOR_FAMILY_DRIFT"):
                common.validate_source_registry()

    def test_registry_is_frozen_input_data_not_mutable_effect_model(self):
        e=data.get(("shaman","elemental"))
        with self.assertRaises(dataclasses.FrozenInstanceError):
            e.weapon_form="dual_two_hand"
        self.assertEqual(e.fifth_replacement(),("head",271483,249317))
        self.assertEqual(e.flask_vector()["crit_rating"],165)

if __name__=="__main__":
    unittest.main()
