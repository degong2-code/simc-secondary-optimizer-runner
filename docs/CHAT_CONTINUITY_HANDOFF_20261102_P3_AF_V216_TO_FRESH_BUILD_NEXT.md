# SIMC SECONDARY OPTIMIZER — 2026-11-02 P3-AF 새 채팅 인계 정본
## v165~v167 / v191→v211→v213→v196→v216 연속 개발 직후 · 다음은 동일 Build 요청의 실제 신규 수집 및 G/J/F/O 통합

**기준일 2026-11-02 KST · 인계 준비만 수행.** 이 파일은 새 채팅의 **첫 번째 읽기 대상이자 단일 최신 인계 정본**이다. P3-AB/AC/AD/AE 문서는 새 기능의 별도 영수증으로 보존하고, 이 인계에 내용을 중복 복사하지 않는다. GitHub 실제 ref·CURRENT·Actions·Native가 변경되었을 경우 최신 사실을 다시 대조한다. 본 파일이 공식 Work OS 승격 또는 ChatGPT Project Sources UI 적용의 증거는 아니다.

## 0. 실물 확인 시점 및 신분

- Repository: `degong2-code/simc-secondary-optimizer-runner`, **PUBLIC** (2026-11-02 이 인계 작성 전 GitHub API 조회).
- 유일한 격리 개발 브랜치: `probe/chat-cache-v035-20261024`. **인계 직전 실제 HEAD** `c50c6ca9c167a749c5e21cc8c0af63cadcabbe6b` (이 문서·관련 노트 작성으로 HEAD는 달라지므로 **반드시 새로 조회**).
- 보호된 `main` 실제 HEAD `07133e0aaf738d6e4816a6486057b1cd49c018de`; 인계 준비에서 main 변경·merge 없음.
- 마지막 P3-AE 기능 검증 대상 코드 HEAD `19dbb87ce92b47fb615f4b19cbd9113b0dfdf1cc` (문서 커밋보다 앞섬). 최종 문서 HEAD에서 새 코드 재검증을 했다는 뜻이 아니다.
- 별도 Project UI/Instructions 업로드, 원본 `v016_SCENARIO_CONTRACT` 통합, v003 immutable, 공식 Work OS M0·Shared State 승격, MAIN/WORK 소유권 이전은 인계에 포함하거나 완료로 주장하지 않는다. 기존 주 제품 개발 소유권 유지.

## 1. 정확한 읽기 순서 (시간 절감, 중복 최소화)

1. **이 문서 전문**: `docs/CHAT_CONTINUITY_HANDOFF_20261102_P3_AF_V216_TO_FRESH_BUILD_NEXT.md` — 복원 범위·중단 지점·첫 응답 규칙.
2. `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` **파일 최상단 최신 P3-AF/P3-AE/P3-AD/P3-AC/P3-AB 요약**. 이 파일은 장대한 누적 역사 로그이며 오래된 동일 제목이나 과거 HEAD/“미구현” 기록보다 **실제 최신 코드·CI** 우선.
3. `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md` + `docs/DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md` — 유효 승인·엔진 개발 기준.
4. `docs/P3_AA_20261102_SINGLE_ENGINE_FRESH_SEASON_CONTROL_ACCEPTANCE.md` — 사용자 직접 정정한 **제로기존자료/정상 신규 외부 수집 허용/단일 엔진** 최종 시험 계약.
5. `docs/P3_ENVIRONMENT_BUILDER_TARGET_ARCHITECTURE_20261031.md` **§12·§13** + `docs/P3C_V208_START_RECEIPT_AND_WINDOWS_PACKAGE_ACCEPTANCE_20261031.md` **§7** (파일명·경로가 다르면 Git tree로 실제 파일을 찾아 유효한 §7만 읽고 부재를 보고). P3 Architecture는 미래 목표, P3-AE는 실제 현재 코드.
6. **최근 개발 근거는 역순** `docs/P3_AE_20261102_V216_NEW_SEASON_SOURCE_PREFLIGHT_NO_INSTALL.md` → `docs/P3_AD_20261102_V191_V196_FRESH_UNAPPROVED_SOURCE_TO_UI.md` → `docs/P3_AC_20261102_V211_V213_FRESH_SEASON_SIMC_ENCHANT_SOURCE_HANDOFF.md` → `docs/P3_AB_20261102_V165_V167_NEW_SEASON_NO_OLD_JF_GEAR_CHAIN.md`. 필요할 때만 해당 실제 코드·focused tests 및 older v191/v211/v213/v216 receipts 참조.
7. DPS26 교정 `docs/SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.1_DPS_ONLY_SCOPE_CORRECTION_20261029.md`가 repo tree에 없다면 실제 Project 업로드본을 사용자에게 요청하지 말고 **최신 v1.4.3의 26 DPS 정책을 우선**. 과거 v1.4.1에 **27 DPS/증강 포함** 기록이 있어도 과거 문서의 모순이며 복원하지 말 것.
8. 최신 GitHub HEAD·main·visibility, Actions jobs/step logs, Native receipts/artifact identity/만료를 API로 조회해 **아래 스냅샷과 대조**. 필요한 원본 범위만 펼치고 역사를 전수 감사·Native 재실행하지 말 것.

