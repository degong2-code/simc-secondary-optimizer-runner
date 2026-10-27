"""v130: strict source identity/APL/talents common guard; offline Native 0."""
from __future__ import annotations
import dataclasses,hashlib,pathlib,sys,tempfile,unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v101_common_representative_equipment as common
import v127_dps_source_metadata as metadata
import v129_common_source_fields as fields
import v130_source_identity_contract as guard

def old_source_validation(source,key,expected_blob,markers,*,min_actions,
                          strict_greater=False,hash_error,identity_error,
                          apl_error,talents_error=None,fail=None):
    """Independent pre-v130 original family checks, no new registry helper."""
    def require(ok,error):
        if not ok:raise ValueError(error)
    must=fail or require
    data=source.encode("utf8")
    source_blob=hashlib.sha1(
        b"blob "+str(len(data)).encode("ascii")+b"\0"+data
    ).hexdigest()
    must(source_blob==expected_blob,hash_error)
    must(all(marker in source for marker in markers),identity_error)
    actions=[s for s in source.splitlines() if s.startswith("actions")]
    actions_valid=(len(actions)>min_actions if strict_greater
                   else len(actions)>=min_actions)
    must(actions_valid and sum(s.startswith("actions=")
                               for s in actions)==1,apl_error)
    talents=[s.partition("=")[2] for s in source.splitlines()
             if s.startswith("talents=")]
    if talents_error is not None:
        must(len(talents)==1,talents_error)
    return actions,talents

class CommonSourceIdentity(unittest.TestCase):
    @staticmethod
    def fail(ok,error):
        if not ok:raise ValueError(error)

    def test_six_real_factories_full_output_equal_prior_identity_checks(self):
        for record in metadata.SOURCE_BACKED:
            with self.subTest(spec=record.key),tempfile.TemporaryDirectory() as td:
                folder=pathlib.Path(td)
                with mock.patch.object(guard,"verify",
                                       side_effect=old_source_validation):
                    old=common.source_backed_gear(record.key,folder,334,self.fail)
                new=common.source_backed_gear(record.key,folder,334,self.fail)
                self.assertEqual(new,old)
                self.assertFalse((folder/"simc_results").exists())

    def test_pinned_source_hash_and_token_rules_are_registry_backed(self):
        for record in metadata.SOURCE_BACKED:
            with self.subTest(spec=record.key):
                source=(ROOT/"integration_probes"/"fixtures"/record.source_fixture
                       ).read_text(encoding="utf8")
                self.assertEqual(guard.git_blob(source),record.source_git_blob)
                self.assertIn(''+record.character_class+'="',source)
                self.assertIn("spec="+record.spec,source)
                bad=source+"\n# tampered\n"
                with self.assertRaisesRegex(ValueError,
                         "SOURCE_HASH_REJECTED"):
                    guard.verify(bad,record.key,record.source_git_blob,
                                 ("spec="+record.spec,),min_actions=1,
                                 hash_error="SOURCE_HASH_REJECTED",
                                 identity_error="SOURCE_IDENTITY_REJECTED",
                                 apl_error="SOURCE_APL_REJECTED",
                                 fail=self.fail)

    def test_registry_sha_drift_is_refused_before_source_acceptance(self):
        record=metadata.get(("rogue","subtlety"))
        with self.assertRaisesRegex(guard.SourceIdentityBlocked,
                                   "SOURCE_IDENTITY_REGISTRY_SHA_DRIFT"):
            guard.verify("rogue=x\n",record.key,"0"*40,("rogue=",),
                         min_actions=1,
                         hash_error="SOURCE_HASH_REJECTED",
                         identity_error="SOURCE_IDENTITY_REJECTED",
                         apl_error="SOURCE_APL_REJECTED")

    def test_identity_apl_threshold_and_duplicate_actions_fail_closed(self):
        base=("rogue=\"Test\"\nspec=subtlety\nrole=attack\n"
              "actions=/start\nactions+=/finish\ntalents=CU123\n")
        record=metadata.get(("rogue","subtlety"))
        for case,source,threshold,markers,err in (
            ("role",base.replace("role=attack","role=spell"),2,
             ("rogue=","spec=subtlety","role=attack"),"IDENTITY_REJECTED"),
            ("count",base,3,("rogue=",),"APL_REJECTED"),
            ("duplicate",base.replace("actions+=/finish","actions=/finish"),
             2,("rogue=",),"APL_REJECTED")
        ):
            with self.subTest(case=case):
                blob=guard.git_blob(source)
                changed=dataclasses.replace(record,source_git_blob=blob)
                with mock.patch.dict(metadata.BY_SPEC,{record.key:changed}):
                    with self.assertRaisesRegex(ValueError,err):
                        guard.verify(source,record.key,blob,markers,
                            min_actions=threshold,
                            hash_error="HASH_REJECTED",
                            identity_error="IDENTITY_REJECTED",
                            apl_error="APL_REJECTED",
                            talents_error="TALENTS_REJECTED",fail=self.fail)

    def test_talent_duplicate_optional_only_for_existing_v104_contract(self):
        source=('rogue=\"Test\"\nspec=subtlety\n'
                'actions=/start\nactions+=/finish\n'
                'talents=CU123\ntalents=CU456\n')
        record=metadata.get(("rogue","subtlety"))
        blob=guard.git_blob(source)
        changed=dataclasses.replace(record,source_git_blob=blob)
        args=(source,record.key,blob,("rogue=",))
        kw=dict(min_actions=2,hash_error="HASH_BAD",
                identity_error="IDENTITY_BAD",apl_error="APL_BAD",
                fail=self.fail)
        with mock.patch.dict(metadata.BY_SPEC,{record.key:changed}):
            with self.assertRaisesRegex(ValueError,"TALENTS_BAD"):
                guard.verify(*args,talents_error="TALENTS_BAD",**kw)
            actions,talents=guard.verify(*args,talents_error=None,**kw)
            self.assertEqual(len(actions),2)
            self.assertEqual(talents,["CU123","CU456"])

if __name__=="__main__":
    unittest.main()
