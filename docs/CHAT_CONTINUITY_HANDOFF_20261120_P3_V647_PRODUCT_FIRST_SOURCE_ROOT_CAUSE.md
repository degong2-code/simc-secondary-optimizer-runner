# SIMC SECONDARY OPTIMIZER — 2026-11-20 P3 v647 최신 일반 채팅 독립 복원·개발 연속성 인계

> **읽기 전용 시작 계약:** 새 채팅은 이 문서·최신 GitHub HEAD·CURRENT·실제 코드·Actions/Native 영수증을 독립 조회한다. 첫 응답에는 지정된 7항목만 보고하고 **STOP**한다. 사용자 `진행` 전에는 코드 수정·새 Actions·Native·HTTP/DB2·공식 상태 변경 금지. 본 문서는 개발 지식 인계이며 프로젝트 소유권 이전·공식 승격이 아니다.
>
> **2026-11-20 14:01 KST 확인 인계 스냅샷 HEAD:** `250835fe3db2d7e6b8530ed4c22f0dcd1e6be506`. 작성 직후 docs 커밋으로 바뀌므로 **새 채팅에서 최신 HEAD 필수 재조회**.

## 1. GitHub 정본·읽기 순서 및 분류

- Repo: `degong2-code/simc-secondary-optimizer-runner`.
- 격리 개발 branch: `probe/chat-cache-v035-20261024` (main 병합 금지).
- **최신 개발 목적 P3:** 사용자가 AI 없는 Windows 제품에서 현재 시즌을 **ZERO-SOURCE 자동 구축**하고, 미래 목표 CHMV 절대 rating 최적화의 SimC DPS/SEM/95% 결과를 저장·재열람할 수 있는 실사용 제품 완성. 독립 EXE/모든 사용자 PC 출시 승인 전 상태.
- **먼저 읽기**: 본 인계 → `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` → `docs/development/notes/2026-11-20_p3-v647_three_view_editorial_visual_balance.md` → `docs/development/notes/2026-11-20_p3-v646_source_failure_first_cause_user_recovery.md` → `docs/development/notes/2026-11-20_p3-v645_simc_connection_confirm_and_credential_save_visibility.md` → `docs/development/notes/2026-11-20_p3-v644_settings_ui_sevenzip_and_source_pending.md` → `docs/development/notes/2026-11-20_p3-v642_simc_updater_integrity_efficiency.md` → `docs/development/notes/2026-11-19_p3-v639_published_zip_70961_final_result_restore.md` → `docs/development/notes/2026-11-19_p3-v638_published_282_zip_real_70961_user_native4.md` → `docs/development/notes/2026-11-19_p2-v637_manual_final_T_signed_Eplus_real_windows.md`.
- 그다음 `WINDOWS_BETA_START_HERE.md`, `docs/development/APP_PACKAGE_FILE_REGISTRY_20261113.md`, `docs/development/POLICY_PRODUCT_FIRST_MINIMUM_SUFFICIENT_VERIFICATION_20261114.md`, `docs/development/POLICY_ZERO_SOURCE_AUTODISCOVERY_GENERALIZATION_20261113.md`, `docs/development/ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md`, `docs/development/78_ELEMENT_COMPLETION_CONTRACTS.json`, 실제 GitHub Actions/Native/ZIP manifest 교차 검증.
- 기존 `docs/CHAT_CONTINUITY_HANDOFF_20261119_P3_V637_WINDOWS_PACKAGE_PRODUCT_FIRST.md`는 **과거 스냅샷**이다. 여기의 282파일/v637과 새 v647 283파일을 혼동하지 않는다.
- 업로드된 v1.4.1 문서 중 과거 **27 DPS·증강 기원사 포함** 문구와 2026-11-02 이후 최종 사용자 **26 DPS·증강 제외** 정책 충돌 시 후자 우선. Project Source UI에 실제 교체됐다고 추정 금지.

## 2. 흔들면 안 되는 제품 목적과 회계

**26개 DPS 전문화만** 지원(증강 기원사·탱커·힐러 제외). 일반 사용자는 전체 현재 착용 장비나 현재 CHMV 총계를 입력하지 않는다. 목표 ilvl(기본 334) 또는 사용자 직접 지정 최종 CHMV `T`에서 **미래 파밍의 목표 치명·가속·특화·유연 절대 rating**을 SimC DPS 최대화로 찾는다. 현재 장비 재분배/장비 추천/파밍 경로/전체 시즌 아이템 DB가 아니다.