## 2. 최종 제품과 최상위 정책 (구현/승인 혼동 금지)

본 제품은 **미래 목표 ilvl(기본 334) 또는 사용자 수동 최종 T**에 대해 **26개 DPS 전문화만**(증강 기원사·탱커·힐러 제외), SimC DPS를 최대화하는 **치명·가속·특화·유연 절대 rating**을 찾는다. 관측 1순위/DPS/SEM/95% 확정·불확정/실질적으로 다른 근접 대안/비율을 제시한다. 장비 조합·아이템 획득경로 추천이나 시즌 전체 장비 DB를 만들지 않는다. 사용자는 전체 장비를 전수 입력하지 않는다. 대표 일반 장비·무기·주능력치·티어 4pc/SimC 프로필은 엔진 내부 구성, 장신구2·선택 특수장비·장식 최대2·종족·특성·소모품/전투조건만 선택. 기존 적응형 SimC optimizer·캐시·취소·재개·95% 기준을 **그대로 재사용**한다. SimC가 효과/proc/APL/DPS 계산 책임을 진다.

**새 시즌 필수:** 동일 시즌 검증 원본에서 대표 장비/무기·티어와 `G`, 최고 품질 보석 `J`, 영약 `F`, 무기별 적용 기름 `O` 전부 자동 구축. `B=G+J+F`, 공식 `T=B+O`, `c_final=c_base+o`. 수동 최종 T 우선(`B=T-O`), 정확한 선택 특수장비 L은 G에 포함/하한, 영구 마부 E와 기름 O는 중복 가산하지 않음. 장신구 정적 값 미관측 ≠ 0, 제작 50:50 초기 분배를 L로 잠그지 않음. 이전 시즌 J138/F165/79×2/기름당 치명16·가속16·G≈2850을 **새 시즌 값으로 복사하지 않는다**. 다만 과거 G=2847은 실측 장비의 SimC 계산이 틀렸다는 뜻은 아니며 해당 조건의 정확 정적 관측이다.

**최고 품질**: 같은 효과·대상/적용 조건·범위가 증명되고 열등하지 않은 최고 품질만 UI. 영구 마부 포함, **일반 임시 마부 제외**·무기 기름 O 유지. 옴니움 등 확장팩 콘텐츠는 선택형 모듈. **정책 A**: 정확 ID/출처/빌드/적용/SimC 입력/CHMV 소유권 범위가 검증되면 별도 건별 수동 승인 없이 원자적 자동 등록, 미검증 옵션만 보류. SimC 효과 메커니즘 독자 인증 Gate/재구현 금지.

