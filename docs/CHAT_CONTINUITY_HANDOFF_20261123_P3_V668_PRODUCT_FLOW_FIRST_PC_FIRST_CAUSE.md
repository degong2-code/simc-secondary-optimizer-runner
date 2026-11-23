# SIMC SECONDARY OPTIMIZER — 2026-11-23 P3 v668 제품 목적·실사용 첫 장애 중심 독립 복원/인계

> **첫 응답 계약: READ-ONLY 7항목 보고 후 STOP.** 다음 새 일반 채팅은 아래 순서로 GitHub **그 시점 최신 HEAD**·CURRENT·코드·Actions·Native/ZIP 영수증을 독립 조회한다. 첫 응답에서 어떠한 코드/문서 수정, Actions/Native/HTTP/DB2 실행·외부 설치, 공식 원장 승격도 하지 않는다. 사용자 별도 `진행` 이후에만 현재 격리 브랜치의 최소 제품 수정을 시작한다. 이 인계 문서 작성으로 기존 주 제품 개발 채팅 소유권이 자동 이전된다고 주장하지 않는다.
>
> **인계 작성 전 조회 HEAD (정적 스냅샷):** `b707fb1b20014feeccf9b5b245521b9016eb1ce5` — 인계 파일 및 CURRENT 기록 커밋 후에는 HEAD가 달라진다. 항상 최신 HEAD 재조회.

## 1. 필수 정본과 읽기 순서

- 저장소 `degong2-code/simc-secondary-optimizer-runner`, 격리 브랜치 `probe/chat-cache-v035-20261024`; GitHub `main` 병합은 허가되지 않았다.
- **첫 문서 이 파일** → `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` (머리부터 실제 최신 순서) → `docs/development/notes/2026-11-23_p3_v668_settings_dynamic_status_visual_hierarchy.md` → `docs/development/notes/2026-11-22_p3_v667_season_failure_diagnostic_exact_fj_restart.md` → `docs/development/notes/2026-11-22_p3_v666_disabled_oil_b8_partial_special_gear_user_feedback.md` → `docs/development/notes/2026-11-22_p3_v665_user_ux_consumables_enchants_icons_embellishments.md`.
- 이전 제품·상태의 실제 성공 범위: `docs/development/notes/2026-11-19_p3-v639_published_zip_70961_final_result_restore.md`, CURRENT의 v570/v572 실제 Windows E2E/취소·재개 기록, v567 Zero-source, v611 예산, v629~v633 영구 마부.
- 범용 SimC 관리 계보와 남은 공백: `docs/development/notes/2026-11-22_p3_v661_selfbuilt_cache_publish_bridge.md`, `docs/development/notes/2026-11-22_p3_v660_generic_oneclick_clean_windows.md`, v657~v659 노트, `docs/CHAT_CONTINUITY_HANDOFF_20261122_P3_V660_GENERIC_SIMC_UPDATE_PRODUCT_FIRST.md` (역사적 우선순위만), `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`, `docs/development/UI_DESIGN_VERSION_REGISTRY.md`, `WINDOWS_BETA_START_HERE.md`.
- 실제 코드: `runner/webui/index.html`, `runner/webui/styles.css`, `runner/webui/app.js`, `runner/v113_local_web_api.py`, `runner/v216_environment_build_coordinator.py`, `runner/v218_v098_profile_stage_adapter.py`, `runner/v432_selected_4pc_budget_bridge.py`, `runner/v665_official_item_icons.py`, 실제 테스트·Windows v181 packager/workflow. **문서 주장과 실제 CODE/HEAD/Actions 실행 증거를 분리**한다.
- 사용자 직접 최신 결정 > 최신 승인 설계 > 실제 최신 소스·CURRENT·Actions/Native/ZIP 영수증 > 과거 인계/역사 자료. Project Sources 사용자 UI 등록 완료를 GitHub 문서나 제공된 파일로 추정하지 않는다. 첨부 v1.4.1(2026-10-29)의 오래된 **27 DPS/증강 포함**은 최신 사용자 직접 결정 **26 DPS/증강 제외**로 교정해야 한다.

## 2. 제품 취지 — 개발을 판단하는 최우선 목적

