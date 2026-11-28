"""v665 display-only Blizzard item icon metadata: allowlist, bounds, no Native."""
import pathlib,sys,unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v665_official_item_icons as icons


class ItemIcons(unittest.TestCase):
    def setUp(self):
        self.cred={"BLIZZARD_CLIENT_ID":"id","BLIZZARD_CLIENT_SECRET":"secret"}
        self.calls=[]
        self.url="https://render.worldofwarcraft.com/us/icons/56/inv_misc_bag_11.jpg"

    def fake_media(self,url,headers=None):
        self.calls.append((url,headers))
        iid=int(url.split("/item/")[1].split("?")[0])
        return {"id":iid,"assets":[{"key":"icon","value":self.url}]}

    def test_exact_media_id_and_https_cdn_only(self):
        self.assertEqual(icons.media_url(270175),
          "https://kr.api.blizzard.com/data/wow/media/item/270175?namespace=static-kr")
        self.assertEqual(icons.verified_icon_url(270175,self.fake_media(
          icons.media_url(270175))),self.url)
        for bad in (
          {"id":270173,"assets":[{"key":"icon","value":self.url}]},
          {"id":270175,"assets":[{"key":"icon","value":"http://render.worldofwarcraft.com/us/icons/56/bad.jpg"}]},
          {"id":270175,"assets":[{"key":"icon","value":"https://evil.example/us/icons/56/bad.jpg"}]},
          {"id":270175,"assets":[{"key":"icon","value":"https://render.worldofwarcraft.com/us/icons/56/bad.exe"}]},
          {"id":270175,"assets":[{"key":"icon","value":"https://render.worldofwarcraft.com/us/icons/56/bad.jpg?secret=1"}]},
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(icons.IconBlocked):
                    icons.verified_icon_url(270175,bad)

    def test_batch_dedup_and_success_does_not_export_secrets(self):
        doc=icons.collect([270175,270173,270175],self.cred,
            token_loader=lambda a,b:"temporary-oauth",
            reader=self.fake_media)
        self.assertEqual(doc["status"],"COMPLETE")
        self.assertEqual(set(doc["icons"]),{"270175","270173"})
        self.assertEqual(doc["network_calls_now"],3)
        self.assertEqual(doc["native_calls"],0)
        self.assertNotIn("temporary-oauth",str(doc))
        self.assertNotIn("secret",str(doc))
        self.assertEqual(len(self.calls),2)
        self.assertTrue(all(row[1]=={"Authorization":"Bearer temporary-oauth"}
                            for row in self.calls))

    def test_absent_credentials_or_provider_failure_never_blocks_gameplay(self):
        no=icons.collect([270175],{})
        self.assertEqual(no["status"],"CREDENTIALS_NOT_CONFIGURED")
        self.assertEqual(no["network_calls_now"],0)
        failed=icons.collect([270175],self.cred,token_loader=lambda a,b:
            (_ for _ in ()).throw(ValueError("network failure")))
        self.assertEqual(failed["status"],"MEDIA_PROVIDER_UNAVAILABLE")
        partial=icons.collect([270175],self.cred,
            token_loader=lambda a,b:"token",
            reader=lambda *args,**kw:{"id":1,"assets":[]})
        self.assertEqual(partial["status"],"PARTIAL")
        self.assertEqual(partial["icons"],{})

    def test_display_over_eighty_reuses_successes_and_retries_only_missing(self):
        cache={}
        ids=list(range(1,84))
        missing={83}
        def media(url,headers=None):
            iid=int(url.split("/item/")[1].split("?")[0])
            self.calls.append(iid)
            return {"id":iid,"assets":[] if iid in missing else
                    [{"key":"icon","value":self.url}]}
        auth=[]
        def token(a,b):
            auth.append(True)
            return "temporary"
        first=icons.collect_display(ids,self.cred,cache,token_loader=token,reader=media)
        self.assertEqual(first["status"],"PARTIAL")
        self.assertEqual(first["pending"],1)
        self.assertEqual(first["network_calls_now"],84)
        self.assertEqual(len(cache),82)
        missing.clear()
        self.calls.clear()
        second=icons.collect_display(ids+[84],self.cred,cache,
            token_loader=token,reader=media)
        self.assertEqual(second["status"],"COMPLETE")
        self.assertEqual(sorted(self.calls),[83,84])
        self.assertEqual(second["network_calls_now"],3)
        third=icons.collect_display([1,84],{},cache)
        self.assertEqual(third["status"],"COMPLETE")
        self.assertEqual(third["network_calls_now"],0)
        self.assertEqual(set(third["icons"]),{"1","84"})
        self.assertEqual(len(auth),2)

    def test_display_missing_fetch_is_bounded_not_all_or_nothing(self):
        cache={}
        first=icons.collect_display(list(range(1,201)),self.cred,cache,
            token_loader=lambda a,b:"token",reader=self.fake_media)
        self.assertEqual(first["status"],"PARTIAL")
        self.assertEqual(first["pending"],40)
        self.assertEqual(first["network_calls_now"],161)
        self.assertEqual(len(cache),160)

    def test_unbounded_or_incorrect_id_rejected_before_api(self):
        for bad in ([],[0],[-1],["270175"],list(range(1,82))):
            with self.subTest(bad=str(bad)[:30]):
                with self.assertRaises(icons.IconBlocked):
                    icons.collect(bad,self.cred,token_loader=lambda a,b:"t",
                                  reader=self.fake_media)
        self.assertEqual(self.calls,[])


if __name__=="__main__":unittest.main()