일반 흐름: **직업/전문화/종족/특성/장신구2·선택 특수장비·장식 최대2·고급 조건 → KR Retail 현재 빌드 자동 발견 → 같은 빌드의 대표 장비·무기·티어4 및 G/J/F/O 원본 검증·자동 구축 → B/T와 L/E/O 소유권 확인 → 대표 SimC 프로필 → 기존 적응형 SimC → 관측 최고 DPS·SEM/오차·95% 우위/미확정·실질적으로 다른 대안·CHMV 절대 rating/비율 → 캐시·취소·재개·저장·재열람.** 선택 SimC 프로필 업로드는 캐릭터 정보 수입용이지 현재 장비 복제용이 아니다.

`G` 목표 ilvl 대표 비장신구, `J` 최고 품질 기본 보석, `F` 최고 품질 영약, `O` 고정 기름. **`B=G+J+F`, `T=B+O`, `c_final=c_base+o`**. 수동 최종 `T` 지정 시 자동 예산보다 우선하여 `B=T-O`; 정확한 특수장비 `L`은 G에 이미 포함, 정적 마부 `E`는 검증 소유권/동적 하한에 한 번만, O는 별도 고정·비자유분배. 장신구 정적 gear 미관측 ≠0, 제작 50:50 초기값은 L 잠금 금지. 새 시즌 G/J/F/O는 모두 실제 시즌 원본과 빌드로 재검증; 과거 79×2 근사 참조와 F165/J92/기름 O 값을 새 시즌 고정치로 복사 금지. 같은 효과·조건이 확인된 최고 품질만 선택지 자동 등록, 시즌 특수 콘텐츠는 선택 모듈.

SimC는 아이템·마부·기름·장신구·장식 효과, proc/APL/DPS를 계산한다. 우리 코드는 입력 ID/slot/ilvl/빌드/옵션/예산/중복 방지/JSON2 정적 rating/후보·95% 통계·캐시·세션을 책임진다. **런타임 생성형 AI 호출 0**. 별도 효과·발동 인증기, 새 APL, 새 optimizer, EXE 변환 강요, 시즌 DB 전수 구축은 불필요하다. 통계 95%만 사용; 관측 1순위 ≠ 95% 확정 ≠ 전역 최적 증명.

## 3. 재사용해야 할 실제 성공 증거 (서로 합치지 말 것)

