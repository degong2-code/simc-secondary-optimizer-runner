"""v129: independent pre-v129 readers vs common source gear/settings/APL, Native0."""
from __future__ import annotations
import pathlib,re,sys,tempfile,unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v101_common_representative_equipment as common
import v127_dps_source_metadata as metadata
import v129_common_source_fields as fields

def old_equipment(source,slots,*,need,duplicate_prefix,
                  missing_id_prefix,include_gem_enchant=False):
    """Independent original v082/v083/v084 regex and v104 comma-field loops."""
    ids={};options={}
    for line in source.splitlines():
        if line.startswith("# Gear Summary"):
            break
        slot,sep,value=line.partition("=")
        if not sep or slot not in slots:
            continue
        need(slot not in ids,duplicate_prefix+slot)
        if include_gem_enchant:
            fields_list=value.split(",")
            identifiers=[x[3:] for x in fields_list[1:] if x.startswith("id=")]
            need(len(identifiers)==1 and identifiers[0].isdigit(),
                 missing_id_prefix+slot)
            ids[slot]=int(identifiers[0])
            options[slot]={}
            for token in fields_list[1:]:
                k,_,v=token.partition("=")
                if k in ("gem_id","enchant","enchant_id") and v:
                    options[slot][k]=v
        else:
            match=re.search(r"(?:^|,)id=(\d+)(?:,|$)",value)
            need(match is not None,missing_id_prefix+slot)
            ids[slot]=int(match.group(1))
    return ids,options

def old_settings(source,keys,*,need,duplicate_prefix=None):
    result={}
    for line in source.splitlines():
        k,sep,value=line.partition("=")
        if sep and k in keys:
            if duplicate_prefix is not None:
                need(k not in result,duplicate_prefix+k)
            result[k]=value
    return result

def old_matching_lines(source,prefix):
    return [line for line in source.splitlines() if line.startswith(prefix)]

class CommonSourceFields(unittest.TestCase):
    @staticmethod
    def need(ok,reason):
        if not ok:
            raise ValueError(reason)

    def test_six_pinned_source_factories_before_after_byte_parity(self):
        for record in metadata.SOURCE_BACKED:
            with self.subTest(spec=record.key),tempfile.TemporaryDirectory() as td:
                folder=pathlib.Path(td)
                with mock.patch.object(fields,"equipment",
                                       side_effect=old_equipment), \
                     mock.patch.object(fields,"settings",
                                       side_effect=old_settings), \
                     mock.patch.object(fields,"matching_lines",
                                       side_effect=old_matching_lines):
                    old=common.source_backed_gear(record.key,folder,334,self.need)
                new=common.source_backed_gear(record.key,folder,334,self.need)
                self.assertEqual(new,old)
                self.assertFalse((folder/"simc_results").exists())

    def test_duplicate_and_missing_item_diagnostics_are_source_scoped(self):
        for mode in (False,True):
            source=("head=some_armor,id=271510,gem_id=240967\n"
                    "head=some_armor,id=271510\n")
            with self.subTest(mode=mode):
                with self.assertRaisesRegex(ValueError,"SOURCE_DUPLICATE:head"):
                    fields.equipment(source,("head",),need=self.need,
                        duplicate_prefix="SOURCE_DUPLICATE:",
                        missing_id_prefix="SOURCE_ID_MISSING:",
                        include_gem_enchant=mode)
                with self.assertRaisesRegex(ValueError,"SOURCE_ID_MISSING:head"):
                    fields.equipment("head=bad_without_id\n",("head",),
                        need=self.need,duplicate_prefix="SOURCE_DUPLICATE:",
                        missing_id_prefix="SOURCE_ID_MISSING:",
                        include_gem_enchant=mode)

    def test_modifiers_and_stopping_at_original_gear_summary(self):
        source=('head=x,id=271510,gem_id=240967,enchant=77,enchant_id=11\n'
                'neck=x,id=999\n'
                '# Gear Summary\n'
                'finger1=ignored,id=777\n')
        ids,opts=fields.equipment(source,("head","neck","finger1"),
                       need=self.need,duplicate_prefix="D:",
                       missing_id_prefix="I:",include_gem_enchant=True)
        self.assertEqual(ids,{"head":271510,"neck":999})
        self.assertEqual(opts["head"],
                         {"gem_id":"240967","enchant":"77","enchant_id":"11"})
        self.assertNotIn("finger1",ids)
        old_ids,old_opts=old_equipment(source,("head","neck","finger1"),
                       need=self.need,duplicate_prefix="D:",
                       missing_id_prefix="I:",include_gem_enchant=True)
        self.assertEqual((ids,opts),(old_ids,old_opts))

    def test_character_and_apl_values_exact_with_duplicate_guard(self):
        source=('rogue="original"\nspec=subtlety\nrace=dwarf\n'
                'talents=C123\nflask=something\n'
                'actions=/start\nactions+=/finish\n'
                'race=human\n')
        keys=("race","spec","talents","flask")
        with self.assertRaisesRegex(ValueError,"SOURCE_DUPLICATE_SETTING:race"):
            fields.settings(source,keys,need=self.need,
                           duplicate_prefix="SOURCE_DUPLICATE_SETTING:")
        values=fields.settings(source,keys)
        self.assertEqual(values,old_settings(source,keys,need=self.need))
        self.assertEqual(values["race"],"human")
        self.assertEqual(fields.matching_lines(source,"actions"),
                         old_matching_lines(source,"actions"))
        self.assertEqual(fields.matching_lines(source,"actions"),
                         ["actions=/start","actions+=/finish"])

    def test_no_source_native_or_gear_db_side_effects(self):
        source='paladin="MID2"\nmain_hand=x,id=270555\n'
        ids,opts=fields.equipment(source,("main_hand",),need=self.need,
                      duplicate_prefix="D:",missing_id_prefix="I:")
        self.assertEqual(ids,{"main_hand":270555})
        self.assertEqual(opts,{})
        self.assertNotIn("json2",fields.settings(source,("json2",)))
        with self.assertRaisesRegex(fields.SourceFieldsBlocked,"I:head"):
            fields.equipment("head=no_id\n",("head",),
                duplicate_prefix="D:",missing_id_prefix="I:")

if __name__=="__main__":
    unittest.main()
