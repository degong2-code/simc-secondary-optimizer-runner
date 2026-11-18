# SIMC SECONDARY OPTIMIZER — v606 최신 제품 우선 독립 복원 및 새 채팅 인계

**2026-11-18 · 일반 채팅 인계 정본.** 과거 대화 요약이 아니라 GitHub 최신 원본과 실제 Actions/Native 영수증으로 제품을 독립 복원하기 위한 자료다. 첫 응답은 READ-ONLY·7항목 보고 후 STOP, 별도 사용자 '진행'을 받아야 개발을 시작한다.

- 저장소: degong2-code/simc-secondary-optimizer-runner
- 격리 브랜치: probe/chat-cache-v035-20261024
- 인계 전 실제 HEAD: 7a7189f14dad8b31ac5dc2ef91f64a4c93781166 (이 문서 커밋 전 역사 스냅샷)
- 최종 제품 기능 코드: **v606** (dab7df72614107a7bb9832a0f5c0376785c6b856), 최종 테스트 교정 ac2b7161c030cff07d6554cf28314c41651ca129.
- 새 채팅은 반드시 새로 HEAD·CURRENT·실제 코드·Actions·Native 영수증을 확인한다. 이 문서 HEAD를 현재 값이라 가정하지 않는다.

## 1. 최종 제품 목적이 모든 판단에서 가장 중요

이 제품은 사용자의 **미래 목표 아이템레벨 또는 수동 최종 CHMV 총량에서 실제 SimC DPS를 최대화하는 치명·가속·특화·유연 절대 rating**을 찾는, **런타임 AI 0** 일반 사용자 프로그램이다. 지원 범위는 **26개 DPS 전문화만**, 증강 기원사·탱커·힐러 제외. 현재 장비 재분배, 장비 조합 추천·획득 경로, 시즌 전체 장비 DB, 독립 APL/효과 연구 엔진이 아니다.

사용자 입력: 전문화·종족·특성·목표 ilvl(현재 시즌 기본 334, 새 시즌은 실제 출처에서 자동 선택) 또는 사용자 최종 T, 장신구 2개, 선택 특수 장비, 장식 최대 2개, 검증된 보석/영약/영구 마부/별도 무기 기름·소모품/전투조건. 현재 전체 장비 입력은 **없음**. SimC 프로필 업로드는 선택적인 캐릭터 정보 입력이며 현재 장비·CHMV를 기본 목표 예산으로 쓰지 않는다. 내부에서 같은 시즌 대표 일반 장비·무기 성능·주능력치·티어 4세트·정확한 SimC 실행 프로필 구성.

핵심 사용자 흐름: **현재 시즌 자동 발견 → G/J/F/O 전체 자동 구축 → B/T와 L/E/O 회계 → 대표 프로필 생성 → 이미 검증한 적응형 SimC 실행 → 절대 rating·비율·DPS·SEM·95% 판정·관측 최고·실질적으로 다른 근접 대안 → 캐시/중단/재개**. 구현률이 아니라 이 실제 사용자 흐름의 미완료와 첫 장애를 우선한다. 영구 마부의 품질 검증은 이 프로그램을 완성하는 데 필요한 입력 정확성이지 프로젝트의 최종 목적이 아니다.

## 2. 공식 수식·SimC 책임·통계

- G: 목표 레벨의 대표 일반 장비/무기 CHMV, J: 검증 보석, F: 검증 영약, O: 선택 기름의 고정 정적 rating. **B=G+J+F, T=B+O**, 사용자 수동 최종 T가 우선하며 **B=T-O**, 최종 **c_final=c_base+o**.
- 실제 특수 장비의 고정 L은 G에 이미 포함, 다시 가산하지 않는다. 영구 마부 E는 검증된 **스탯별 정확한 고정치**로만 한 번 반영하며 수동 T를 증가시키지 않는다. O는 자유분배 대상이 아니며 중복 가산하지 않는다. 장신구 고정치는 자유 G 밖, JSON2 미관측은 0이 아니다. 과거 79×2 참조/B, 보석·영약 수치를 다른 시즌의 검증값으로 복사 금지.
- **우리 프로그램:** 출처·정확 ID/빌드/ilvl/장비 부위·손·옵션, 대표 프로필, 회계·고정하한·중복 방지, SimC 후보 실행/JSON2 rating/SEM/95%·캐시·취소·재개.
- **SimC:** 장비·마부·보석·장식·장신구/기름의 실제 효과, proc·발동, APL, 전투·DPS. **별도의 효과 발동 인증 Gate, 주문 메커니즘 재구현 또는 독립 발동 Native 전수 검사 금지.**
- **E0 정상:** E는 정적 CHMV 증가만 뜻한다. E=0이어도 SimC에 마부 ID를 넣어 효과가 계산된다. 검증 E>0은 정확한 해당 스탯 고정치, E 미확정은 0으로 추정하지 말고 해당 선택지만 보류.
- 결과 통계는 **95%만** 사용. 관측 최고 DPS와 통계적 우위 확정, 전역 최적해 입증을 혼동하지 않는다.