- **v567 ZERO-SOURCE 환경 구축** 성공. v611 실제 KR70961 기초 **G2850/J92/F165/O0/B=T3107** (해당 시즌/대표 시나리오만).
- **v629~v633 영구 마부**: 슬롯·손 관계 전달 결손 수정(등록19→30), 정적 E0 30개는 기존 원본 재사용, 미확정 E 8개는 기준 Native1+선택 Native8 **총9**로 확인해 해당 시즌 **38/38 자동 등록 PASS**. E+ 예시는 +24/+29 등 **미래 시즌 고정치 아님**. E0는 SimC 효과 없음이 아님.
- **v624** 별도 checkout E0 Native64 완주/결과·재열람; **v636** 자동 T3165/E+ Native4 취소·재개; **v637** 수동 최종 T3500·E58 하한/Native4 취소·재개. 모두 개별 증거.
- **v638 실제 배포 원본 ZIP** KR70961 ZERO-SOURCE·마부38/38·실 Chrome 수동T3500/E+ Native4 취소·재개 PASS.
- **v639 같은 282파일 원본 ZIP 자체의 대표 1건 종단**: KR70961 G2850/J92/F165/O0, 가슴 E0, 징벌 성기사/ilvl334/장신구2, Native2→취소→HTTP 재시작/재개→**Native64 완료**, 관측 rating **1098/922/922/165**, DPS **161718.63**, SEM **243.11**, **95% 우위 미확정**, 근접 대안 **5**, `global_optimum_proven=false`; 저장→서버 재시작→재열람 추가 Native0 **PASS**. [Actions #44539361949](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44539361949), [원본 노트](development/notes/2026-11-19_p3-v639_published_zip_70961_final_result_restore.md). 이것은 **한 대표 시나리오 ZIP E2E PASS**, 전26/모든 조합/실사용 개인 PC 전체 완료 아님.
- **v640** 첫 Windows 설치/동의 N→Y, Python/웹 의존성, 격리 Python 환경, Chrome 첫 화면 PASS. v641 처음 최적화 클릭의 SimC 사전 입력 검증 순서 수정.
- **v642~v646** SimC 업데이트 HTTPS 공식 호스트 교정·설치 안전성/중복 skip·UI 즉시 반응·7-Zip 오류 안내·명시 연결 확인/저장·원본 실패 첫 원인 및 복구 UX 연결. 새 런타임 SimC/DPS64 시험 증거 아님.

## 4. 실제 사용자 PC에서 새로 발견된 첫 장애 — 개발 최우선

사용자가 최신 Windows 베타에서 **시즌 환경 확인·설치**를 누른 실제 캡처:
- 상위 첫 원인: **`V229_SET_BONUS_BUILD_OR_HEADER_MISMATCH`**, 화면에서는 'SimC 세트 효과 원본의 빌드 정보를 확인하지 못했습니다'로 사용자 표현 개선(v647).
- 후속 `REPRESENTATIVE_TIER_SOURCE_PENDING`, `REPRESENTATIVE_GEAR_SOURCE_PENDING`, `G_NATIVE_RATING_OBSERVATION_PENDING`, `HIGHEST_QUALITY_GEM_J_SOURCE_PENDING`, `HIGHEST_QUALITY_FLASK_F_SOURCE_PENDING`, `WEAPON_OIL_O_EXACT_APPLICATION_AND_RATING_PENDING`, `FRESH_COMPILER_INPUT_*` 8종, `SOURCE_COMPILER:*`와 v212 GJFO/설치 PENDING은 **상위 원본 검증 실패에서 파생된 연쇄 상태**일 수 있다. 각각 사용자에게 입력하라고 요구할 25개 결함으로 보지 않는다.
- 특히 이 코드는 **실제 빌드가 다르다는 뜻일 수도, set-bonus 헤더 포맷·파싱 불일치일 수도 있다.** `V229_GENERATED_SIMC_COMPILED_BUILD_MISMATCH` 같은 **명시적** 코드를 받기 전에는 '구버전 SimC가 원인 확정' 주장 금지. v647에서 이를 쉽고 정확한 문장으로 고침.
- 사용자의 당시 `simc.exe` 입력 `7bc1071`은 과거 생성 데이터 헤더 70448, 받은 `0d19401` .7z의 생성 데이터는 70783, v639의 검증 `9933ffb`는 70961; 확인된 최신 SimC `midnight` 소스 HEAD `6924096`은 70961이었다. **Git revision 번호와 게임 BuildId는 다른 것**이며 최신 소스 = 최신 Windows Nightly 바이너리 보장 아님. 당시 GitHub fallback 실제 사용자의 `0d19401`은 70961 대응이라고 단정할 수 없다. 실제 PC의 현재 binary SHA/revision/출력 game build와 요청한 KR 현재 빌드를 반드시 다시 확인한다.
- **v289**은 Blizzard 공개 `https://us.version.battle.net/wow/versions`에서 KR Retail live BuildId를 조회; **v229**는 pinned SimC Git 원본의 generated 파일 헤더/build를 비교. 공식 조회 실패 시 오래된 build를 현재로 가정하지 않는다. 공개 API/툴 사용 제한으로 직접 확인 못한 경우 `v289 실제 PASS`라고 쓰지 않는다.
- **근본 원인 조사 순서**: 기존 UI의 `진단 영수증 복사`에서 비밀정보 없는 상위 `fresh_pinned_first_party_simc_source.status/reason`, Git commit resolution·소스 분류, 대상 `game_build`, `source_compilation.missing` 확인 → 해당 정확 revision의 기존 `v229` `item_set_bonus.inc` 원본 헤더 및 parser 기대/실제 포맷, 같은 빌드 인증 경계 대조 → (a) 실제 build 불일치라면 사용자에게 검증 가능한 공식 SimC 빌드 안내, (b) parser/경로 결함이면 **그 단일 원인만** FIX, (c) 네트워크/인증/원본 미제공이면 정확한 회복 안내. **새 compiler·stage·효과 인증 Gate를 만들지 말 것.**
- 실제 사용자 PC에서 복구와 ZERO-SOURCE→GJFO v212 READY/대표 결과까지 완료됐다는 새 증거는 **아직 없다**. 여전히 `full_product_e2e=PENDING`(전 제품 범위). 사용자가 새 ZIP에서 다시 시험할 때만 필요한 단계 확인.

## 5. 업데이트·7-Zip·저장 기능과 최근 UI 교훈

- 사용자 PC `공식 업데이트 확인` 클릭 무반응 → v643 즉시 '조회 중'/오류/다른 busy 이유를 **같은 패널**에 표시. 사용자에게는 HTTPS TLS 인증서 검증 실패가 실제 관측됨; 우회 금지. 공식 GitHub Nightly fallback은 **최근 아티팩트 ≠ 현재 KR 빌드 호환성 검증**이고 artifact ZIP은 .7z와 다르다.
- 사용자가 .7z 경로를 정확히 입력했는데 `SEVEN_ZIP_REQUIRED`: 파일 오류가 아니라 압축 해제 실행파일 `7z.exe` 탐색 실패. v644는 공식 7-Zip 설치 링크·같은 위치 즉시 진행/실패 안내를 제공. 7z.exe 표준 경로/실설치 확인하고 불필요한 압축 엔진 재개발 금지.
- v645: **`SimC 연결 확인·저장`**은 user action에서 로컬 `simc.exe display_build=2` 1회/20초(비DPS)를 통해 기동과 가능한 출력 빌드를 확인 후 사용자별 경로·revision 보존. **저장 성공 ≠ SHA·Git 공식 출처 독립 증명 ≠ 현재 시즌 READY**. Blizzard/WCL API 키는 기존 Windows Credential Manager에 저장하며 성공 여부와 실제 공급자 API 인증은 분리.
- v646: 시즌 빌드 UI에서 상위 reason → 쉬운 제목/해결 버튼/기술코드 보조로 보여준다. 오류가 확정되지 않으면 무조건 SimC 재설치 지시하지 않는다. 기존 버튼 ID·서버 validation·캐시 연결 유지.
- **v647 완료 (마지막 변경)**: 세 화면 `#view-settings`, `#view-results`, `#view-optimizer`에서 큰 구획에만 약한 separator, 행마다 무한 구분선 제거; 전역 `#notice` 상태 박스는 테두리/진한 음영 대신 **좌측 골드(오류 핑크) 강조선·짧은 텍스트·아주 약한 하이라이트**. DPS/SEM/95%·CHMV·근접 대안·세션 기능 변경 없음. 기술코드를 주제목에서 보조로 내리고 미확정 헤더 문제는 미확정이라고 표시. CSS 룰 중복 `!important` 누적보다 기존 충돌 selector 교정; DOM ID·event·focus/hover/disabled/모바일 보호.
- **최종 v647 배포 근거**: [Windows v181 Actions #44677378569](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44677378569) Python3.12/3.14 각 **패키징5 + 웹·UI·세션 회귀289 PASS**, ZIP 압축 해제/CMD/localhost HTTP 3계획 PASS, 신규 Native0. [ZIP artifact #14603195195](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44677378569/artifacts/14603195195): **283 소스 + manifest1**, 283/283 SHA/size PASS, ZIP SHA256 **`debb25affa7e0539f2197a267deb5286d566b57510cec1d3412e838b28edfdd2`**, 1,500,443 bytes. 최초 v647 구형 밑줄 기대 테스트 FAIL 후 새 디자인 기준에 맞게 교정하고 최종 PASS; **실 사용자 PC 렌더링/미적 인수는 아직 별도**. 현재 GitHub에 문서만 더 쓰는 것을 신규 Windows CI/새 ZIP PASS라고 표시 금지.

## 6. 현재 다음 작업의 단일 우선순위와 중단 조건

**P3 최우선은 새 예산·효과 엔진이 아니라 실제 사용자가 다시 실행할 수 있도록 첫 시즌 원본 차단을 해결하는 것.** 읽기 전용 복원 후 사용자 `진행`이면:
1. 실제 브랜치 HEAD·v647 ZIP·사용자 PC 진단 원본과 최초 실패 코드 재확인. 이미 결과가 있으면 무조건 시즌/Native를 다시 돌리지 않는다.
2. `V229_SET_BONUS_BUILD_OR_HEADER_MISMATCH`가 **실제 원본 set-bonus 헤더 포맷·정확 빌드·rev·소스 경로 중 어디서** 발생하는지 기존 v229의 원본 검증 로직과 사용자 redacted receipt를 비교. **정확한 증거 없는 '최신 SimC 설치하라'를 근본 해결로 단정하지 않는다.**
3. 특정 결함이 코드에 있으면 해당 전달/파싱/오류 분류 한 곳만 수정, 기존 focused QA와 Windows v181 minimal workflow 사용; CI 실패/모의/실 Native 구분. 네트워크/공식 바이너리 부재면 사용자에게 안전한 공식 수동 경로/불확실성 안내. `READY` 우회 금지.
4. 실제 장애가 해결된 것이라면 신규 제품 개발 STOP; 다음 실사용 확인은 검증된 G/J/F/O→대표 프로필→기존 적응형 SimC→DPS/SEM/95%/결과 저장·재열람의 **최초로 미입증된 하나의 연결**만 최소 재현한다.
5. UI v647은 디자인 첫 실사용 수용 대기. 사용자 새 캡처에 기능/가독성 결함이 있으면 *그 부분만* 좁게 고친다. 디자인 새 엔진·패키저 복제 금지.

**비용 우선순위 `STOP → REUSE → CONNECT/FIX → 필요한 최소 EXTEND → 최후 NEW`.** 코드 변경마다 사용자 제품의 어느 버튼/결과와 연결되는지, 이전 증거 재사용 여부, Native·HTTP/DB2·CPU/RAM·I/O·캐시 비용, 실패 근본 원인과 STOP 경계 기록. 기존 v639 Native64, v633 38/38 측정, 역사 26전문화 물리 프로필을 변경마다 다시 실행하지 않는다. 동일 시즌 정적 아이템 캐시는 SimC revision 변경만으로 폐기 금지; DPS 캐시는 SimC 실행 바이너리 SHA+프로필·환경·후보·iterations·조건 identity로 구분.

## 7. 공식 상태·권한·증거 표기

- `15/78 COMPLETE` (제품 구현률이 아님), `full_product_e2e=PENDING` (**v639 대표 한 건 PASS와 양립**), `next_review=B10` (개발 차단 Gate 아님).
- 격리 branch의 코드/문서는 사용자 지시 범위에서 수정 가능하되 **main 병합, v003 immutable 변경, 원본 v016 직접 통합 완료 주장, Project Sources/Instructions UI 실제 적용 주장, Work OS M0/Shared State 공식 승격, 78-element 공식 상태 변경**은 별도 명시 승인/실제 영수증 전 금지. WEQUIP 운영 의존성 금지.
- 주 제품 개발 채팅의 소유권은 단순 handoff 문서 작성으로 이전되지 않는다. 사용자 새 일반 채팅에서 `진행` 지시가 있어야 최소 비용 개발을 시작한다.
- **증거 표현 4종 반드시 구분:** (a) 코드 구현됨, (b) 신규 CI/mock/offline PASS, (c) 기존 Native 실증 재사용, (d) 사용자의 실제 로컬 PC/최종 제품에서 미실측. CI 289 PASS·Windows ZIP SHA ≠ 최신 26개 전문화 실제 DPS/새 시즌 E2E 증명.

## 8. 새 채팅 첫 응답 (정확히 7항목 보고하고 STOP)

새 채팅은 READ-ONLY 독립 조회 뒤 다음 순서로만 보고한다.

1. **현재 HEAD·Actions·최신 v647 ZIP**: SUCCESS/FAIL/CANCEL/SKIP, 최초 실패한 중간 CI와 최종 PASS, 283파일 SHA, Native0과 역사 실증 구분.
2. **제품 목적/설계 비협상사항**: 26 DPS·미래 목표 CHMV 절대 rating·기본334/수동 T·AI 런타임0·SimC/우리 코드 책임 분리.
3. **재사용한 기능과 실증**: ZERO-SOURCE G/J/F/O·v633 38/38 마부·v637/v638 E+ 수동T Native4·v639 ZIP Native64/95%·저장/재열람.
4. **사용자 PC의 현재 첫 장애**: 실제 `V229_SET_BONUS_BUILD_OR_HEADER_MISMATCH`, 연쇄 PENDING, 최신 소스 vs Windows 바이너리, 현재 빌드/리비전/인증 불확실성을 구분.
5. **v642~v647 UI/SimC 설정과 남은 미검증**: TLS fail-closed, 7-Zip 필요, user confirm/save, 원인 해결 버튼, 3화면 시각 개선, PC 미수용/일반 무지원 배포 한계.
6. **다음 최소 비용 작업 딱 하나**: v229 첫 원인 정확히 확인 → 필요 최소 FIX/실사용 재확인 → 충분하면 STOP; Native·DB2·인증·캐시 새 전수 점검 금지.
7. **공식 상태·권한**: `15/78 COMPLETE`/`full_product_e2e=PENDING`/`next_review=B10`, main/v003/v016/Project UI/Work OS/주 채팅 소유권·승격 제한.

**여기서 STOP.** 새 채팅 첫 응답에서 GitHub 파일 수정·Actions 재실행·Native/HTTP/DB2 신규 수집·새 ZIP 제작을 하지 않는다. 사용자가 별도 `진행`이라고 하면 최신 HEAD/첫 장애부터 재확인한 다음 기존 격리 branch에서 최소 수정한다.
