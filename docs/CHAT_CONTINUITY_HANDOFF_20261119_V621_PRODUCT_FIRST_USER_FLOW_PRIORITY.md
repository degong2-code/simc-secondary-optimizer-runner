# SIMC SECONDARY OPTIMIZER — v621 최신 제품 우선 독립 복원 / 새 일반 채팅 인계

**2026-11-19 KST · GitHub 실코드·CURRENT·Actions·Native 기반 · 이전 v606 인계를 대체하는 최신 스냅샷.**

> **새 채팅의 첫 응답은 READ-ONLY 복원과 7개 항목의 보고만 하고 STOP.** 사용자의 별도 **“진행”** 명령 이전에는 GitHub 코드·문서 변경, 신규 Actions/Native/HTTP/DB2, 원본 재수집, 공식 승격을 하지 않는다.
>
> 이것은 프로젝트 재시작이 아니다. **이미 성공한 ZERO-SOURCE 시즌 엔진·영구 마부 자동 등록·대표 프로필·적응형 SimC·UI 취소/재개를 보존하면서 AI 없는 일반 사용자 프로그램의 마지막 미완료 경로만 최소 비용으로 완성**하는 것이 목적이다.

## 1. 최신 실제 정본과 검증 순서

- Repo: `degong2-code/simc-secondary-optimizer-runner`
- 사용자 허용 격리 브랜치: `probe/chat-cache-v035-20261024`
- **이 인계 문서 생성 직전 실제 HEAD**: `54a0ebf66504871e6143641d4f2e2fca59e25ee7` — `docs(current): actual v621 Chrome signed E0 choice Start Cancel HTTP restart same-session Resume four Native PASS`. **이 SHA 역시 역사 스냅샷이다. 새 채팅에서는 반드시 새 HEAD를 직접 조회한다.**
- 최근 실제 제품 실증 기능: **v621**. 종전 `docs/CHAT_CONTINUITY_HANDOFF_20261118_V606_PRODUCT_FIRST_POLICY_A_LAST_MILE.md`와 v596~v606의 당시 NEXT는 역사 자료다. **v606 `product_input` 증거 누락을 현재 새로 연구하지 않는다.** v607~v621에서 실제 진전이 있었다.
- **먼저 열 파일**: 이 문서 → `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md`(최신 항목을 우선) → `docs/development/notes/2026-11-19_p1-v621_actual_chrome_signed_E0_cancel_resume_native_70961.md` → `docs/development/notes/2026-11-19_p1-v618-v619_real_70961_enchant_auto_admission_user_dps_95.md` → `docs/development/notes/2026-11-19_p1-v620_signed_E0_user_visible_armor_slot_ui_bridge.md`.
- 정책: `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`, `docs/development/POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md`, `docs/development/PRODUCT_DELIVERY_ROADMAP_M0_M7_20261115.md` **2026-11-18 최신 상단 사용자 결정**. 이전 역사적 M0~M7 PENDING보다 최신 수락·구현 상태를 우선한다.
- 코드: 원본 공급/설치 `runner/v216_environment_build_coordinator.py` → `v217/v212`, 자동 등록 `v220/v196`, 웹 `runner/webui/app.js` + `runner/v113_local_web_api.py`, 세션 `v106`, 사용자 프로필 `v098`, 최적화 `v096/v094/v293`. 최근 실제 탐침 `integration_probes/p1_v619_real_70961_user_enchant_dps_once.py`, `integration_probes/p1_v621_real_70961_browser_enchant_cancel_resume_once.py`, 해당 `.github/workflows/p1_v621_real_70961_chrome_enchant_cancel_resume_once.yml`.
- 확인 순서: GitHub 최신 HEAD/코드→CURRENT→해당 Actions 결론 및 artifact/Native 영수증→원본 출처와 정확한 검증 범위. 역사 인계의 HEAD·숫자를 최신 실측값으로 무단 승격하지 않는다.

## 2. 프로젝트 목적 — 어떤 추가 코드보다 우선

