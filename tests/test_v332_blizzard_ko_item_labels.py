"""v332: never manufacture or drift official localized item IDs."""
import tempfile,pathlib,json,unittest,sys
from unittest import mock

# Production v332 is a runner-local script (v155/v167 top-level imports).
# The standalone unittest discovery process does not add runner/ itself.
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
from runner import v332_blizzard_ko_item_labels as loc

class OfficialKoreanNames(unittest.TestCase):
    def test_blizzard_item_id_and_locale_proof(self):
        row=loc.row_from_api(268249,{"id":268249,"name":"예시 공식 응답"})
        self.assertEqual(row["item_id"],268249)
        self.assertEqual(row["api_url"],loc.url_for(268249))
        with self.assertRaises(loc.LocaleBlocked):
            loc.row_from_api(268249,{"id":268250,"name":"다른 아이템"})
        with self.assertRaises(loc.LocaleBlocked):
            loc.row_from_api(268249,{"id":268249,"name":""})

    def test_load_verified_only_matching_catalog_and_ids(self):
        row=loc.row_from_api(268249,{"id":268249,"name":"테스트용 가상 응답"})
        doc=loc.build_document("12.1.5.70575",[268249,268250],[row],
                               catalog_sha="a"*64)
        self.assertEqual(doc["status"],"PARTIAL")
        self.assertEqual(loc.verified_names(doc,"12.1.5.70575",
                                           {268249,268250},"a"*64),
                         {268249:"테스트용 가상 응답"})
        doc["items"][0]["item_id"]=268250
        with self.assertRaises(loc.LocaleBlocked):
            loc.verified_names(doc,"12.1.5.70575",{268249,268250},"a"*64)
        doc["items"][0]["item_id"]=268249
        with self.assertRaises(loc.LocaleBlocked):
            loc.verified_names(doc,"12.1.5.70575",{268249,268250},"b"*64)

    def test_official_installed_77_names_bound_to_exact_source(self):
        build,ids=loc.selected_ids()
        names=loc.installed_names(build,set(ids))
        self.assertEqual(len(ids),77)
        self.assertEqual(len(names),77)
        self.assertEqual(names[158367],"메레크타의 송곳니")
        from runner import v167_product_season_gear_adapter as adapter
        public=adapter.public_options(adapter.read())
        self.assertEqual(public["verified_ko_item_names"],77)
        self.assertTrue(all("name_ko" in item
            for role in ("trinket","special_effect_gear_candidate")
            for item in public["choices"][role]))

    def test_missing_or_unverified_file_never_blocks_original_choices(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/"ko.json"
            self.assertEqual(loc.installed_names("build",{1},p),{})
            p.write_text('{"schema":"incorrect"}',encoding="utf8")
            self.assertEqual(loc.installed_names("build",{1},p),{})

if __name__=="__main__":unittest.main()