**26개 딜러(DPS) 전문화에 대해, 미래 목표 아이템레벨(기본 334) 또는 사용자가 직접 입력한 최종 T에서 SimulationCraft DPS를 최대화하는 치명·가속·특화·유연의 최적 절대 rating을 찾아주는 일반 Windows 프로그램.** 결과는 절대 rating, 보조 비율, 관측 DPS, SEM, **95%** 통계 판정(미확정도 정직하게), 실질적으로 분배가 다른 근접 대안, 실행/저장/재열람. **증강 기원사·탱커·힐러 제외**.

**실제 사용자 흐름**: ZIP 1개→필요시 현재 게임 빌드와 호환되는 SimC 자동 확보/검증→캐릭터·전문화·종족·특성/목표 ilvl 또는 수동 T/장신구 2개·선택 특수효과·장식(최대 2개)·소모품·전투조건→해당 시즌 G/J/F/O **전체** 자동 구축/검증→선택된 예산/고정치 보호→내부 대표 일반 장비/무기/티어4세트와 SimC 기본 APL 프로필 생성→기존 적응형 Native SimC 최적화→DPS·SEM·95%·후보/대안→캐시·취소·재개·저장·재열람.

공식 회계: `B=G+J+F`, `T=B+O`, **수동 최종 T 우선**이면 `B=T−O`, `c_final=c_base+o`. 기름 O는 고정·비자유분배이며 동일 rating에 **한 번만** 포함, 정확 특수장비 L은 G 안의 스탯별 고정 하한이므로 다시 더하지 않음, 정적 영구마부 E 역시 해당 회계 소유권에서 한 번만 반영. 새 시즌 G/J/F/O는 **그 시즌 원본으로 모두 새로 결정**, 과거 J92/F165/G2850/79×2 근사를 새 시즌에 복사하지 않음. 정확한 v212 설치 SHA와 시즌/목표 ilvl/F/J/O 조건 불일치는 READY가 아님.

전체 착용 장비 선택·현재 스탯 재분배·장비 추천/파밍 경로/전체 시즌 장비 DB는 **제품이 아니다**. SimC 프로필 업로드는 캐릭터·특성 불러오기 보조, 현재 장비를 목표로 복제하지 않음. SimC는 APL·아이템/장신구/장식/보석/마부/proc·DPS 책임, 자체 코드는 프로필/ID/조건/정적 rating·중복방지·후보/통계/캐시만. **별도 효과·APL 인증 Gate/새 optimizer/AI 영구 런타임 의존성 0**. Omnium처럼 시즌 한정 기능은 선택 모듈로 완전 ON/OFF 가능해야 한다.

## 3. 재사용 가능한 제품 성공 자산 — 재개발/Native 반복 금지

