"""Long-run fixed scout-N seal: old sessions never follow a new default."""
import hashlib,json,pathlib,tempfile,unittest
from unittest import mock
from runner import v293_local_longrun_session as p

class FixedScoutSession(unittest.TestCase):
    def test_old_config_keeps_35_when_new_default_changes(self):
        with tempfile.TemporaryDirectory() as d:
            folder=pathlib.Path(d);generated=folder/"generated";generated.mkdir()
            manifest=generated/"manifest.json";manifest.write_text("{}")
            raw={"schema":p.SCHEMA,"native_budget":64,
                 "manifest_sha256":hashlib.sha256(manifest.read_bytes()).hexdigest()}
            p.config_path(folder).write_text(json.dumps(raw))
            with mock.patch.object(p,"DEFAULT_SCOUT_ITERATIONS",56):
                self.assertEqual(p.selected_scout_iterations(p.config(folder)),35)
                self.assertEqual(p.selected_scout_iterations(None),56)
                raw["scout_iterations"]=48
                p.config_path(folder).write_text(json.dumps(raw))
                self.assertEqual(p.selected_scout_iterations(p.config(folder)),48)
                raw["scout_iterations"]=32
                p.config_path(folder).write_text(json.dumps(raw))
                with self.assertRaises(p.LocalLongRunBlocked):p.config(folder)
    def test_rebind_changes_only_scout_identity(self):
        i={"scout_iterations":35,"confirm_iterations":320,
           "binary_sha256":"a"*64,"revision":"abcdefg",
           "source_profile_sha256":"b"*64,"base_B":3107}
        c={"identity":i,"bundle":{}}
        self.assertIs(p.rebind_scout_iterations(c,35),c)
        fresh={"identity":dict(i,scout_iterations=56),"bundle":{}}
        with mock.patch.object(p.durable.adaptive,"prepare",return_value=fresh):
            self.assertEqual(p.rebind_scout_iterations(c,56),fresh)
        drift={"identity":dict(fresh["identity"],base_B=1),"bundle":{}}
        with mock.patch.object(p.durable.adaptive,"prepare",return_value=drift):
            with self.assertRaises(p.LocalLongRunBlocked):
                p.rebind_scout_iterations(c,56)
    def test_new_config_seals_selected_value(self):
        with tempfile.TemporaryDirectory() as d:
            folder=pathlib.Path(d);generated=folder/"generated";generated.mkdir()
            (generated/"manifest.json").write_text("{}")
            with mock.patch.object(p,"DEFAULT_SCOUT_ITERATIONS",56), mock.patch.object(p,"prepare",return_value={}):
                p.establish(folder,64)
            self.assertEqual(p.config(folder)["scout_iterations"],56)
            with mock.patch.object(p,"DEFAULT_SCOUT_ITERATIONS",64):
                self.assertEqual(p.selected_scout_iterations(p.config(folder)),56)
if __name__=="__main__":unittest.main()