**제품은 목표 아이템레벨(현 기본 334) 또는 사용자가 직접 입력한 최종 CHMV T를 기준으로, 미래 장비 파밍의 목표가 될 치명·가속·특화·유연의 `최적 절대 rating`을 실제 SimulationCraft DPS 최대화로 찾는 프로그램이다.**

- 대상은 **26개 DPS 전문화만**. 증강 기원사·탱커·힐러 제외. 기존 역사 `v1.4.1` 일부 문단의 **27 DPS/증강 포함** 표기는 더 최신 사용자 결정에 의해 폐기.
- 사용자는 직업·전문화·종족·특성, 목표 ilvl/최종 T, 장신구 2개, 선택 특수효과 장비, 장식 최대 2개, 검증된 보석·영약·영구 마부·별도 기름/소모품·전투조건을 선택한다. **전체 현재 착용 장비를 입력하지 않으며 현재 장비 CHMV를 기본 예산으로 삼지 않는다.** SimC 프로필 업로드는 캐릭터 정보·특성 불러오기 선택 편의 기능.
- 프로그램이 해당 시즌 **대표 일반 장비·무기·주능력치·티어 4세트·정확한 실행 프로필**을 내부 생성한다. **미래 파밍 목표 rating을 제시**할 뿐 장비 조합/아이템 획득 경로/전체 시즌 장비 DB를 추천·구축하지 않는다.
- **런타임 AI/LLM/외부 AI API·에이전트 0**. 개발 도구로서의 GPT 사용은 허용하지만 배포 프로그램 사용자는 AI 없이 실행한다.
- 최종 사용자 흐름: **시즌 자동 발견 → 해당 시즌 G/J/F/O 전체 검증·설치 → B/T·L/E/O 보호 → 대표 장비/프로필 → 기존 적응형 SimC → 절대 rating·비율·DPS·SEM·95% 판정·관측 1순위·실질적으로 다른 근접 대안 → 캐시/중단/재개/화면 결과**.
- SimC는 장비·마부·장신구·장식·보석·기름의 실제 효과/proc·발동·APL·전투 DPS를 책임진다. **우리 코드는 정확한 출처/ID/ilvl/슬롯/손/옵션·정적 G/J/F/O·L/E/O·후보·JSON2 rating·DPS/SEM/95% 결과·캐시·재개를 책임진다.** 마부 효과를 연구/재구현하거나 발동 여부 독립 인증 Gate 신설 금지.

**공식 회계**: `B=G+J+F`, `T=B+O`, 최종 `c_final=c_base+o`. 수동 최종 T 최우선, `B=T-O`. O는 고정·비자유분배·중복 0회, G 안의 정확한 L 재가산 금지, 검증된 스탯별 E를 한 번만 보호. **정적 E=0도 정상 마부**이며 효과가 없다는 뜻이 아니다. 미측정 E를 0으로 추정 금지. 현재 시즌 실제 출처의 G/J/F/O를 과거 다른 빌드 값으로 대체 금지. 결과 통계는 **95%만** 사용하고 관측 최고·95% 확정·전역 최적 입증을 구분한다.

## 3. 최근 실제 PASS — 다시 만들거나 전수 재검증하지 않는다