- v567 **ZERO-SOURCE 시즌 환경 자동 구축 성공**. v611 및 실제 70961/334 검증 대표 예산 `G2850/J92/F165/O0/B=T3107` (그 시점/조건에서만), v629~v633 **영구 마부 38/38 등록**, 신규 실측 필요한 미확정 E만 기존 Native 경로로 처리.
- v624 E0 Native64, v636~v638 수동/자동 T·양수 E·취소·재개 및 실 ZIP 영수증.
- **v639 실제 배포 ZIP, 징벌 성기사/334/70961 Native64**: 관측 최종 rating `1098 / 922 / 922 / 165`, DPS `161718.63`, SEM `243.11`, 95% **우위 미확정**, 실질 근접 대안 **5**, 저장·로컬 서버 재시작·재열람 PASS. [Actions #44539361949](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44539361949).
- **v570 실제 Windows Chrome 한 케이스 E2E**: 70783/334, ZERO-SOURCE 수집/설치 + 장신구 2개 선택 → 실제 SimC **DPS Native64**, CHMV `571/1165/1206/165`, DPS `179563.6082`, SEM `316.8207`, 95% 우위 미확정·대안 5. [Actions #44074372451](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44074372451). **실제 사용자의 개인 Windows PC가 아니라 GitHub Windows runner 1조건 E2E**.
- **v572 실제 배포 ZIP 중단→서버 종료·Chrome 재시작→이전 세션 복원→재개→재중단**: 누적 Native DPS4회, 이전 SimC 원본/영수증 SHA 보존; 전체64 완료로 주장 금지. [Actions #44082378854](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44082378854).
- 기존 정확한 session identity/정적 캐시/실제 DPS 캐시/95% 판정/근접 대안/로그·롤백 보존. 같은 시즌 정적 아이템 캐시는 단순 SimC revision 변경으로 폐기하지 않으며 **사용자 명시 교정**만; DPS 캐시는 바이너리 SHA·빌드·프로필·장비 옵션·후보·O·전투조건·iterations별 분리. 완료 결과를 재계산하지 않는다. 앞선 단일 사례 성공을 26개 전문화 완성/개인 PC PASS로 확대하지 않는다.

## 4. 최신 제품·Windows v668 증거와 변경 범위

- v657~v661은 공식 Nightly 여러 후보의 **실제 게임빌드** 확인→기존 관리본/검증 공개 자체 빌드 캐시 HIT→안전 py7zr 압축 해제/해시 검증/원자 설치·롤백→신뢰된 빌더 request push 시 HIT면 컴파일 생략/MISS면 소스 SHA 고정 Windows CLI 빌드·EXPERIMENTAL prerelease 게시까지 연결. **공개 캐시가 없는 완전 신규 시즌에 일반 사용자(토큰 없음)가 직접 보낼 신뢰된 원격 빌드 요청 브로커는 미구현**; 운영 권한 별도 승인 없이 새로운 서버나 PAT 요구하지 않는다. 자체 컴파일본은 공식 SimulationCraft 릴리스가 아님. 일반 사용자에게 SimC 별도 ZIP/외부 7-Zip 설치를 v668 기본 사용법으로 되돌리지 말 것.
- v663~v664 실제 Windows py7zr 우선 변경과 7자리 Git revision 원본 조회 응답 크기 첫 장애 및 검증 full SHA 자동 사용. 최초 `V229_SET_BONUS_BUILD_OR_HEADER_MISMATCH`의 직접 원인은 역사적으로 **확정되지 않았음**; 첫 재현 영수증 `V229_REVISION_LOOKUP_RESPONSE_TOO_LARGE`는 그 실행의 구체적 선행 차단. 새 CLI를 연결했다고 오류 완치로 주장하지 않는다.
- v665: 장식 UI를 캐릭터 프로필 하단으로 이동, 검증 마부 이름/정적 E 중심 간결화·같은 효과 강한 ring 마부만 노출, 공식 Blizzard item-media 아이콘 정확 ID/HTTPS 검증+실패 시 중립 표시. **음식/딜물약 기본 자동 사용·영약 DPS 기반 결정은 아직 미구현**: v218 현재 시즌 `source_default` → `disabled`; 과거 토큰을 현재 시즌의 승인 효과로 승격하지 말 것.
- v666: 실행 버튼 비활성 사유 표시, 기름 ON 무기 조합 미검증 차단/명시적 O=0 재사용 구분, `WEB_SELECTED_B8_PROFILE_OR_STATIC_VARIANTS_PENDING`을 선택 특수효과 장비·장식 **정확 정적 변형 또는 프로필 부족**과 구분(기름 OFF 때문이라고 오판 금지). 특수효과 장비 10여 개 표시는 렌더링 80 상한 때문이 아니라 현재 검증 설치 후보만 노출; `full_season_completeness_confirmed=false`이므로 **전체 목록 완성 보증이 아님**.
- v667: 중복 설치 F/J `V216_UNQUALIFIED_MULTIPLE_INSTALLED_FJ_VARIANTS_SELECT_EXACT_SHA`에서 기존 v212 검증 설치본을 F/J·소켓·O=0 기준 **정확 설치 내부 SHA로 명시 재연결**; 같은 표시 조건의 여러 출처는 구별 불가능하므로 선택 보류. `LOCAL_SESSION_PRECHECK_BLOCKED`의 안전 예외 `kind`·고정 실패 단계·HTTP 상태를 **진단 영수증**으로 복사. 실패한 요청의 '검증 요청 중' 잔여 표시 제거. 사용자 세션/캐시 삭제·무단 예산 선택·Native 재실행 없음.
- **v668 최신 UI**: SimC '저장 설정 불러옴(검증 전)' vs 실제 CLI `display_build=2` 확인/저장, '출력 게임 데이터 빌드' vs '현재 게임·시즌 일치(별도)' vs '수동 Git revision/CLI 확인 수준'을 라벨·값·글씨 크기로 분리. READY v212에서만 G/J/F/O/T 수치 강조, 미확정은 설명/대기. 디자인 v653 컨트롤 기준/과도한 카드 금지, 성공/대기/실패 텍스트 명시, `textContent` 안전 처리. **표시 개선은 Source/Native/시즌 READY의 새 증거가 아니다**.
- **v668 실측 Windows** [#45093009034](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45093009034) Windows 2022 Python 3.12·3.14 각각 **344 PASS/0 FAIL**, 압축 해제·로컬 HTTP3 계획·패키징 파일 SHA/CRC PASS. API [#45093009038](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45093009038), UI [#45093008960](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45093008960), focused [#45093009083](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45093009083): SUCCESS. **Native DPS0, 새 C++ 빌드0**. v668 한 번 압축 해제하는 실제 제품 ZIP SHA256 `c4666ca21b20da1bd60cfb94a271574d544097253d7bf832c88f5f6c56d3ea90`, **1,529,712 bytes**, 286 source files SHA/ZIP CRC PASS. [Actions artifact #14782331499](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45093009034/artifacts/14782331499)은 중첩 wrapper이므로 실제 단일 제품 ZIP과 구분. 초기 회귀 일부 실패·취소/스킵 이력은 숨기지 않고 최종 green과 분리.
- **사용자 개인 PC 최신 관찰:** 수동 지정한 `simc-1210.01.710c240-win64\simc.exe`, Git revision 입력 `710c240`; `SimC 연결 확인·저장` 이후 실제 CLI 출력 게임 데이터 빌드 **`12.1.5.70575`**, 그러나 이전 검증 시즌 설치/사용자 요청은 **`12.1.5.70961`**. 둘의 **빌드가 다른 사실**을 기록하되, 최신 KR Live가 무엇인지/선택 세션·원본의 현재 상태를 독립 확인하기 전에는 자동 호환·시즌 READY 또는 과거 설치본 재사용을 주장하지 않는다. 입력 Git revision은 실행파일로부터 **독립 인증된 full SHA가 아님**. 사용자 PC에서 v668 실제 시각적 인수 및 70575↔70961 간 온전한 Chrome→SimC 최적화는 **미확인**.

## 5. 현재 우선순위 — 원격 빌더보다 사용자 첫 막힘 해소를 먼저

**P0 / 바로 다음 실사용 접합 1건:** v668을 사용자의 Windows에서 재확인하되 **먼저 SimC CLI 실제 출력 빌드·요청 KR Live/설치 시즌 v212 manifest·영약 J/F/O/ilvl 정확 identity를 읽기 전용으로 대조**한다. 현재 입력값은 710c240/내장70575, 과거 검증 시즌은 70961. 무단 버전 교체·비밀키 제출·캐시 삭제 없이 mismatch를 분리하고, 기존 확인된 호환 관리본/공개 캐시가 있으면 재사용한다. 사용자 원본 오류 **최초 한 건**만 재현: `V216_UNQUALIFIED_MULTIPLE_INSTALLED_FJ_VARIANTS_SELECT_EXACT_SHA`, `LOCAL_SESSION_PRECHECK_BLOCKED`의 `error_kind/failure_stage/http_status`, 실제 다른 원본 `V229_...`이면 독립 최초 실패 추적. 진단 영수증 복사만 요구하고 비밀키·프로필·Windows 사용자 전체 경로 유출하지 않는다. 전체 시즌 재구축·Native 재실행 금지.
 
**P1 / 하나의 정상 기본 구성 진입:** 검증된 같은 시즌/ilvl/F/J/O=0을 선택해 내부 대표 프로필을 구성하고, **기름 OFF, 특수효과 장비 OFF, 장식 OFF, 음식/물약/룬 현재 미승인 옵션 OFF**, 정확한 필수 장신구2와 기본 검증 영약/보석만 남긴 **최소 기본 시나리오**로 '최적 스탯 찾기' 실행 준비까지 확인. 검증 결과가 이미 존재하면 기존 cache/session 우선 재사용. 새로 실측해야 하는 첫 정확 경계만 허용된 최소 SimC 시험; 이전 64회·26전문화 전수 금지. STOP 기준: 같은 identity의 시즌 READY, 필수 선택과 실행 가능성, 실제 DPS·SEM·95%/대안·저장·재열람(이미 역사적으로 성공했던 범위 재실행 강요 안 함), 개인 PC의 첫 원인 resolved/remaining 정직한 보고.

**P2 / 기본 정상 경로 이후 추가 입력:** 시즌 환경 구축 과정에서 **기름 정확 ID/손별 적용/품질/고정 O/SimC 입력을 미리 등록·검증**, 사용자는 전문화 무기 구조에 따라 자동 적용. 기름 미사용 `temporary_enchant=disabled`와 O=0은 별도 정상 기본 사용 경로이어야 함. 기름 자체의 모든 장비조합/효과를 새로운 SimC 인증 Gate로 만들지 않는다. B8 선택 장비/장식의 정확 정적 variant·프로필 부족은 기존 exact native-on-miss 경로만 최소 증분 보완. 시즌 특수효과 후보 누락 여부는 v212/v213 현재 시즌 원본·분류 범위로 정확히 조사하되 전 시즌 DB 구축이나 장비 추천으로 확대하지 않는다.
 
**P3 / 사용자 편의와 소모품:** 시즌별 검증된 최고 품질의 주능력치 음식 기본, 전문화 기본 SimC APL 딜물약 실제 token/적용 조건, 검증된 F 영약을 CHMV 최적화에 맞춰 선택. 기존 v216/v212/v218/SimC·예산 identity에 연결; 검증 전에 UI만 사용으로 바꾸지 말 것. v665 공식 아이콘의 개인 PC 실표시/한국어 아이템명/반지 마부 동일 효과 하위 숨김·장식 위치/v668 동적 상태 실제 가독성은 별도 UI 인수. 사용자 UI를 SimC 개발용 manifest/SHA 선택 화면으로 만들지 않는다.

**P4 / 범용 신규 패치 SimC 공급의 잔여 공백:** 공식 Nightly와 공개 자체 빌드 캐시가 모두 없을 때 일반 사용자의 안전한 원격 Windows 빌드 요청을 처리하는 **브로커/운영 자동 갱신**은 아직 미구현. v657~v661(특히 v661 캐시 HIT 및 신뢰된 push→게시)을 재사용해 필요 최소만 연결. 사용자 PC에 C++ 컴파일러/PAT/비밀키 강요 금지, 익명 GitHub Actions dispatch를 가정하지 않기, 인증·남용 비용·중복 빌드·소스40 SHA/게임빌드/배포 SHA·artifacts 만료·권한을 검토. 새 운영 서버/main workflow/default branch 권한은 별도 사용자 승인 전 구현/운영하지 않는다. **현재 실제 사용 장애를 미루고 원격 빌더 플랫폼부터 만드는 것이 우선순위는 아니다.**

**모든 결정:** `STOP → REUSE → CONNECT/FIX → 필요한 최소 EXTEND → 최후 NEW`. 첫 실제 실패를 확인→동일 조건 캐시/이전 영수증 조회→작은 결손 하나만 수정→focused/offline Windows 회귀→미확정 구간에만 Native·HTTP/DB2. 실행 시간·메모리·디스크·네트워크·Actions 컴파일/중복 비용 포함 검토. 화면에는 '왜 버튼이 막혔는지/어떻게 해결하는지'를 개발 코드보다 먼저 제시. 연쇄 PENDING 항목을 각각 새 엔진/Gate의 근거로 삼지 않는다.

## 6. 주요 금지와 승인 디자인/통계/권한

- 사용자 승인 기본 시각 설계 **v653**(컨트롤/간결 구분선)과 최신 v665~v668 실제 UI 개선을 계승. 변화하는 상태는 고정 설명과 분리·더 강한 글꼴/값, 성공은 실제 검증되었을 때만. 사용자 동의 없는 UI 전면 개편/장식 과다 추가 금지. 화면에 외부 로그/파일 경로·SHA/기술 PENDING의 홍수보다 **한 가지 첫 차단/다음 행동**. 레이아웃 기존 ID/접근성/저장 세션 복원 보존.
- Git revision 문자열·SimC 표시 게임 데이터 빌드·실제 WoW KR 게임 BuildId·현재 시즌 v212 installed SHA를 **각각 별개** identity로 취급. 710c240은 실측 GUI 입력값, 70575는 최근 CLI 실측, 70961은 별도 과거 검증 시즌; 버전 불일치인지/헤더·파서/원본 접근 문제인지 실제 source receipt 없이 추정 금지.
- G/J/F/O 필수 owner 미확정이면 Environment READY 금지, 단 선택 아이템 후보만 미확정이면 검증된 기본 환경까지 불필요하게 차단하지 않음. 기름 OFF/ON을 자동으로 바꾸지 말 것. 동일 수치 F/J 중복은 번호만 같다고 동일한 효과로 판정하지 않음.
- 95% 관측 우위 미확정은 정직하게 표시, '최고 관측 후보'≠전역 최적 증명. 정적 마부 E/장신구 L 등 회계 재가산 금지. 고품질 결정은 동일 효과·조건·적용 범위·수치 확인 이후. 음식/물약은 SimC APL/아이템 효과를 자체 재구현하지 않음.
- **형식적 78 계약 원장**의 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10`은 이전 공식 기록으로 유지하지만 **15/78은 제품 개발률이 아니며 일상 제품 진척 KPI로 쓰지 않는다**. GitHub/Work OS의 공식 계약 상태를 임의로 변경·승격하지 않는다. B10/Work OS M0가 일반 제품 구현/승인된 최소 Native 시험을 중단시키는 선행 Gate가 아님.
- 사용자 별도 지시 없이는 `main` 병합, v003 immutable 변경, 원본 v016 직접 통합 완료 주장, Project Instructions/Sources 실제 적용 완료 주장, Work OS M0/Shared State/78 계약 공식 승격, 기존 주 제품 개발 채팅 소유권 이전, WEQUIP 영구 권한/운영 의존성, 별도 외부 서버 도입 금지. **인계 준비는 권한 이전이 아니다**.

## 7. 새 채팅이 첫 응답에서 보고할 정확한 7항목

1. **최신 GitHub 실상:** HEAD(인계 문서의 정적 SHA 재조회)·CURRENT·v668 단일 ZIP 바이트/Actions #45093009034·API/UI·취소/실패/건너뜀·신규 vs 역사 Native 경계.
2. **진짜 제품 목적:** 26 DPS 미래 ilvl/T CHMV 절대 rating·실제 SimC DPS, G/J/F/O와 L/E/O·95%·근접 대안, 생성형 AI 런타임0, 장비 추천/전체 DB/새 엔진 아님.
3. **재사용 성공:** v567 Zero-source, v611 예산, 영구 마부38/38, v639 Native64, **v570 Chrome 실제 Native64**, **v572 중단·재개**, 캐시/저장/재열람 및 각각 검증 범위.
4. **v657~v668 진척:** SimC 자동 관리 공식/자체 컴파일/공개 캐시, v665 UI 마부/아이콘/장식, v666 oil/B8/후보 수, v667 정확 F/J·진단 영수증, v668 동적 상태 계층 및 최신 미구현.
5. **최근 개인 PC 최초 장애:** 최근 CLI `710c240` → 내장 **70575**, 이전 시즌 설치 **70961**; `V216...` F/J 중복, `LOCAL_SESSION_PRECHECK_BLOCKED` 미분류 근본 원인, oil OFF와 B8 구별, 시즌/프로필 READY를 주장하지 않는 기준.
6. **다음 작업 단 하나와 STOP 기준:** 최신 사용자의 **빌드/설치/실패 영수증 일치 조회 및 첫 blocker 1건 최소 FIX**가 우선, 기본 기름 OFF·선택 장비 없는 일상 UI 연결→필요한 최소 SimC 시험, 신규 원격 빌더는 후순위. 비용·캐시/권한 포함.
7. **공식 상태·권한:** 15/78 의미 제한, `full_product_e2e=PENDING`, B10, v653 UI·main/immutable/Project UI/Work OS·주 개발 채팅 소유권 제한.

**정확히 일곱 항목 보고 후 STOP**. 사용자가 별도로 `진행`이라 지시하면 해당 시점 최신 HEAD/첫 미완료 접합을 재확인하고 격리 브랜치에서만 최소 제품 개발을 실시한다. 신규 Native/Actions/원본 HTTP/DB2를 습관적으로 재실행하지 말 것.

**최종 원칙:** 완성된 엔진을 다시 만들지 않는다. 일반 사용자가 별도 AI 없이 목표 CHMV 절대 rating·실제 SimC DPS/SEM/95%·대안을 받기까지 막히는 첫 연결을 재사용과 최소 수정으로 끝까지 해결한다.
