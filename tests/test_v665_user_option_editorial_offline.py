"""v665 user UI: source name, stronger signed ring stats, icons and layout."""
import pathlib,subprocess,shutil,unittest
from html.parser import HTMLParser

ROOT=pathlib.Path(__file__).resolve().parents[1]


class IDs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
    def handle_starttag(self,tag,attrs):
        name=dict(attrs).get("id")
        if name:self.ids.append(name)


class OptionsEditorial(unittest.TestCase):
    def test_v865_embellishment_in_equipment_step_without_id_changes(self):
        html=(ROOT/"runner/webui/index.html").read_text("utf8")
        parser=IDs();parser.feed(html)
        self.assertEqual(len(parser.ids),len(set(parser.ids)))
        self.assertEqual(html.count('id="crafted-rows"'),1)
        self.assertEqual(html.count('id="special-rows"'),1)
        form=html.split('<form id="optimizer-form"',1)[1].split('</form>',1)[0]
        profile=form.split('<section class="panel profile-panel"',1)[1].split('</section>',1)[0]
        gear=form.split('<section class="panel fixed-gear-panel"',1)[1].split('</section>',1)[0]
        self.assertNotIn('id="crafted-rows"',profile)
        self.assertIn('id="crafted-rows"',gear)
        self.assertIn('id="special-rows"',gear)
        self.assertIn('profile-embellishments',gear)
        for left,right in zip(("input-title","equipment-title","special-rows","crafted-rows","conditions-title"),
                              ("equipment-title","special-rows","crafted-rows","conditions-title","start-btn")):
            self.assertLess(form.index('id="'+left+'"'),form.index('id="'+right+'"'))

    def test_source_identifier_and_optional_icon_routes_are_non_authoritative(self):
        js=(ROOT/"runner/webui/app.js").read_text("utf8")
        server=(ROOT/"runner/v113_local_web_api.py").read_text("utf8")
        self.assertIn("function enchantSourceName(row)",js)
        self.assertIn("function sourceSupportedStrongRingEnchants(rows,catalog)",js)
        self.assertIn("const approvedVisible=sourceSupportedStrongRingEnchants(rows,catalog)",js)
        self.assertNotIn("실행 시 실제 반지/SimC 입력 재확인",js)
        self.assertIn("function refreshOfficialEquipmentIcons(gear)",js)
        self.assertIn("official_item_icons.collect_display(ids,credentials,cache)",server)
        self.assertIn("official_ko_env.build_for_verified_gear(",server)
        self.assertIn('"/api/v1/season-item-icons"',server)
        self.assertIn('installed_manifest_sha256: str',server)
        self.assertIn("state.equipmentIconUrls.get(item.item_id)",js)

    def test_v844_names_independent_of_media_and_same_sha_new_gear(self):
        node=shutil.which("node")
        if not node:self.skipTest("Node not available")
        harness=r"""
const fs=require('fs'),assert=require('assert');
const raw=fs.readFileSync(process.argv[1],'utf8');
const a=raw.indexOf('async function refreshOfficialEquipmentIcons(gear)');
const b=raw.indexOf('async function refreshExistingSeasonTrinkets(',a);
assert(a>=0&&b>a);
const gear={source_scope:"VERIFIED_INSTALLED_V212_SOURCE_V213_CANDIDATES",
 season_build:"12.1.5.70961",installed_manifest_sha256:"a".repeat(64),
 choices:{trinket:[{item_id:1,name:"One"}],special_effect_gear_candidate:[]}};
const state={seasonGear:gear,equipmentIconUrls:new Map(),
 equipmentIconEpoch:0,equipmentIconScope:""};
const first={value:"1",options:[{value:"1",textContent:"One"}]};
const second={value:"",options:[{value:"1",textContent:"One"}]};
const special={querySelectorAll:()=>[]};
const $=id=>({trinket1:first,trinket2:second,"special-rows":special})[id];
let level="334",calls=0,draws=0,respond;
const field=id=>level;
const api=async path=>{calls++;return respond(path)};
const drawInlineEquipment=()=>{draws++};
const refresh=Function("state","$","field","api","drawInlineEquipment",
 "URLSearchParams",raw.slice(a,b)+"return refreshOfficialEquipmentIcons;")(
 state,$,field,api,drawInlineEquipment,URLSearchParams);
const reply=(status,icons,names_ko)=>({
 schema:"v665_official_blizzard_item_media_icons_v1",status,icons,names_ko});
const url="https://render.worldofwarcraft.com/us/icons/56/item.jpg";
(async()=>{
 respond=()=>reply("MEDIA_PROVIDER_UNAVAILABLE",{},{"1":"공식 이름","9":"불가"});
 await refresh(gear);
 assert.equal(gear.choices.trinket[0].name_ko,"공식 이름");
 assert.equal(first.options[0].textContent,"공식 이름");
 assert.equal(first.value,"1");
 assert.equal(state.equipmentIconUrls.size,0);
 assert.equal(calls,1);
 respond=()=>reply("COMPLETE",{"1":url},{"1":"공식 이름"});
 await refresh(gear);
 assert.equal(calls,2);
 await refresh(gear);
 assert.equal(calls,2,"complete same scope no request");
 gear.choices.trinket.push({item_id:2,name:"Two"});
 first.options.push({value:"2",textContent:"Two"});
 respond=()=>reply("COMPLETE",{"1":url,"2":url,"9":url},
  {"1":"공식 이름","2":"새 공식 이름"});
 await refresh(gear);
 assert.equal(calls,3,"same SHA new visible IDs refresh");
 assert.equal(first.options[1].textContent,"새 공식 이름");
 assert.deepEqual([...state.equipmentIconUrls.keys()],[1,2]);
 assert.equal(first.value,"1");
 gear.choices.trinket.push({item_id:3,name:"Three"});
 respond=()=>{level="335";return reply("COMPLETE",{"3":url},{"3":"오래된 응답"})};
 await refresh(gear);
 assert.equal(gear.choices.trinket[2].name_ko,undefined);
 assert.equal(state.equipmentIconUrls.has(3),false);
 assert.equal(draws,3);
 console.log("V844_MEDIA_AND_NAME_SCOPE_PASS");
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
"""
        proc=subprocess.run([node,"-e",harness,str(ROOT/"runner/webui/app.js")],
            cwd=ROOT,text=True,capture_output=True,timeout=20)
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertIn("V844_MEDIA_AND_NAME_SCOPE_PASS",proc.stdout)

    def test_actual_node_enchant_comparison_is_exact_and_effect_safe(self):
        node=shutil.which("node")
        if not node:self.skipTest("Node not available")
        harness=r"""
const fs=require('fs'),assert=require('assert');
const raw=fs.readFileSync(process.argv[1],'utf8');
const a=raw.indexOf('function enchantSourceName(row){');
const b=raw.indexOf('function renderSeasonOptionCatalog(catalog) {',a);
assert(a>=0&&b>a);
const f=Function(raw.slice(a,b)+'\nreturn {enchantSourceName,enchantVisibleLabel,sourceSupportedStrongRingEnchants};')();
const make=(id,token,stat,n)=>({
  enchant_id:id,simc_token:token,slot:'finger1/finger2',
  verified_fixed_E:{
    crit_rating:stat==='crit_rating'?n:0,haste_rating:stat==='haste_rating'?n:0,
    mastery_rating:stat==='mastery_rating'?n:0,
    versatility_rating:stat==='versatility_rating'?n:0}
});
const weak=make(7965,'enchant_ring__amani_mastery','mastery_rating',24);
const strong=make(7969,'enchant_ring__zuljins_mastery','mastery_rating',29);
const distinct=make(7967,'enchant_ring__eyes_of_the_eagle','',0);
const candidate=(row,effect_family,kind)=>({
  enchant_id:row.enchant_id,token:row.simc_token,effect_family,
  preferred_if_same_effect_source:kind,
  effect_description:kind==='DISTINCT_EFFECT_NO_DOMINANCE'?'치명타 효과 증가':'특화 증가'
});
const source={enchant_candidates:{items:[
  candidate(weak,'mastery_rating','WEAKER_VARIANT_REPORTED'),
  candidate(strong,'mastery_rating','STRONGER_VARIANT_REPORTED'),
  candidate(distinct,'crit_effectiveness','DISTINCT_EFFECT_NO_DOMINANCE')
]}};
assert.deepEqual(f.sourceSupportedStrongRingEnchants([weak,strong,distinct],source)
  .map(x=>x.enchant_id),[7969,7967]);
assert(f.enchantVisibleLabel(strong).includes('Zuljins Mastery'));
assert(f.enchantVisibleLabel(strong).includes('특화 +29'));
assert(!f.enchantVisibleLabel(strong).includes('실행 시'));
assert.deepEqual(f.sourceSupportedStrongRingEnchants([weak,distinct],source)
  .map(x=>x.enchant_id),[7965,7967]); // missing strong may NOT hide weaker
assert.deepEqual(f.sourceSupportedStrongRingEnchants([weak,strong],
  {enchant_candidates:{items:[]}}).map(x=>x.enchant_id),[7965,7969]);
const differentSlot={...strong,slot:'head'};
assert.deepEqual(f.sourceSupportedStrongRingEnchants([weak,differentSlot],source)
  .map(x=>x.enchant_id),[7965,7969]);
"""
        proc=subprocess.run([node,"-e",harness,str(ROOT/"runner/webui/app.js")],
            cwd=ROOT,text=True,capture_output=True,timeout=20)
        self.assertEqual(proc.returncode,0,proc.stderr)


if __name__=="__main__":unittest.main()
