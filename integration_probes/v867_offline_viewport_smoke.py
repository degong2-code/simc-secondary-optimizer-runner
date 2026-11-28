"""Optional real Chromium layout probe; local in-process read-only API, no network/Native.
Run against an extracted ZIP or checkout: --root PATH --chromium PATH.
Requires test dependencies and Playwright (not a product runtime dependency).
"""
import argparse,json,pathlib,sys,tempfile,uuid

WIDTHS=(1440,1280,1024,970,768,540,390)


def run(root,chromium):
    sys.path.insert(0,str(root/'runner'))
    from fastapi.testclient import TestClient
    from playwright.sync_api import sync_playwright
    import v113_local_web_api as api
    assets=root/'runner/webui'
    css=(assets/'styles.css').read_text(encoding='utf8')
    html=(assets/'index.html').read_text(encoding='utf8').replace(
        '<link rel="stylesheet" href="/assets/styles.css">','<style>'+css+'</style>').replace(
        '<script src="/assets/app.js" defer></script>','')
    js=(assets/'app.js').read_text(encoding='utf8')
    calls=[];errors=[];blocked=[];rows=[]
    with tempfile.TemporaryDirectory(prefix='ss-view-') as tmp:
        p=pathlib.Path(tmp)
        credentials=api.local_source_keys.WindowsSourceCredentialStore(
            target=api.local_source_keys.TARGET+'.viewport-'+uuid.uuid4().hex)
        app=api.create_app(root=p/'runs',update_root=p/'simc',batch_root=p/'batch',
                           token='offline-render',source_credential_store=credentials)
        with TestClient(app,base_url='http://127.0.0.1:8765') as client, sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=chromium,args=['--no-sandbox','--disable-dev-shm-usage'])
            try:
                page=browser.new_page(viewport={'width':1440,'height':1000})
                page.on('pageerror',lambda exc:errors.append(str(exc)))
                def abort(route):
                    blocked.append(route.request.url);route.abort()
                page.route('**/*',abort)
                def fixture_fetch(path,method,headers):
                    calls.append((method,path))
                    if method!='GET' or not path.startswith('/api/v1/'):
                        return {'status':403,'body':{'detail':{'code':'OFFLINE_RENDER_READ_ONLY'}}}
                    res=client.get(path,headers=headers)
                    return {'status':res.status_code,'body':res.json()}
                page.expose_function('offlineFixtureFetch',fixture_fetch)
                page.set_content(html)
                page.evaluate('''()=>{window.fetch=async(path,options={})=>{
                  const x=await window.offlineFixtureFetch(path,options.method||'GET',options.headers||{});
                  return {ok:x.status>=200&&x.status<300,status:x.status,json:async()=>x.body};};}''')
                page.add_script_tag(content=js)
                page.evaluate('initialize()')
                assert '로컬 서버 연결됨' in page.locator('#notice').inner_text()
                # Synthetic long names exercise actual visual card creation only;
                # they never enter the season catalogue, selection or API.
                page.evaluate('''()=>{const grid=document.getElementById('equipment-special-grid');
                  const name='시인성 시험 전용 매우 긴 특수효과 장비 이름 '.repeat(3);
                  grid.replaceChildren(...[true,false].map((selected,i)=>inlineEquipmentCard(
                    {item_id:900000+i,name},{type:'special',selected,disabled:false,onSelect:()=>{}})));}''')
                for width in WIDTHS:
                    page.set_viewport_size({'width':width,'height':1000})
                    facts=page.evaluate('''()=>{
                      const box=id=>document.getElementById(id).getBoundingClientRect();
                      const a=box('input-title'),b=box('conditions-title'),c=box('equipment-title');
                      const proxies=[...document.querySelectorAll('#optimizer-form select.choice-native-select')]
                        .filter(n=>n.getClientRects().length).map(n=>{const r=n.getBoundingClientRect();return [r.width,r.height]});
                      const names=[...document.querySelectorAll('#equipment-special-grid .inline-item-label')];
                      return {viewport:innerWidth,document:document.documentElement.scrollWidth,
                        parallel:Math.abs(a.y-b.y)<2,gearBelow:c.y>Math.max(a.y,b.y),
                        proxyCount:proxies.length,proxyMax:Math.max(0,...proxies.flat()),
                        namesFit:names.length===2&&names.every(n=>n.scrollWidth<=n.clientWidth+1),
                        selected:document.querySelector('#equipment-special-grid [aria-pressed=true] .inline-item-mark').textContent};}''')
                    rows.append(facts)
                    assert facts['document']==width, facts
                    assert facts['parallel']==(width>970) and facts['gearBelow'],facts
                    assert facts['proxyCount']>0 and facts['proxyMax']<=2,facts
                    assert facts['namesFit'] and facts['selected']=='✓',facts
                page.locator('.top-nav [data-view=history]').click()
                assert page.locator('#view-history').is_visible()
                assert '기록 0개' in page.locator('#recent-session-note').inner_text()
                page.locator('.top-nav [data-view=optimizer]').click()
                assert page.locator('#view-optimizer').is_visible()
                assert not errors and not blocked and all(m=='GET' for m,_ in calls),(errors,blocked,calls)
            finally:
                browser.close()
    print(json.dumps({'viewports':rows,'local_read_only_requests':len(calls),
                      'post_requests':0,'external_requests':0,'page_errors':0,
                      'native_calls':0,'evidence':'OFFLINE_RENDER_WITH_IN_PROCESS_API_AND_SYNTHETIC_VISUAL_ROWS'},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[1])
    parser.add_argument('--chromium',required=True)
    args=parser.parse_args()
    run(args.root.resolve(),args.chromium)