**통제실험 결정은 절대 왜곡 금지:** 최종 인수시험은 **실제 제품과 동일한 하나의 Environment Build 엔진**을, 기존 시즌 DB/수집 스냅샷/캐시/GJFO 참조/과거 Native·Actions 영수증이 입력으로 없는 **빈 상태**에서 돌리고 결과를 봉인한 뒤 역사 DB와 독립 비교한다. **Wago DB2, Blizzard, WCL, 공개 GitHub/Localbots, SimC 등의 정상 신규 외부 다운로드는 허용**한다. 실험 전용 SimC-only 제품 엔진/수집기/프로필 생성기 작성 금지. 과거 `v229~v237` SimC-only는 국소 원본 조사 실험 코드·증거일 뿐 최종 수용시험이 아니다. 시험은 정상 Build 완성 후에만.

## 3. 개발 흐름의 마지막 정확한 접합점 (자연스럽게 이어갈 것)

**P3-AB** 기존 `v165→v166→v167`: 새 Wago 시즌 후보 수집기에서 구시즌 J/F JSON **import-time 자동 참조 제거**; `--fresh-source-only`/명시 `budget_source=None`으로 기어 후보를 계속 만들면서 새 J/F는 PENDING, 이후 모듈에 전달. 같은 시즌 설치 경로는 지연 참조 호환. 새 HTTP 실행은 없었다.

**P3-AC** 기존 `v211→v213`: 새 pinned SimC revision/game build의 exact source SHA/Git blob로 영구 마부 DBC/SpellText/handler 분류, 시즌마다 다른 마부 개수 허용. 이전 고정 38/7967/8025/E Native 승인값 새 시즌 승계 금지. 실제 새 빌드 대신 합성 파일로 계약 시험.

**P3-AD** 기존 `v191→v211→v213→v196` **동일 함수 연속 경로**: `v191`은 신규 시즌에서 `--fresh-budget-pending`으로 J/F 참조·예산 SHA=null, G/B/T=null, `environment_ready=false`; `v213`은 이 정확한 경우만 null budget SHA를 수용하고 새 SimC source-manifest identity를 `v196`에 전달. `v196`은 인증 전 마부 후보를 read-only로 보여주되 사용 가능 선택지 0개, 구시즌 E/J/F 및 승인/라벨 미승계. 이전 정상 설치 시즌은 호환 보존.

**P3-AE — 마지막 실제 코드 변경, 먼저 코드에서 확인할 것:** `runner/v216_environment_build_coordinator.py`에 `preflight_new_season_source(source_catalog_path, expected_game_build, ...)` 추가. 원래 `build_environment`가 신규 v213/v196 후보 출처·SHA/SimC revision을 **외부 요청의 expected_new_season_build**와 비교한다. J/F 참조/예산 SHA가 null이고 승인 0, G/J/F/O/B/T=null, 새 profile 미검증인 경우 `V216_FRESH_SOURCE_PROVENANCE_PASS_GJFO_NOT_READY:<sha>`로 **세션·캐시 쓰기 전에 안전 차단**. 구시즌 7967/38 고정된 `v212`에 후보를 무단 설치하지 않는다. 여기서 멈춰 있으며 **신규 외부 수집이나 실제 GJFO 산출이 연결된 게 아니다**. 새 채팅은 이 차단을 임시 제거하거나 fake READY로 우회하지 않는다. [P3-AE](P3_AE_20261102_V216_NEW_SEASON_SOURCE_PREFLIGHT_NO_INSTALL.md)를 기준으로 결손 의존성을 채워야 한다.

**기존 주요 재사용 지점:** `v160/v161/v163` Wago DB2/season join, `v162` Localbots, `v171` M+ inclusion, `v168` 시즌별 tier anchor input, `v169` 대표 장비, `v189/v190/v191` 소비품/효과 후보, `v211/v213/v196` source/classify/catalog/view, `v220` 정책 A 판정, `v221` gem relation, `v222` GJFO 정합/B/T, `v226~v228` G source/Native 최소 work order, `v212/v216/v217/v218` 환경/단계/영수증/재개, `v098` 대표 프로필, `v093~v095` 적응형 SimC, `v113` 사용 API. **새 optimizer, collector, profile generator, effect evaluator, 다른 Environment Builder 금지**.

## 4. 실제 확인한 영수증 (사용 범위/재사용/만료)

