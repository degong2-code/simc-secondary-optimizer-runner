# v383 — A10/A11/G2 실제 Windows 원본 영수증 재조회·범위 한정 승격

- **Capability:** `SOURCE.SEAL`, `ENVIRONMENT.SEASON`, `ENVIRONMENT.WEB`, `BUDGET.GJFO`, `DEV.CONTINUITY`; 78요소 **A10·A11·G2**. [운영 헌장](../OPERATING_CHARTER_FUTURE_SEASONS_AND_EVIDENCE_20261113.md).
- **Keywords:** v383, evidence reuse, source compiler, original sealed receipt, installed SHA, current vs historical scope, ZERO-INSTALL, Native ZIP SHA, GJFO.
- **Prior evidence:** GitHub Actions [v337 #43000049793](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43000049793), [v343 #43049564271](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43049564271), [v344 #43114134208](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43114134208). 이번 재조회에서 세 Job `conclusion=success` 확인; GitHub의 원본 artifact **#13868303468 (v343)**, **#13897178782 (v344)**, **#13845203640 (v337)** 다시 다운로드·내부 JSON/ZIP 확인.
- **Decision:** **REUSE / SCOPED**. v274의 아홉 **완전 카탈로그** 입력을 J/F/O 숫자 검증으로 재분류하거나 기존 v216→v222→v212 인증을 우회하지 않는다. 현재 사용자 Windows의 `source_compilation.missing`과 `required_core_source_owner_report`를 아직 확보하지 못했으므로 현재 발생한 결함·최초 차단 필드가 있다고 주장하지 않는다.
- **Changes:** 제품 코드·API/UI·캐시 변경 **0**. 해당 역사 실행의 준비 판정을 [78개 원장](../ENVIRONMENT_READINESS_78_ELEMENT_TRACKER_20261113.md) A10/A11/G2에 **READY_SCOPED: HISTORICAL_70783_EXECUTION_ONLY**로 기록하고 전체 현재 HEAD·새 시즌·USER 변경 선택지의 READY와 분리.
- **Verification / A10:** v344 실제 Chrome 원본 UI 진단에 `원본 EXECUTED_AND_SEALED`, `컴파일 FRESH_V191_V211_V213_COMPILED_UNADMITTED` 확인. 원본 컴파일 완성 사실은 역사 70783 **한 요청**의 단계 관측이며 현재 다른 요청 `missing=[]`이라는 증거가 아님. v343/v344 실제 v212 설치도 컴파일된 catalog 소비 확인. v191 기록 gear209/tier65/enchant772는 전체 아이템 인증이 아님.
- **Verification / A11:** v344 실제 원본 UI의 `EXECUTED_AND_SEALED`와 v212 설치 manifest SHA `278d3c52d4c9c272d8d2c89d7b02cff4abe05db1639bde80b58b14d99f4f4294`; v343 별도 설치 manifest `5d655836c6f69382a1ca81d72346fa5d71dc78eb2ae029843b49dea532693a02`. 두 manifest는 **서로 다른 실행의 원본**이며 동일해야 한다는 가정 금지. v337의 같은 설치 root 재실행 Native0/API0 재사용 영수증은 같은 빌드 조건만 인정. 각각의 개별 원본 stage 영수증 바이트/전체 source_owner 보고서는 압축 요약에 없어 새로 확인한 것으로 주장하지 않는다.
- **Verification / G2:** 2026-11-11~12 Windows 빌드 `12.1.5.70783`, ilvl334, survival hunter, 일반보석4, 미사용 O0. v343/v344 모두 `G2850,J92,F165,O0,B=T3107`, `environment_installed=true`, `environment_ready=true`, 환경 Native3. v343 FastAPI DPS12, v344 Chrome→SimC DPS64·중단/재시작·재개 완료; v344 `original_environment_report.status=FRESH_WAGO_DB2_COLLECTED_MORE_SOURCES_PENDING`는 `environment_ready=true`인 설치 결과와 **다른 진단 차원**이므로 새 실패 판정이 아님.
- **ZIP integrity:** v343 내부 `V343_NATIVE_INPUT_JSON2_RECEIPT.zip` SHA256 `efb6d13d87ba945d5415b6d8f83e96be8ff7d7245f78652b00aa0f1d516dc849` = 원본 compact의 `raw_evidence_sha256`. v344 내부 `V344_NATIVE64_INPUT_JSON2_RECEIPTS.zip` SHA256 `9dc7f1f310c1fef3db486d1e528993c2f23a3eec137afe113036b9d9c4f44bd7` = compact `native_original_zip_sha256`. 유효한 원본 ZIP을 **읽고 해시 대조**했으며 신규 SimC 실행은 아님.
- **Remaining / first exact blocker:** 현재 Windows 사용자 요청의 `web_environment_scope.auto_initial_core_build_requested`, `source_compilation.status/missing`, `zero_history_build.required_core_source_owner_report`, `native_G_status`, `versioned_environment_installed`는 이전 v163 후보 JSON/역사 compact로 확정 불가. 새 요청의 원본 영수증을 얻기 전 실제 missing 키, 선택하지 않은 컴파일 전용 파일의 BASE 차단 여부, 새 USER 양성 설치를 가정하지 않는다. v381 이후 최신 HEAD 실 Windows Native/Actions 통합 시험 **미실시**.
- **Efficiency:** 신규 Native **0**, 새 수집 HTTP/DB2 **0**, Actions 실행 **0**, 소스 컴파일 재실행 **0**, 기존 GitHub artifact **3개 조회/다운로드 및 ZIP 해시 대조만**. 기존 캐시·바이너리·게임 원본·사용자 비밀정보/세션 무변경.

## Appendix: 세 항목 READY_SCOPED 판정 재현 절차와 추적 키 (2026-11-13)

> 이번에는 새 Native가 아니라 **이미 저장된 기존 Actions artifact의 바이트를 다시 읽어** 무엇을 입증하는지 기록했다. 아래 SHA는 각각 무엇의 SHA인지 구분한다. 과거 설치 manifest SHA, 내부 ZIP SHA, SimC binary SHA를 서로 같은 것으로 취급하지 않는다. 실제 78개 완료/최종 ZERO-SOURCE 요구는 [운영 헌장 §11](../OPERATING_CHARTER_FUTURE_SEASONS_AND_EVIDENCE_20261113.md) 참고.

### 1. 이번에 실제 수행한 판정 순서

1. **대상·조건 지정:** A10=원본 통합 컴파일, A11=원본 단계 봉인/영수증, G2=기본 환경 READY. 사용 범위는 KR Retail `12.1.5.70783`, 목표 ilvl `334`, 생존 사냥꾼, 일반 보석4, 기름 미사용 O0. v343 실제 시험 HEAD `420652d58c6d71e63e08a9c7f583a40f7562ee89`, v344 HEAD `d8620d733140b148deb534975485f45ee22cf118`; **이번 문서 수정 HEAD나 최신 프로그램 Native 재시험이 아니다**.
2. **독립 Jobs 조회:** v337 run `43000049793`/job `130453646118`, v343 run `43049564271`/job `130622638360`, v344 run `43114134208`/job `130837588866`에서 각각 `success`를 확인하고 원본 로그의 `V337_REAL_COLD_START_RECEIPT`, `V343_WINDOWS_70783_NATIVE`, `V344_REAL_WIN_BROWSER_NATIVE64` 최종 JSON 줄을 대조했다.
3. **기존 artifact 원본 재확인:** v337 artifact `13845203640`, v343 `13868303468`, v344 `13897178782`를 읽었다. v337 내부 `p1_v337_zero_history_environment_locale_receipt.json` SHA256 `1033a882e1d0a5f106cf53601335d897fa0c1d5be6172a139d75a836898c0140`. v343 내부 `V343_WINDOWS_70783_COMPACT.json` SHA256 `9ceec67cf25361dcde0a6ce11f68d39075dc482bf2b0231881c5572ccf4da5bf`, v344 내부 `V344_WINDOWS_REAL_BROWSER64_COMPACT.json` SHA256 `98ffc9ee697cd93a2db39167e2730ee01e7435813906c8c19885cedc7c31fb65`. ZIP 파일의 바이트 SHA가 아니라 **해당 artifact 안의 파일 바이트 SHA**다.
4. **Native 원본 중첩 ZIP 해시:** v343 `V343_NATIVE_INPUT_JSON2_RECEIPT.zip` SHA256 `efb6d13d87ba945d5415b6d8f83e96be8ff7d7245f78652b00aa0f1d516dc849`는 compact의 `raw_evidence_sha256`과 정확히 일치, 파일 목록 40개(케이스별 input/receipt/result ×12+세션4). v344 `V344_NATIVE64_INPUT_JSON2_RECEIPTS.zip` SHA256 `9dc7f1f310c1fef3db486d1e528993c2f23a3eec137afe113036b9d9c4f44bd7`는 compact `native_original_zip_sha256`과 일치, 파일 목록 196개(케이스별 input/receipt/result ×64+세션4). **중첩 ZIP 개별 JSON2의 각 계산값을 이번에 새로 Native 재평가했다는 뜻은 아니다.**
5. **단계 구분 후 상태 판정:** v344 실제 제품 `season_build_ui_stage`에는 `원본 EXECUTED_AND_SEALED`, `컴파일 FRESH_V191_V211_V213_COMPILED_UNADMITTED`가 기록되어 있다. 동일 v344 compact `original_environment_report.environment_ready=true`, `environment_installed=true`, `installed_manifest_sha256=278d3c52d4c9c272d8d2c89d7b02cff4abe05db1639bde80b58b14d99f4f4294` 및 환경 Native3. v343 별도 compact도 `environment_ready=true`, 설치 SHA `5d655836c6f69382a1ca81d72346fa5d71dc78eb2ae029843b49dea532693a02` 및 Native3. **소스 진단의 PENDING 문자열과 설치 READY를 별도 축으로 취급**한다.
6. **범위 판정:** 이 실행 조건에서만 A10/A11/G2의 역사적 `READY_SCOPED`로 등록. 나머지 75항목, 현재 사용자 최신 Windows, 새 시즌의 실제 소스, 선택된 다른 소켓/영약/기름은 `PENDING_SCOPE` 또는 별도 인수 대상으로 남긴다.

### 2. 항목별 결정 논리와 아직 없는 증거

| ID | 실제 성공에서 확인된 의존 경계 | 해당 범위 READY를 내린 이유 | 지금 확인하지 않은 항목 |
|---|---|---|---|
| **A10** | v344 원본 봉인 → `v191/v211/v213 COMPILED_UNADMITTED` → v212 설치 경유 | 실제 성공 사용자 경로에서 통합 카탈로그가 완성되어 소비되었음을 입증 | 원본 9개 개별 파일 SHA 전체 대사, 현재 요청의 `source_compilation.missing`, 새 빌드 카탈로그 완성 |
| **A11** | v344 `EXECUTED_AND_SEALED`; v337 동 root 재실행 Native0·API0; v343/v344 각각 정확 설치 SHA | 원본 단계 봉인·동일 조건 재사용·서로 별개 설치 ID가 기록된 실제 경로 | 모든 `v217` 개별 원본 stage 영수증 바이트·현재 사용자 source_owner 원본 전체·현 HEAD 재실행 |
| **G2** | G2850/J92/F165/O0, `B=T=3107`, v212 설치·환경 Native3, v343 DPS12/v344 Chrome DPS64 | 기본 70783 조건에서 실제 G/J/F/O 회계와 설치·후속 SimC 실행 성공 | 현재 70783 이후 빌드, 다른 ilvl/전문화/USER 변형, 새 시즌 ZERO-SOURCE, 현재 HEAD 신규 Windows 통합 |

공통 고정 실행자: Windows Actions, SimC 바이너리 SHA256 `1fc927d2be7f1b6064c75f004b5b22245b064a6b3e56e572af4048ba822a986d`, SimC revision `de11f57df75dda668bae6ac7043a43b98831fa96`. 본인 PC 실행이나 미래 시즌 실증이 아니다.

### 3. 최종 ZERO-SOURCE 실패 시 이번 성공과 대조할 순서

- **A10:** `source_compilation.status/missing`와 v274 아홉 입력의 실제 원본 공급자 → 기존 v275/v241/컴파일 과정. 컴파일에만 필요한 선택 카탈로그 원본과 G/J/F/O 숫자 근거를 구별한다.
- **A11:** stage `status/receipt_sha256`, source season/build/revision, 원본 파일 SHA/매니페스트 → 처음 불일치한 stage. 현 SHA와 v343/v344 서로 다른 설치 SHA가 다르다는 사실만으로 오류가 아니다.
- **G2:** 선택한 시즌·ilvl·보석/영약/기름 → 각 source owner `source_verification` → v222 B/T → v212 `verified_environment_install`과 정확 설치 SHA. 다른 시즌 수치가 3107이 아니어도 자동 실패로 판정하지 않으며 **그 시즌의 독립 근거와 회계가 맞는지** 검사한다.
- **그 이후:** USER 변형의 SHA 및 v098 프로필 → SimC JSON2 → v290/v291/v293 Native/DPS/SEM/95%·결과·캐시. 이 영역은 A10/A11/G2 세 항목의 역사적 `READY_SCOPED`를 근거로 자동 PASS하지 않는다.

**최종 수락 구분:** `TRACKER_78_APPLICABLE_SCOPES_RECONCILED` ≠ `CURRENT_SEASON_ZERO_SOURCE_USER_E2E_PASS`. 현재 두 최종 상태는 모두 별도 새 실증이 필요하며, v383은 **그 어느 최종 Gate도 통과시킨 작업이 아니다**.