**기존 역사적 제품 사용 실증**
- `v567`: 현재 시즌 ZERO-SOURCE G/J/F/O→사용자 SimC 실환경 PASS [#44046442654](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44046442654). 범용 시즌 자동 발견 기능은 이미 사용자 수락 범위에서 PASS. 미래 미출시 시즌 데이터를 지금 검증해야 한다는 새 Gate 금지.
- `v570`: Windows Chrome → 시즌 자동 Build → 선택 → **64 DPS Native** → 결과 PASS [#44074372451](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44074372451).
- `v572`: Windows ZIP 취소/재시작/재개 PASS [#44082378854](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44082378854).
- `v530/v532/v533/v534`: 정확한 과거 조건의 E0·E+30·E+26·수동 T 우선권 Native PASS. `v578~v581`: 기름 O32·수동 T3500·Native·캐시·재개 PASS. **해당 빌드/아이템/조건 범위 증거만 재사용**, 일반 E>0/모든 전문화 전체 PASS로 확대 해석 금지.
- `v290+v291+v293/v094`: 기존 적응형 탐색/95%·결과·캐시·취소·재개 경로. 새 알고리즘/SEM 엔진 작성 금지.

**2026-11-19 현재 빌드 70961의 새 실제 성과**
- `v610` [#44425195290](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44425195290): 실제 live `12.1.5.70961` vs 기존 `70783` SimC 불일치로 정합 차단(올바른 fail-closed). 새 원본 SimC commit **`9933ffb946fb55b1fa66657b848f519ac19006e1`** 확보·빌드.
- `v611` [#44425813732](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44425813732): 70961 신규 원본으로 **G=2850/J=92/F=165/O=0/B=T=3107**, 기본 환경 설치 PASS, 환경 Native6회. **숫자 동일성은 과거 빌드 복사 증거가 아니라 이 실행의 실측**. 해당 수치만 현재 70961/ilvl334 조건에 속함.
- `v613` [#44428472283](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44428472283): `v163` 외부 `source_scope.expansion_id`를 `v583`에 잘못 전달하던 내부/외부 키 불일치 수정, 실제 최고 품질 **38/38 계열**, 물리 아이템/마부 ID **76/76** source-only PASS.
- `v616→v617` [#44431796139](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44431796139): v607이 관련 없는 SimC 영구마부 1062 원본 행의 중복 ID까지 오류 처리하던 범위 수정. 정확 DPS 장비 마부만 판정, `product_input=38/38`, `chmv_budget=30/38`, Native0.
- `v618` [#44438148520](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44438148520) **SUCCESS**: 실제 최고품질/부위/정적 E·서명 영수증이 모두 충족된 영구 마부 **19건 `v212` 자동 등록**(가슴/머리/어깨/발, 정적 E=0). 나머지 **19건만 선택적으로 보류**(정확한 물리 슬롯/손 관계 19, 일부 E 미확정 8); 기본 환경은 정상 사용 가능. 38 source 품질 증거와 19 실제 UI 승인 수를 혼동 금지.
- `v619` [#44440673155](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44440673155) **SUCCESS**: 징벌 성기사 ilvl334, 실제 대표 가슴 ItemID **268222**에 승인 `enchant_id=7957` 정확히 1회, B=T3107/E0, 원래 `v098/v096/v094`의 실제 **DPS Native 6회**. 관측 최고 **DPS 158565.166·SEM 246.502**, CHMV **736/736/735/900**; 근접 대안 **DPS 157790.260·SEM 236.043**, 두 후보 간 95% 방향 지지. **전역 최적해 증명 아님**.
- `v620` [웹 API #44442806896](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44442806896), [UI #44442806922](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44442806922) 각 Windows·Ubuntu **SUCCESS**: 검증된 E0를 웹 머리·어깨·가슴·발 개별 선택칸에 연결, 기존 한 부위 선택/정확 설치 SHA/부위·최종 ItemID/미검증 항목 차단 유지.
- **최신 `v621`** [실 Windows Chrome #44445250976](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44445250976) **SUCCESS**: 실제 Chrome에서 `chest:7957` 클릭 → 서명된 `v212` 19건/같은 SHA → 실제 Start → 사용자 Cancel Native2회 → HTTP 서버 종료·재시작/페이지 새로고침 → **같은 session ID 및 설치 SHA·선택 복원** → 실제 Resume 추가 Native2회(누적 2→4) → 두 번째 Cancel. 실제 사용자 DPS Native **4회**, 시즌 환경 Native **6회**, 소스 바운드 Windows CLI **캐시 HIT/새 컴파일 0회**. 64개 전체 후보 계산 완료나 최종 95% 결과를 이번 v621에서 새로 관측한 것은 아니다. **v619의 실제 DPS/SEM/95% 증거와 v621의 실제 웹 취소/재개 증거는 각각 다른 정확한 증명이다.**
- v621 첫 시도 [#44444615522](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44444615522)는 실제 E0 웹 클릭/요청까지 PASS 후 **새 테스트가 응답 `ilvl`을 `ilevel`로 잘못 읽고 자동 `final_T`를 필수로 가정하여 KeyError**, 제품 로직 실패 아님. `1e31c41cd7680cd9cc802a2424b1bf0f8b932e2e`에서 시험 스크립트만 수정 후 v621 SUCCESS.
- 현재 HEAD에서 [공통 offline #44445250753](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44445250753) SUCCESS, [78 계약 #44445924964](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44445924964) SUCCESS. 최근 중간 실패는 최종 PASS와 별도 기록한다.

## 4. 가장 중요한 최근 교정·함정

1. **마부 효과/품질의 반복 연구 금지.** 사용자 확정 정책상 정확한 사용 부위·동시즌 최고 품질 물리 ID와 SimC 입력이 검증됐다면 **효과/주문 발동·DPS는 SimC 책임**. 정적 CHMV가 있는 일부 마부만 E를 보석 방식으로 정확 판정한다. **E=0이거나 등급별 `id_spell`이 다르다는 이유만으로 별도 효과 비교/발동 Gate 신설 금지.** 이전 v585의 수치 우열 미확정은 새 정책 이전의 역사적 탐색 배경이다. 다만 정확 출처·품질 계열 관계·부위·E·사용 가능성 자체를 허위 승인하지 않는다.
2. **시즌·소스 값의 표면/내부 스키마 혼동 금지.** v613의 `source_scope` vs `auto_source_scope` 실결함을 재현성 있는 회귀로 보존. 확장팩/시즌 ID 하드코딩 금지.
3. **전체 원본의 다른 시스템을 잘못된 차단 Gate로 만들지 말 것.** v616 수정은 1062개의 비해당 마부 DBC source rows가 76개 실제 DPS 대상의 승인에 영향을 주지 않게 했다. 실제 대상 내부 중복·오류는 여전히 fail-closed.
4. **실제 최종 아이템과 동일 게임 빌드, 실물 손/부위·서명 SHA**가 결정한다. v618/v619/v621에서 제품은 source-only 38, 정적 E 30, 실제 등록 19만 사용. **미확정 E=0 추정·반지/무기손 임의 적용·미승인 UI 승격 금지.**
5. **부위별 웹 선택은 현재 한 개 E0 마부**로 제한된다. 그 제한을 근거 없이 풀지 말고, 검증된 E>0/복수 부위의 회계 합산과 정확 한 번 SimC 프로필 적용이 필요할 때 좁게 확장. 사용자 수동 최종 T를 E 때문에 증가시키지 않는다.
6. **v621 취소/재개를 완료 결과로 과장 금지.** PAUSED_USER_CANCEL의 partial Native4와 v619 별도 DPS6은 서로 다른 session/scopes. 이전 결과가 남아도 현재 재개 결과로 오인하지 않도록 기존 UI의 stale-result 보호 유지. 64후보 전부 실행·26전문화 전수 반복을 새 인수 Gate로 발명하지 않는다.
7. **정확 캐시 정체성**: 동일 시즌 정적 아이템 캐시는 SimC revision 단독 변경으로 폐기 금지. DPS 캐시는 실제 SimC binary SHA/revision·프로필·설정·마부·기름·후보·iterations별 분리. 사용자의 선택 수정이 과거 세션/원본 서명을 덮어쓰지 않도록 보호.
8. **기본 환경을 선택적 미완료 항목으로 막지 않는다.** 영구 마부 미승인 19건·DK 룬벼리기 별도 SimC 원본 경로·옴니움 장서 후속 선택형 모듈은 전체 BASE G/J/F/O 제품 실행 차단 사유가 아니다. 일반 임시 마부는 범위 밖, 무기 기름은 별도 O.
9. **검증 단위 구분**: 합성/오프라인 PASS ≠ 동시즌 source 봉인 PASS ≠ 실제 Native DPS/SEM/95% PASS ≠ 실제 Chrome 사용자 E2E PASS ≠ 전제품 완료. 결과가 현재 실제 빌드·선택 조건에 귀속되는지 명시.
10. **PC 실사용·26전문화 전체**: v621 Windows GitHub Actions Chrome은 실제 UI 시나리오지만 개인 Windows PC 배포/모든 전문화/모든 영구마부·수동 T/기름 조합 제품 완료의 증거가 아니다.

## 5. 현재 우선순위 — 최소 사용자 기능으로 완결

### P1 — 가장 먼저 **이번 사용자 E0 웹 선택의 완료 결과 확인** (한 시나리오)

이미 `v621`에서 실제 Chrome Start/Cancel/서버 재시작/Resume이 작동하고, `v619`에서 같은 선정 마부의 실제 DPS/SEM/95%가 별도 성공했다. **아직 증명하지 않은 경계는 동일 웹 사용자 세션의 자연스러운 종료 → 결과 화면에 절대 rating/비율/DPS/SEM/95%/근접 대안/진행·캐시 정체성 정상 표시 및 재방문 시 정확한 보존**이다. 시작 지점을 **v621 기존 세션/결과 소비자**, 기존 `v113/v293/v094`와 `webui/app.js`에서 확인한다.

- 먼저 **기존 v570 일반 웹 64 Native 결과 완결·v619 서명 E0 DPS 6 Native·v621 실제 Resume Native4와 결과 렌더링 오프라인 증거**를 비교하여 **새 Native 없이 증명 가능한 부분은 재사용**. 실제 남은 단절만 1개 골라 수리.
- 반드시 실행할 필요가 있을 때만 **하나의 실제 서명 E0 세션에서 사전에 정한 bounded Native/시간 예산**으로 최종 결과를 관측. 기존 v621의 64 Native 상한을 '64회 전수 재실행' 명령으로 오해하지 않는다. 조건이 충분하면 **STOP**. 결론 미확정/실행 예산 종료는 정직하게 표시하고 전역 최적해라고 주장하지 않는다.
- 중복 시즌 G/J/F/O/SimC 재컴파일 방지: 동일 빌드 70961의 검증된 실행 파일 캐시·영수증·세션 후보 캐시를 먼저 탐색. 사용 가능 범위 밖의 역사 JSON/다른 SHA를 신뢰한 척 재사용하지 말 것. 취소 후 이어서만 추가 native 실행, 중복/전면 재실행 방지.
- 변경 전 6문항: 이 기능이 사용자 결과의 어느 단계인가 / 지금 못 하는 일 / 첫 원래 생산자→소비자 단절 / 기존 코드·cache·Native로 해결되는가 / 추가 HTTP·DB2·Native·CPU/RAM/I/O 예상·상한 / 정확한 STOP 기준. **STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW**.

### P2 — 일반 사용자 기능의 실제 남은 필수 범위

E>0 영구 마부의 일반 사용 정적 E·수동 T/고정 하한 정합, 복수 부위 영구 마부의 정확 E 합산·중복 방지, 필요 옵션/전투설정 UI에서 실제 유효 사용자 입력→동일 실행 경로 연결. 이미 `v532/v533/v534` 역사 Native 한정 PASS 사례를 재사용하고, **실제 최초 사용자 장애가 나타난 경우**만 하나씩 확장. 마부 효과 연구/기능보다 **정확한 사용자 선택·프로필·DPS 연결**을 우선한다.

### P3 — 최종 사용자 제품 인수·릴리스 정합

성공한 ZERO-SOURCE 시즌 구축과 한 일반 사용자 시나리오의 **UI 입력→안전한 예산/대표 장비/SimC→완료 결과/대안/통계→중단·재개/동일 조건 캐시**를 Windows 실제 제품 범위로 완결. 현재 유효한 `78`요소 관련 적용 증거와 포장/복구·설치 절차를 확인하되, 무의미한 26 DPS/마부 전체 Native 전수·독립 효과 Gate·새 적응형 solver·시즌 장비 DB 개발 금지.

### P4 — 명확히 후순위/범위 밖

DK 룬벼리기 자체 SimC 원본 경로 유지, 확장팩 특수 콘텐츠 옴니움 장서 등은 별도 ON/OFF 선택형 모듈(제품 본 기능 완료 이후), exact Native G는 필요한 정확 예산 조회 보조 경로이며 전체 착용 장비 요청 기능이나 기본 제품 통합 선행 Gate가 아니다.

## 6. 개발 비용·상태/승인 경계

- 최우선 사용자 기능이 이미 완성됐으면 **더 시험하지 않고 STOP**. 특히 70961 소스 Win64 바이너리를 매 시험 새 컴파일하거나 이전 64 Native·새 시즌 전체 Wago/DB2를 반복하지 않는다. *새 출처·새 빌드·선택된 시나리오의 실제 변경 증거만* 추가.
- 보고 형식: **실제 사용자 변화 / 코드 변경 / 새로운 PASS·FAIL·SKIP / 역사 증거 재사용 / 신규 Native·HTTP/DB2·RAM/CPU/I/O·cache 영향 / 남은 범위 / 다음 하나**. GitHub 액션 실패도 숨기지 않되 단순 probe KeyError는 SimC 제품 실패가 아님을 분리.
- **공식 현재 상태** `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10`. 15/78은 전체 구현률(%)이 아니며 B10은 공식 검토 순서이지 제품 P1 개발 금지명령이 아님. 실환경 한 옵션 PASS만으로 공식 상태 임의 변경 금지.
- 격리 브랜치 개발만 허용. 별도 사용자 승인 없이 **main 병합, v003 immutable, 원본 v016 직접 통합 완료 주장, 실제 Project Sources/Instructions UI 적용 완료 주장, Work OS M0·Shared State 공식 승격, WEQUIP 영구 authority/runtime 의존성, 기존 주 제품 개발 채팅 소유권 이전** 금지. GitHub 문서 커밋은 Project UI 반영이 아니다.

## 7. 새 채팅의 첫 응답 — 일곱 항목만, READ-ONLY 후 STOP

현 최신 HEAD·CURRENT·실제 v621 코드/Actions/Native·위 최신 사용자 정책을 확인하고 **짧지만 구체적으로** 다음을 보고:

1. **실제 최신 HEAD / 최근 Actions SUCCESS·FAILURE·CANCELLED·SKIP, 수정 전후 구분**
2. **미래 목표 CHMV 절대 rating·26 DPS·런타임 AI 0·SimC/우리 책임 경계**
3. **ZERO-SOURCE·Windows 일반 E2E 및 현재 70961 G/J/F/O, v618 원래 19 마부 자동 등록·나머지 정확 보류**
4. **v619 실제 SimC DPS/SEM/95%·관측 최고·대안, v620 웹 선택, v621 실제 Chrome Start/Cancel/서버 재시작/Resume 증거(부분 Native4)**
5. **일반 사용자 실완료까지 남은 한 경계, E>0/다부위 등 선택적 범위, DK·Omnium 후순위**
6. **비용 대비 다음 작업 하나와 기존 캐시/Native 코드 재사용·불필요 전수 STOP**
7. **미확인 증거/15/78·full_product_e2e·B10 및 GitHub main/Project UI/Work OS·개발 소유권 경계**

**첫 응답은 소스 코드/문서/GitHub/Actions/Native/HTTP/DB2를 바꾸지 않는다. 일곱 항목 보고 후 STOP. 사용자가 별도로 “진행”이라고 명령하면 그때 새 HEAD와 첫 실제 사용자 장애를 재확인하고, 기존 프로그램 경로에서 최소 변경·최소 검증만 수행한다.**

**핵심: 이 프로그램은 마부나 SimC 주문 효과 연구용 도구가 아니다. AI 없는 일반 사용자가 미래 목표 CHMV 절대 rating과 실제 SimC DPS·SEM·95%·근접 대안을 구해 파밍 목표를 정할 수 있게 만드는 프로그램이다. 이미 성공한 기능을 다시 만들지 않는다.**