| 구분 | 실제 run 및 조회 | 정확한 의미 |
|---|---|---|
| **최신 P3-AE v216** | [#41408530210](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41408530210), Ubuntu job `125155985187`, Windows `125155985484`, 각 로그 **Ran 320 tests / OK (skipped=2)**, SUCCESS, artifact 없음 | **합성 새 시즌 사전검증·세션 무변경·기존 회귀** PASS. 신규 실제 HTTP 0, Native 0, G/J/F/O 산출/설치 0 |
| **v113 기존 로컬 API** | [#41408530200](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41408530200), Ubuntu/Windows SUCCESS, 각 **181 tests / OK** | 기존 local HTTP/API/세션 경계의 오프라인·loopback 계약; 새 시즌 전체 설치 증명 아님. 테스트에서 의도적으로 BLOCKED 오류 메시지 출력될 수 있음 |
| **P3-AD** | [#41406516956](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41406516956), Ubuntu/Windows 각 **319 tests / OK (skipped=2)** | `v191→v211→v213→v196` 합성 새 빌드 연속 검증, 실제 신규 출처 fetch/Native 아님 |
| **P3-AB** | [#41402618779](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41402618779), Ubuntu/Windows 각 **299 tests / OK (skipped=2)** | 기존 v165→v167 새 기어 원본 의존성 분리 |
| **실물 이전 Native 26 DPS** | [#40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357), native-all-26 SUCCESS; artifact [#12941461212](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357/artifacts/12941461212) **2026-11-05T23:24Z 만료**, 2026-11-02 API 확인 시 **not expired** | 26개 실제 물리 SimC 프로필 수용 smoke. 26개 적응형 최적화 E2E가 아님. 이전 영수증 유효 범위만 재사용 |
| **실물 G=2847** | [#41396545012](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41396545012), 단일 실제 Native SUCCESS, [artifact #13119881002](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41396545012/artifacts/13119881002) **2026-11-05T05:53Z 만료**, 2026-11-02 API not expired | 냉법334 14 비장신구 정적 `484/567/164/1632`=2847 정확 실측. 4 Primal Leywarden + 10 역사 Sinful Gladiator 아이템 혼용의 **시즌 대표 선별** 제한. 계산 오류 아님, 새 시즌 G 확정 아님 |
| **기존 카탈로그 v213** | [#41360273361](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41360273361), artifact [#13104842881](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41360273361/artifacts/13104842881) API not expired, **2027-01-30T23:04Z 만료** | same-build 과거 catalog 검증. 새 시즌 인수시험 입력으로는 금지 |
| **보석 item ↔ property** | [#41362149724](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41362149724), artifact [#13106070626](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41362149724/artifacts/13106070626) API not expired, **2026-11-15T23:27Z 만료** | 75 exact 관계, UI 신규 승인 0. J·소켓/품질/SimC 입력 완결 증명 아님 |
| **기존 Windows 패키지** | [#41361156911](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41361156911), artifact [#13105011863](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41361156911/artifacts/13105011863) API not expired, **2026-11-08T23:15Z 만료** | 베타 패키지/loopback 이전 범위. 실제 신규 시즌 Build/최적화 사용 인수시험 아님 |

위 각 실행/아티팩트는 **API 메타데이터·상태·로그를 이번 인계에서 조회**했다. 역사 ZIP 원본 바이트를 다시 다운로드·재해시하지는 않았으므로 **아티팩트 byte-level 재검증을 새로 했다고 주장하지 않는다**. 동일 시즌 유효한 캐시는 일반 제품에서 재사용하되, **최종 제로기존자료 통제시험에만** 기존 cache/영수증 입력 재사용 금지.

## 5. 미완료/실질적 블로커 (우선순위 순서)

1. **같은 실제 Build 요청에서 정상 신규 원본 fetch 연결 미완료**: `v113 POST /api/v1/environment/build`→`v216.build_environment`는 설치 자료 위주. 승인된 Wago/Blizzard/WCL/GitHub/SimC 수집기 호출, 시즌 판정·원본 SHA·tier anchor 발견·정규화/조인을 **기존 v217 단계 영수증 재사용**으로 연결해야 한다. 소스가 이전 시즌이라고 가정하거나 이전 `data/current_season_*`을 새 시즌 입력으로 주입 금지.
2. **새 시즌 G/J/F/O 숫자 검증/생성 미완료**: G 대표 장비/무기·Tier, 최고 품질 J/F, 기름 O/적용 손/weapon, 영구 E, 선택 L이 새로운 원본 증거로 확정돼야 한다. 기존 `v222` 계약으로 B/T, 수동 T와 하한·중복 방지. 숫자 임의 보간·역사 값을 신규 값으로 복사 금지. Native는 실제 결손 하나에 한정하고 기존 같은 시즌 유효 evidence 우선.
3. **v212/v216의 실제 신규 시즌 설치/프로필 + 정책 A 등록 미완료**: v212 구시즌 `7967/38` 검증과 이미 생성된 v098 profile을 의존. 새로운 same-build source/선택지 validation 및 실제 v220 정책 A 통과 항목만 atomically publish, 새 profile과 manifest/caches/session identity 구성해야 한다. 현재 `V216_FRESH_SOURCE_PROVENANCE_PASS_GJFO_NOT_READY`는 안전 가드다.
4. **완성된 사용자 Build→Start→결과·취소/재개 시험 미완료**: 기존 v093~v095 및 v113 운영코드 재사용. 한 대표 시나리오 E2E 후 26 DPS 증거 범위 활용. 과거 26 physical smoke = 26 adaptive complete 아님.
5. **최종 인수통제시험은 아직 미실시**: 먼저 위 하나의 실제 Build 완성. 완성 후 사전에 이전 자료·캐시·영수증 접근 차단, **정상 신규 HTTP 소스 허용**, 결과 먼저 봉인, 그 뒤 기존 시즌과 독립 비교.

**기타:** 원본 `v016` 파일 바이트/직접 통합 미확인, Project Sources 최신 v1.4.3 실제 UI 등록 미확인. 공식 Work OS 진행을 중단 사유로 이용하지 말 것.

## 6. 다음 실행 묶음 (가장 효율적인 현재 작업)

**다음 P1 작업 묶음: `Build(request) → 신규 시즌 소스 단계 → 기존 v191/v211/v213 후보 → v216 preflight` 하나의 실제 진입점 연결.**

- **A (읽기+계획 / 신규 CI 최소)**: 최신 `v113.plan`, `v216.build_environment`, `v217.execute_stage`, `v161/v163/v162/v171/v168/v189/v190/v191` 입출력을 직접 대조. 이미 구현된 collector/HTTP path/receipt를 재사용하는 **한 개의** stage adapter를 최소 수정 범위로 붙인다. Build의 과거 자료 재사용 mode와 신규 season mode를 명시적으로 구별하되 **서로 다른 엔진으로 분기하지 않는다**.
- **B (작은 수직 오프라인 시험)**: 구 시즌 `data/current_season_*`을 접근 불가로 만들고, **합성 신규 source 모사 입력**에서 같은 normal collector→v191→v211→v213→v216 source preflight까지 진행. 기대: 원본 출처/빌드·SHA 정합/기어·티어/옵션 후보 생성, budget 미확정이면 세션 write 없이 PENDING, **old J/F/E/7967/old gear seed/caches 0 읽기**, 중복 collector/Native 0, fetch stage 동일 identity 재호출 시 무변경.
- **C (작은 실제 외부 소스 시험 — 필요·가용 시)**: 정상 신규 Wago DB2/SimC 등 **실제 HTTP 1회 제한적** 수집, URL·build·SHA 영수증과 실제 API 오류 원문 보존. 새 시즌 자동 G/J/F/O가 검증되기 전에는 설치 READY 금지. CI 기존 320 tests 매 변경마다 전체 무조건 재실행하지 말고 focused + 영향 범위 확인 후 Windows/Ubuntu 종합.
- **D (후속 P2)**: 기존 `v222`에 정확한 G/J/F/O 검증 inputs 제공하고 신규 v212 설치/정책 A 선택지까지 이어간다. 독립 가능 소규모 작업은 한 번에 묶고 큰 의존성은 단계별 seal/check 후 확장.

**더 효율적인 대안:** 새 G·J·F·O별 collector, 별도 Run dispatcher, 새 optimizer·profile generator를 다시 만들지 않는다. 반복 수집/Native 최소화, 기존 stage identity, 작은 SHA/provenance 기록만 보존, large raw Wago CSV는 필요 시 임시 파일만 사용; cache/메모리/I/O/전체 소요시간을 신규 변경마다 정량 또는 제한된 근거로 평가. 성공 영수증의 적용 범위가 변하지 않았으면 반복 실행·재감사 금지.

## 7. 장·단기 로드맵 / 완료 정의

**단기:** P1 **한 Build 요청에서 정상 신규 source fetch + 후보/티어/G 생성 원본 합성** → P2 **같은 시즌의 G/J/F/O·E/L 검증, B/T, 수동 T** → P3 **최고 품질+정책 A 실제 사용자 옵션 자동 발행** → P4 **v212/v216 환경 설치·v098 대표 프로필→기존 적응형 SimC 결과/95%/취소·재개** → P5 **동일 Build의 제로기존자료 통제시험**.

**장기:** 새 확장팩·시즌마다 같은 **범용 환경 구축 엔진이 다시 수집·검증·갱신·실행 연결**을 반복할 수 있도록 한다. 특정 시즌의 ID·고정 38·상수 J/F/O·한 전문화만 되는 분기 늘리기를 엔진 완성으로 착각하지 않는다.

**결과 판정:** 같은 시즌·빌드/소스/SHA 적합한 대표 gear/weapon/tier, G/J/F/O, L/E/O 보존, B/T, 최고품질 목록/SimC 입력 일치, 캐시·버전·프로필, 실패/보류 목록, 실제 Install 후 Start가 일관되기 전에는 `ENVIRONMENT_READY`로 표시하지 않는다. 오프라인 PASS는 실제 외부 source/Native/제품 E2E나 최종 zero-history 시험을 대체하지 않는다.

## 8. 새 채팅 첫 응답 및 권한 경계

**첫 응답은 복원 보고 전용**: GitHub 인계 정본 전체→§1 순서대로 확인, HEAD/main/visibility/Actions/Native/artifact 상태를 직접 대조하고 아래의 항목만 간결한 자연어로 보고: **제품 목적, 엔진 중심 원칙, 최신 완료/미완료, 검증 증거와 범위, 막힌 지점, 간결한 장·단기 로드맵, 가장 효율적인 첫 다음 작업**. 이전 개발 재시작/전체 기록 전수 감사 금지.

**복원 보고를 마친 즉시 멈추고 사용자의 명시적인 “진행”까지 코드 수정·GitHub Actions 실행·Native 시험·새 구현을 시작하지 않는다.** 첫 응답에서 과도한 부수 요청·반복 확인 금지. 인계 문서의 상태 확인을 위한 GitHub 읽기는 허용. `main`, v003 immutable, 원본 v016, Project UI, repository visibility, 공식 Work OS M0/Shared State 또는 주 제품 개발 소유권은 별도 사용자 지시 없이는 변경하지 않는다.

---

## 9. 새 채팅 시작 프롬프트 (복사하여 첫 메시지로 사용)

> 너는 기존 **SIMC SECONDARY OPTIMIZER** 프로젝트의 개발을 이어받는다. 프로젝트를 새로 시작하거나 과거 개발을 반복하지 마라.
>
> 먼저 `degong2-code/simc-secondary-optimizer-runner` 브랜치 `probe/chat-cache-v035-20261024`의 **`docs/CHAT_CONTINUITY_HANDOFF_20261102_P3_AF_V216_TO_FRESH_BUILD_NEXT.md` 전체**를 읽어라. §1의 순서대로 CURRENT, 최신 승인 개발자 노트 v1.4.3, 엔진 실행 보충, P3-AA, P3 아키텍처 §12·13, P3-AE/AD/AC/AB 및 관련 인수 기준을 확인하라. GitHub HEAD/main/visibility, Actions jobs/logs, Native 영수증과 artifact 만료를 실제 조회하고 기록과 대조하라. 오래된 누적 CURRENT 항목을 최신 완료 상태로 오인하지 마라.
>
> **장기 목표는 특정 기능 몇 개를 따로 개발하는 일이 아니라, 새 시즌마다 해당 기능을 반복 구현·갱신할 수 있는 범용 “프로그램 환경 DB 구축 엔진”을 만드는 일이다. 모든 작업에서 이 목적에 부합하는지 자가검증하라.** 정상 제품 Build 요청 하나가 원본 수집→대표 일반 장비/무기·티어→G/J/F/O→B/T→검증된 최고품질 옵션/정책 A 등록→환경 설치·SimC 프로필→기존 적응형 최적화로 이어져야 한다. 26 DPS(증강·탱커·힐러 제외), 목표 ilvl334 또는 사용자 최종 T, 절대 CHMV rating/DPS/SEM/95%/근접 대안, SimC 효과/proc/APL 책임, E/L/O 중복 방지, 기존 캐시/취소·재개를 보존한다.
>
> 현재까지 **v165→v167의 과거 J/F import 분리, v191→v211→v213→v196의 신규 시즌 미승인 카탈로그 연속 경로, 마지막 v216의 원본 SHA·빌드·예산 미확정 사전검증**이 구현되어 있다. 마지막 실제 오프라인 PASS는 [#41408530210](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41408530210) Ubuntu/Windows 각 320 tests, 2 skipped; 실제 신규 HTTP/Native·G/J/F/O 확정·Build 환경 설치는 **아직 미완료**이다. v216의 `V216_FRESH_SOURCE_PROVENANCE_PASS_GJFO_NOT_READY` 차단은 올바른 안전 장치다.
>
> 사용자가 요구한 미래 **제로기존자료 통제시험**은 완성된 **같은 정상 제품 엔진**을 기존 시즌 DB·수집 스냅샷·캐시·과거 Native 증거 없이 빈 상태에서 실행하되, **Wago DB2/Blizzard/WCL/공개 GitHub/SimC 등 정상 신규 외부 수집은 모두 허용**한 뒤 결과 봉인·독립 비교하는 시험이다. SimC-only 별도 최종 엔진/수집기 개발은 금지한다.
>
> **다음 개발은 같은 v216 Build 요청 안에 기존 승인된 외부 원본 신규 수집과 tier anchor/소스 정규화·v191-v213, 기존 v217 재개·캐시·SHA stage를 연결하는 최소 수직 작업부터** 진행한다. 기존 v222 G/J/F/O 회계, v220 정책 A, v212 manifest, v098 profile, v093~v095 optimizer를 재사용하고 중복 구현하지 않는다. **독립 작업은 효율적으로 묶고**, 큰 작업은 검증 가능한 패치로 구분한다. 동일 검증 계약·완료 판정과 과거 유효 Native/CI를 재사용하며 이유 없는 Native 전수 반복·새 Gate·재감사를 하지 않는다. 모든 수정에서 Native/HTTP 호출, 실행시간, 중복 수집, 캐시, 메모리, I/O 및 구조 단순화를 검토하라. 구현·신규 PASS·역사 증거·미구현·미승격을 분리 보고하라.
>
> `main`, v003 immutable, 원본 v016, Project Sources/Instructions UI, repo visibility, 공식 Work OS 상태 및 제품 개발 소유권은 사용자 별도 지시 없이 변경하지 마라.
>
> **첫 응답에서는 복원한 목적·현재 HEAD와 개발 상태·검증·완료/미완료·블로커·간결한 장·단기 로드맵·가장 효율적인 다음 작업만 자연어로 보고하라. 복원 보고 직후 반드시 중단하고, 내가 “진행”이라고 하기 전에는 코드 수정·Actions 실행·Native 시험을 시작하지 마라.**