## 3. 실제 성공한 핵심 엔진·Native 재사용 (새로 만들지 않는다)

- **v567 ZERO-SOURCE** 시즌 환경 자동 구축(G/J/F/O 및 USER SimC) 실제 PASS [#44046442654](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44046442654). 당시 70783 현재 시즌의 G2850/J92/F165/O0/B=T3107은 **그 시나리오 한정**, 새 시즌 불변 상수 아님. 미래 시즌이 아직 출시되지 않았다는 이유로 이미 수락한 범용 발견 기능을 다시 PENDING으로 되돌리지 않는다.
- **v570 Windows Chrome** 빈 환경→시즌 Build→장신구 선택→Native SimC DPS **64회**→결과 화면 PASS [#44074372451](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44074372451). 이 경로 Native 64회 반복 금지.
- **v572 Windows ZIP 중단·재시작·재개** 실제 PASS [#44082378854](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44082378854).
- **v530 단일 정확 E0**, **v532/v533 가속 E+30/특화 E+26**, **v534 양수 E + 수동 T**, **v578~v581 O32·수동 T3500·DPS·캐시·재개** Native PASS는 각 빌드·전문화·정확 장비·SimC 바이너리/조건에 한정된다. 26 DPS·모든 마부의 일괄 승인 근거가 아니다.
- 기존 적응형 **v290+v291+v293**와 현재 v093/v094는 DPS/SEM/95%·후보·캐시·취소·재개를 구현. 새 탐색 엔진·SEM 미세 정밀화 엔진·동일 시즌 전수 Native 반복은 요구하지 않는다.

## 4. v596~v606의 실제 변경 — 과거 NEXT 재작업 금지

- **v596:** 설치·승인된 정확 E0 반지를 사용자 실물 ID, 고정 예산, SimC 프로필 enchant_id 1회, 캐시로 연결.
- **v597:** 일반 영구 마부 등록 생산자의 당시 첫 증거 단절 확인(source_relation 외 세 분야 미충족). 역사 기록이다.
- **v599:** 시즌/영약/기름 비동기 조회 중 사용자 선택이 낡은 장비값으로 복구되는 문제 해결.
- **v600:** 이미 검증·등록된 E0를 반지1 또는 반지2 **한 부위** 선택하는 UI 경로.
- **v601:** 무기 subclass 원본 마스크는 계열, 실제 주무기/보조무기 손 판단은 최종 장비에서 검증. 계열 정보만으로 마부 승인 금지.
- **v602:** 봉인된 같은 빌드 v191/v211/v213 원본에 근거한 정확 SimC enchant_id 입력의 **simc_input** 증거 생산/연결.
- **v603:** 영구 마부는 기존 chmv_budget 검증에서 **정확한 4스탯 fixed_E** 필수. 값이 없으면 E0로 간주 금지.
- **v604:** 서명된 E0를 반지 외 일반 대표 장비에도 선택하는 **단일 마부** 사용자 경로(v106→v098→v096 및 UI). 무기/양수 E 일반화/서로 다른 부위 복수 마부는 아직 미완료.
- **v605:** 최종 v220 물리 마스크의 목걸이 neck=InventoryType2 누락 해결 및 실제 E0 일반 장비 선택 가능성을 UI에 정확하게 표시.
- **v606 최신:** 동일 시즌 원본 v211의 완전히 분류된 **static_nonchmv_item_mod** 중 모든 component가 알려진 비CHMV 정적 수치이고, spell_effects/unknown_components/동적 CHMV/custom handler 등이 없으며 ID/token/빌드/SHA·원본 분류·범위가 모두 일치한 정확 항목에 대해서만 **정적 고정 E0 네 스탯**을 기존 chmv_budget 증거로 산출하고 v216→v220→v212에 전달. 이는 정적 CHMV 소유권 증거다. 효과 발동·Native DPS·품질 우위 증명이 아니다. **새 실제 Policy A 승인/사용자 선택지 0개**, 실제 이 시즌 E0 생성 개수도 새 원본 빌드를 돌리지 않아 미측정. E+와 주문/미분류 항목은 보류.

**정확한 현재 첫 차단:** v606의 조건을 만족한 정적 E0 항목은 기존 Policy A의 **source_relation + simc_input + chmv_budget**까지 받을 수 있어도, **product_input = 동일 효과·실제 사용조건·최고 품질의 관련 수치 비열등성** 미확정이다. v220은 **네 증거**가 모두 있어야 자동 등록 가능. 새로운 승인 Gate나 수동 승인 추가하지 않는다.

## 5. v585 실제 품질 조사에서 드러난 주의사항

70783의 원본 Wago/SimC가 연결된 영구 마부 8개 최고 품질 계열에 대해, 5/8은 DBC 정적 component 수치 방향이 비열등, 3/8은 spell-driver 비교 필요. **8/8 모두 등급별 id_spell 다름, 실제 동일 효과·비열등성 품질 인증 0/8**. SimC는 E_ENCHANT_ITEM spell 효과 평균을 우선하고, 그것이 0일 때 DBC ench_amount/coeff를 사용할 수 있다. 따라서 DBC 계수 상승만 보고 실제 수치 우위를 인증하거나 낮은 품질을 삭제하면 안 된다. 동일 이름/품질 랭크/ItemLevel만으로 같은 효과도 추정 금지.

v606에서 **DBC에 CHMV가 없으면 모두 E0**라는 단순 규칙을 만든 것이 아니다. 알려진 비CHMV static-only 전부를 원본·영수증까지 폐쇄적으로 비교한 좁은 경우만 E0. 효과 미확인·spell/unknown/CHMV 구분 안 되는 항목은 E 미확정.

일반 임시 마부는 범위 밖, 무기 **기름 O는 별도 지원**. DK 룬벼리기는 SimC 클래스 원본 별도 경로, Wago 룬 아이템 수집/효과 발동 검증 추가 금지. 옴니움 장서 같은 확장팩 특수 콘텐츠는 일반 제품 완성 후 ON/OFF 선택형 모듈, 핵심 제품 완성 선행 Gate 아님.

## 6. 지금 다음 작업은 하나 — product_input 실제 증거

1. **실제로 제품 선택지로 등록할 가치가 있는 정확 한 마부 계열/ID**를 같은 시즌 v211/v213/v583/v584/v585의 이미 봉인된 원본과 최신 설치 v212에서 선정. 인증된 실제 ID/품질·부위·효과/사용 조건, 게임 빌드·SimC revision·SHA를 먼저 확인한다. 가상 아이템/합성 영수증으로 READY 생성 금지.
2. **동일 효과·동일 적용 조건·최고 품질의 비열등성**을 실제 SimC 원본 경로(id_spell 포함)에서 가능한 범위로 좁혀 증명한다. 이는 UI 최고 품질 중복 선택지 정리이며 **마부가 실제 발동하는지 별도 독립 인증하는 일이 아니다**. 원본이 이 관계를 입증하지 못하면 해당 항목만 PENDING, 승인하지 않고 STOP. 필요한 경우에만 한정된 최소 Native/소스 확인으로 사용자가 실제 소비할 정확한 입력/수치를 확인한다.
3. 증거가 충분한 정확한 한 항목에 대해서만 **기존 v220 product_input**에 연결→v196→v212 Policy A 자동 등록(추가 수동 승인 불필요)→v113 UI/사용자 선택→v106/v098/v096 정확한 실물 장비/마부 ID·B/T/L/E/O·프로필 SHA/캐시 정체성. 이미 존재하는 같은 조건 Native 결과가 없고 변경된 실제 사용자 경로를 확인해야 할 때만 최소 한 시나리오 SimC DPS/SEM/95%/재개 검증 후 STOP.
4. 이후 **일반 양수 E**, **복수 부위 영구마부 동시 선택 및 E 합산/중복 방지**, 나머지 일반 사용자 필수 옵션·최종 제품 E2E를 사용자 소비 순서로 확장한다. 이 시점까지 전체 마부/26 DPS 전수 Native나 효과 해석 엔진 금지.

**모든 변경 전 사용자에게** (a) 실제 사용자 흐름의 위치, (b) 현재 못 하는 일, (c) 기존 생산자/소비자의 첫 끊긴 지점, (d) REUSE/CONNECT/FIX 우선, (e) HTTP/DB2/Native·CPU/RAM/I/O·캐시 비용, (f) STOP 기준을 간단히 설명한다. **STOP → REUSE → CONNECT/FIX → 최소 EXTEND → 최후 NEW.**

미선택·미승인 마부 때문에 검증된 기본 시즌 G/J/F/O와 사용자 SimC 실행 전체를 막지 않는다. 다만 영구 마부 제품 선택지가 불완전한 현재를 **전체 영구 마부 완성 또는 full product ready**로 주장하지 않는다.

## 7. 최신 Actions/공식 원장/권한

**v606 중간 코드** dab7df72 CI의 신규 테스트 Python copy import 누락으로 v583 #44324423890 / v212 #44324424024 / web API #44324423924 FAIL. **ac2b7161 교정 뒤 최종:**
- [v583 #44324621970](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44324621970) SUCCESS
- [v212 Windows·Ubuntu #44324621955](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44324621955) 각각 **522 PASS/4 SKIP/0 FAIL**
- [웹 API Windows·Ubuntu #44324622220](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44324622220) 각각 **489 PASS/1 SKIP/0 FAIL**
- [집중 #44324622026](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44324622026) **681 PASS/2 SKIP/0 FAIL**
- [UI Windows·Ubuntu #44324622066](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44324622066) 각각 **313 PASS/0 FAIL**
- [Windows ZIP #44324624751](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44324624751) SUCCESS
- [78계약 #44325151294](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44325151294) SUCCESS (이전 docs HEAD 기준).

**v606 신규 Native 0 / 게임 원본 HTTP·DB2 0 / 기존 캐시 폐기 0**. 위 CI는 실제 신규 일반 마부 DPS E2E가 아니다.

**공식 원장: 15/78 COMPLETE, full_product_e2e=PENDING, next_review=B10.** 15/78을 제품 구현률로 읽지 않으며, B10 검토 순서를 P1 사용자 기능 개발 중단 명령으로 읽지 않는다.

별도 승인 없이 **main 병합, v003 immutable 변경, 원본 v016 직접 통합 완료 주장, Project Sources/Instructions UI 적용 완료 주장, Work OS M0/Shared State 공식 승격, 78 COMPLETE 조작, 기존 주 제품 개발 채팅 소유권 변경** 금지. GitHub 격리 개발과 공식 제품 승격은 별개다. WEQUIP의 영구 authority/runtime 의존성 금지.

## 8. 새 채팅 READ-ONLY 첫 응답 및 STOP

새 채팅은 위 문서/최신 CURRENT/코드/Actions/Native를 **실제 읽고** 다음 7항목만 간명하게 보고한다.

1. 현재 HEAD와 실제 최근 Actions PASS/FAIL/CANCELLED/SKIP
2. 최종 26 DPS 미래 절대 rating 목적, 런타임 AI 0, SimC/우리 책임 경계
3. ZERO-SOURCE와 Windows 기본 E2E PASS, v606의 정적 E0 증거와 신규 일반 마부 Native E2E 미실증
4. 기존 적응형 SimC·DPS/SEM/95%·캐시·중단·재개 실증
5. 필수 남은 product_input/품질·일반 E+/다부위·전체 제품 E2E, 선택형 Omnium·DK 별도 경로
6. 비용 대비 **다음 작업 하나**, 기존 자산 재사용과 STOP 기준
7. 미확인 증거, 공식 78 원장, GitHub/Project UI/Work OS/개발 소유권

**첫 응답에서 코드/문서/GitHub 변경·신규 Actions/Native/HTTP/DB2·원본 재수집 없음. 보고 후 STOP. 사용자 별도 '진행' 시 그때 HEAD를 새로 읽고 첫 실제 장애 하나만 최소 개발한다.**

**END — 제품 목적: AI 없이, SimC DPS로 미래 CHMV 절대 rating을 찾는 사용자 프로그램 완성. 이미 성공한 엔진을 다시 만들지 말라.**
