"""v336 official bilingual playable-term source-only provenance tests."""
from __future__ import annotations
import copy
import json
import os
import pathlib
import tempfile
import unittest
from unittest import mock

from runner import v336_environment_ko_playable_terms as terms


BUILD="12.1.5.70783"

def fixture():
    roster=terms.roster()
    class_id={name:i+1 for i,name in enumerate(roster["class"])}
    spec_id={key:i+60 for i,key in enumerate(roster["spec"])}
    race_id={name:i+150 for i,name in enumerate(roster["race"])}
    source={}
    def row(i,name):
        return {"id":i,"name":name,
                "key":{"href":"https://kr.api.blizzard.com/dummy/"+str(i)}}
    names={
        "class":[(id,key.replace("_"," ").title())
                 for key,id in class_id.items()],
        "spec":[(id,key.split("/")[1].replace("_"," ").title())
                 for key,id in spec_id.items()],
        "race":[(id,key.replace("_"," ").title())
                 for key,id in race_id.items()]
    }
    for kind in terms.KINDS:
        prop=terms.KINDS[kind][1]
        source[kind,"en_US"]={prop:[row(i,n) for i,n in names[kind]]}
        source[kind,"ko_KR"]={prop:[row(i,"공식 가상 "+n) for i,n in names[kind]]}
    # Multiple Blizzard entries for the same displayed race are allowed
    # only when the official localized name agrees exactly.
    extra=row(999,"Pandaren")
    source["race","en_US"]["races"].append(extra)
    source["race","ko_KR"]["races"].append(row(999,"공식 가상 Pandaren"))
    details={i:{"id":i,"playable_class":{"id":class_id[key.split("/")[0]]}}
             for key,i in spec_id.items()}
    return source,details,class_id,spec_id,race_id

def request_fixture(source,details,calls):
    def fetch(url,*,headers):
        calls.append(url)
        assert headers["Authorization"]=="Bearer UNIT_ONLY"
        kind=next(k for k,(part,_) in terms.KINDS.items()
                  if "/"+part+"/" in url)
        locale=url.split("locale=")[1]
        if "/index?" in url:
            return copy.deepcopy(source[kind,locale])
        ident=int(url.split("?")[0].split("/")[-1])
        return copy.deepcopy(details[ident])
    return fetch


class OfficialPlayableTerms(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.data,self.details,self.classes,self.specs,self.races=fixture()

    def test_whole_dps_roster_and_disambiguated_frost(self):
        row=terms.compile_terms(BUILD,self.data,self.details)
        terms.validate(row,BUILD)
        self.assertEqual(row["status"],"COMPLETE")
        self.assertEqual(list(map(len,(row["names"][k] for k in terms.KINDS))),
                         [13,26,25])
        self.assertNotEqual(row["names"]["spec"]["mage/frost"]["id"],
                            row["names"]["spec"]["deathknight/frost"]["id"])
        self.assertEqual(row["names"]["race"]["pandaren"]["ids"],
                         sorted([self.races["pandaren"],999]))
        self.assertEqual(row["names"]["spec"]["evoker/devastation"]
                         ["class_id"],self.classes["evoker"])
        self.assertNotIn("dracthyr_visage",row["names"]["race"])
        self.assertEqual(row["new_native_calls"],0)

    def test_same_name_different_class_is_not_admitted(self):
        details=copy.deepcopy(self.details)
        dk=self.specs["deathknight/frost"]
        details[dk]["playable_class"]["id"]=self.classes["mage"]
        row=terms.compile_terms(BUILD,self.data,details)
        self.assertIn("deathknight/frost",row["missing"]["spec"])
        self.assertIn("mage/frost",row["missing"]["spec"])
        self.assertNotIn("mage/frost",row["names"]["spec"])
        self.assertEqual(row["status"],"PARTIAL_VERIFIED_NAMES")

    def test_index_locale_id_drift_and_untranslated_english_fail_closed(self):
        changed=copy.deepcopy(self.data)
        changed["class","ko_KR"]["classes"].pop()
        with self.assertRaises(terms.TermBlocked):
            terms.compile_terms(BUILD,changed,self.details)
        changed=copy.deepcopy(self.data)
        changed["class","ko_KR"]["classes"][0]["name"]="Death Knight"
        partial=terms.compile_terms(BUILD,changed,self.details)
        self.assertIn("deathknight",partial["missing"]["class"])
        self.assertNotIn("deathknight/frost",partial["names"]["spec"])

    def test_only_source_enko_index_ids_create_user_display_names(self):
        calls=[]
        fetch=request_fixture(self.data,self.details,calls)
        first=terms.build_for_environment(self.root,BUILD,token="UNIT_ONLY",
                                          request_json=fetch)
        self.assertEqual(first["status"],"COMPLETE")
        self.assertEqual(first["native_calls_now"],0)
        self.assertEqual(first["network_calls_now"],6+26)
        self.assertEqual(len(calls),32)
        public=terms.public(self.root,BUILD)
        self.assertEqual(public["verified_count"],64)
        self.assertEqual(public["names"]["class"]["paladin"],
                         "공식 가상 Paladin")
        self.assertEqual(public["names"]["spec"]["mage/frost"],
                         "공식 가상 Frost")
        self.assertNotIn("id",public["names"]["spec"]["mage/frost"])
        self.assertEqual(public["native_calls_now"],0)
        again=terms.build_for_environment(self.root,BUILD,token="UNIT_ONLY",
                                          request_json=fetch)
        self.assertTrue(again["reused_same_build_cache"])
        self.assertEqual(again["network_calls_now"],0)
        self.assertEqual(len(calls),32)
        self.assertEqual(terms.public(self.root,"12.1.5.70784")["status"],
                         "NO_VERIFIED_OFFICIAL_TERMS")

    def test_corrupted_cache_and_changed_roster_not_exposed(self):
        terms.build_for_environment(self.root,BUILD,token="UNIT_ONLY",
            request_json=request_fixture(self.data,self.details,[]))
        path=terms.path_for(self.root,BUILD)
        doc=json.loads(path.read_text("utf8"))
        doc["names"]["spec"]["mage/frost"]["name_ko"]="부정확한 변경"
        path.write_text(json.dumps(doc),encoding="utf8")
        self.assertIsNone(terms.read(self.root,BUILD))
        self.assertEqual(terms.public(self.root,BUILD)["names"]["spec"],{})

    def test_missing_credentials_avoid_all_network_and_do_not_block(self):
        with mock.patch.dict(os.environ,{"BLIZZARD_ACCESS_TOKEN":"",
                                       "BLIZZARD_CLIENT_ID":"",
                                       "BLIZZARD_CLIENT_SECRET":""}):
            with mock.patch.object(terms.blizzard,"request_json") as get:
                doc=terms.build_for_environment(self.root,BUILD)
        self.assertEqual(doc["status"],"CREDENTIALS_UNAVAILABLE_TERMS_PENDING")
        self.assertEqual(doc["network_calls_now"],0)
        self.assertEqual(doc["native_calls_now"],0)
        get.assert_not_called()

    def test_namespace_endpoints_and_api_id_request_scope(self):
        self.assertEqual(terms.url_for("class","ko_KR"),
            "https://kr.api.blizzard.com/data/wow/playable-class/index"
            "?namespace=static-kr&locale=ko_KR")
        self.assertEqual(terms.url_for("spec","en_US",64),
            "https://kr.api.blizzard.com/data/wow/playable-specialization/64"
            "?namespace=static-kr&locale=en_US")
        with self.assertRaises(terms.TermBlocked):
            terms.url_for("race","ko_KR",12)
        with self.assertRaises(terms.TermBlocked):
            terms.path_for(self.root,"../../bad")

if __name__=="__main__":
    unittest.main()
