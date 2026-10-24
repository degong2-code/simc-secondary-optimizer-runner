# SIMC SECONDARY OPTIMIZER — Chat↔GitHub Actions 자동 실행 운영 기록 v1.0

- **작성 기준일:** 2026-10-24 (KST)
- **문서 성격:** 일반 제품 개발/시험용 **운영환경 검증 기록 및 작업 지침**. 새로운 제품 요구사항이나 Work OS 상태 승격 문서가 아님.
- **대상:** GitHub 비공개 저장소 \`degong2-code/simc-secondary-optimizer-runner\`
- **근거:** 2026-10-24에 실제 수행한 v033→v035 GitHub Actions 실행·영수증·잡 로그·원본 ZIP 검증
- **상태:** **GitHub 직접 읽기/쓰기, push-trigger 실행, 실행 ID 조회, Artifact 직접 다운로드, 바이너리 캐시 MISS→HIT 실측 PASS**. 단, 현행 자동화·캐시는 **격리 시험 브랜치**에 있고 기본 브랜치 \`main\`의 일상적 생산 워크플로로 승격되지 않음.
- **권한:** 기존 주 제품 개발 채팅이 일반 제품 구현·시험을 소유. 공식 Work OS M0·Project Instructions·Project Sources·CURRENT·Shared State의 변경 또는 승격은 기존 MAIN 승인 계약에 따름.

## 1. 이번에 실증된 혁신

**사용자의 반복 수작업 없이 일반 Chat만으로 다음 순환이 가능함을 실측했다.**

\`\`\`text
일반 Chat: 제품 구현·검증·GitHub 반영 요청 준비
    ↓
인증된 GitHub 연결: 브랜치/파일 생성·수정·재조회
    ↓
GitHub Actions: 제한된 push 트리거로 실제 Linux SimC 실행
    ↓
GitHub: 실행 ID/잡 상태/JSON2/로그 Artifact
    ↓
일반 Chat: GitHub API로 실행 결과 조회 및 Artifact 직접 다운로드
    ↓
일반 Chat: SHA/JSON2/CHMV·통계 검증 → 다음 제품 버전
\`\`\`

- 성공 시험에서 **GitHub Desktop, Windows PowerShell, 사용자 ZIP 다운로드·재첨부, Work, Codex 사용은 모두 0회**.
- 연결된 GitHub 도구에서 \`create_branch\`, \`create_file\`, \`update_file\`, \`fetch_file\`, \`fetch\`, \`fetch_workflow_run_jobs\`, \`fetch_workflow_run_artifacts\`, \`download_workflow_artifact\` 사용 가능함을 관측했다. **실제 호출 성공과 호출 가능 목록을 구분한다.**
- **직접 신규 \`workflow_dispatch\`를 발생시키는 도구는 이번 도구 목록에서 확인되지 않았음.** 해결책으로 특정 브랜치의 지정된 요청 파일에 대한 \`push\`를 Actions 트리거로 사용했다.
- **Chat의 GitHub 권한은 연결/인증/제품 도구 제공 상태에 의존**한다. 새 채팅·환경에서도 반드시 작은 읽기 및 쓰기 검사를 먼저 실시한다. 설치/로그인을 완료했다는 사실만으로 현재 요청의 쓰기 권한을 가정하지 않는다.
- 일반 Chat의 원본 ZIP을 Work의 파일 표면에 자동 첨부하는 별도 메커니즘은 **확인되지 않았다**. GitHub Artifact를 일반 Chat이 직접 가져올 수 있게 되어 그 경로를 우회함.

## 2. 보존해야 할 실측 증거

| 단계 | GitHub Run ID | 브랜치 | 실측 판정 | 핵심 |
| --- | --- | --- | --- | --- |
| v033 원격 호환성 | [40087963873](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40087963873) | \`main\` | PASS | 수동 \`workflow_dispatch\`; 고정 SimC Linux 빌드·치명타/가속 룬 JSON2 |
| v034 Chat 자동 시작 | [40093110367](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40093110367) | \`probe/chat-auto-run-20261024\` | PASS | 일반 Chat의 요청 파일 push → 자동 실행 → Run ID 기록 → Artifact 직접 회수 |
| v035 캐시 최초 생성 | [40094860925](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40094860925) | \`probe/chat-cache-v035-20261024\` | PASS | 캐시 MISS; 소스 빌드 후 캐시 저장 |
| v035 캐시 재사용 | [40095632889](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40095632889) | \`probe/chat-cache-v035-20261024\` | PASS | 캐시 HIT; 소스 다운로드·빌드 도구 설치·C++ 빌드 단계 생략; SimC 실제 실행 |

관련 실패도 **삭제하거나 성공으로 바꾸지 않는다**:

- v034 최초 두 push: 워크플로 YAML 키가 \`oon:\`, \`oncurrency:\`로 손상되어 실패. 수정 뒤 성공. **YAML 문자열 조립 시 원본/수정본 인덱스를 혼용하지 말 것.**
- v035 최초 1차 요청 [40094634175](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40094634175): \`UNAPPROVED_CHANGESET\` 실패. \`actions/checkout\` 기본 얕은 체크아웃에 부모 커밋이 없어 \`git diff-tree\`를 통한 엄격한 1파일 검증이 실패. \`fetch-depth: 2\`로 교정한 후 1차 성공.
- 오류를 발견하면 원인을 잡 로그에서 확인하고 최소 변경만 교정. 동일 작업 무분별 재시도 금지.

### 2.1 정확한 v035 캐시 성능

- 고정 SimC 소스 커밋: \`7bc10711b5a4514066fa402ca0a71c9ba4b7c9dd\` (SimulationCraft 1210-01)
- Linux: \`ubuntu-24.04\`, CLI-only Release, \`BUILD_GUI=OFF\`, \`SC_NO_NETWORKING=ON\`, 병렬 빌드 2
- 바이너리 SHA256 (1·2차 동일): \`64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e\`
- 바이너리 원본: 156,439,344 bytes; GitHub 로그상 압축 캐시 약 19MB
- 1차 캐시 MISS, \`Built target simc\`, 종료 시 \`Cache saved with key\` 확인.
- 2차 캐시 HIT, \`Cache restored successfully\`, 설치·소스 fetch·컴파일 세 단계 \`skipped\`, 검증된 SHA의 SimC로 JSON2 생성 PASS.
- **Runner 실제 로그 기준:** 1차 약 9분 47초, 2차 약 8.7초, **약 67배 단축**. 단, GitHub 웹상 전체 Run 기준은 실행 배정·큐·완료 기록을 포함해 2차에도 약 16초가 걸렸으므로 **사용자 체감 시간을 8.7초로 보장하지 않는다**.
- v035는 **같은 치명타 룬, 60 iterations, 고정 CHMV (600/1140/1115/329), 합계 3184**의 정상 실행을 검증한 것으로 **최적 CHMV를 발견했다는 의미가 아니다**. DPS 샘플 차이로 룬 우열 또는 CHMV 최적성을 단정 금지.
- \`actions/cache@v4\`의 Node.js 20 지원 종료 경고가 남음. 차기 운영 전 Node.js 24 호환되는 새 캐시 액션으로 업데이트하고 검증; 경고를 계산 오류로 혼동하지 않는다.

### 2.2 GitHub 저장 위치/현행 상태

- **기본 브랜치 \`main\`**: \`.github/workflows/remote-simc-v033.yml\` (**수동 실행용 v033**, 직접 읽은 blob SHA \`e852231748f85e890090bb356bf77e36f198bfe1\`). 이후의 v034/v035 자동화가 이 파일을 대체하거나 \`main\`에 병합된 것은 **아니다**.
- **시험 브랜치 \`probe/chat-auto-run-20261024\`**: \`.github/workflows/v034_chat_auto_trigger.yml\` 및 \`integration_probes/requests/v034_native_one_shot.json\`.
- **시험 브랜치 \`probe/chat-cache-v035-20261024\`**: \`.github/workflows/v035_cache_native_probe.yml\`, \`integration_probes/requests/v035_cache_round_1.json\`, \`...round_2.json\`, 실행 ID 파일 \`integration_probes/results/v035_round_1.json\` 및 \`...round_2.json\`.
- v035 캐시는 **해당 브랜치의 Actions 캐시 범위**에 있으므로 \`main\`이나 형제 브랜치가 곧바로 캐시 HIT라고 가정하면 안 된다.
- **이 MD 파일은 GitHub 제품 실행환경의 운영 기록**이지, \`SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.0.md\` 또는 Work OS의 공식 상태 파일이 아니다.

## 3. 앞으로의 표준 개발 루프

1. **일반 Chat에서 제품을 개발한다.** 제품 설계 기준, 기존 승인 정책, v032 옴니움 룬 기본값(치명타), CHMV 예산·고정 하한을 지킨다. 로컬 오프라인 테스트와 코드 리뷰를 먼저 시행한다. 제품 조건이 바뀌지 않았다면 기존 증거 재사용.
2. **변경 파일을 최소 단위로 준비한다.** 파일 경로·기준 브랜치/커밋·실행 허용 범위·SHA256/Manifest·예상 결과·STOP 조건을 고정한다. 공식 Work OS 문서와 별개로 관리한다.
3. **GitHub 최소 권한으로 반영한다.** \`fetch_file\`로 현행 blob SHA를 확인한 다음 \`create_branch\` 또는 \`create_file/update_file\`을 사용한다. 제품 안정 버전은 보전하고, 처음에는 별도 브랜치/짧은 시험으로 확인한다. 동시에 다수의 같은 파일에 쓰지 않는다.
4. **Actions는 명시적으로 좁힌 \`push\` 이벤트로 시작한다.** YAML \`on.push.branches\` + \`paths\` 두 필터, 요청 JSON의 schema·authorization·SimC commit·룬·iterations·변경 파일 수 검사를 함께 수행한다. 외부의 임의 PR, Issue, 댓글에 응답해 무제한 컴파일/실행하지 않는다.
5. **실행 ID를 찾는다.** 실행이 성공적으로 시작된 뒤 Actions가 GitHub에 기록한 \`integration_probes/results/*\`의 Run ID를 \`fetch_file\`로 읽거나 \`fetch\`로 GitHub GET \`/actions/runs?branch=...&per_page=...\`에서 정확한 head SHA를 검색한다. ID를 추측하지 않는다.
6. **실제 완료를 확인한다.** \`fetch_workflow_run_jobs\`에서 각 step의 결과·전체 conclusion을 확인하고, 실패하면 \`fetch_workflow_job_logs\`로 근거를 읽는다. 요청 접수·run pointer 생성·job 시작만으로 SimC PASS라고 말하지 않는다.
7. **Artifact를 직접 회수한다.** \`fetch_workflow_run_artifacts\`에서 **해당 Run ID**의 정확한 \`artifact_id\`와 이름을 확인하고 \`download_workflow_artifact(repo_full_name, artifact_id, file_name)\`로 다운로드한다. **Run ID와 Artifact ID는 다르다.** 이미 있던 Chat ZIP을 신규 GitHub 다운로드라고 가장하지 않는다.
8. **실행 결과를 독립 검증한다.** ZIP CRC, 실제 파일 크기·SHA256, JSON2 출처, 입력 해시, SimC source/binary identity, CHMV 절댓 rating 합계·하한, 장비/티어/룬/소모품·버프, DPS 표본·오차, 실행 회차와 캐시 HIT/MISS를 대조한다. 오류를 숨기지 않는다.
9. **다음 버전을 설계한다.** 안정적인 성능 개선이 실측된 경우에만 성공으로 승격한다. 사용자가 직접 반복해서 ZIP을 옮기거나 PowerShell을 수행할 필요가 없는지 함께 평가한다.

## 4. 필수 안전장치 및 한계

### 권한·격리

- \`main\` 자동 갱신·공식 Work OS M0 실행·Project Instructions/Sources/CURRENT/Shared State 변경 및 승격은 **구분된 권한 계약**에 따라 수행. 제품 개발의 일반 승인과 공식 운영 Gate 승인 혼동 금지.
- 기존 immutable v003 보호, WEQUIP에 운영 authority 또는 지속적 runtime dependency 부여 금지.
- 실험은 브랜치/경로 제한, bounded 반복·제한된 병렬성·시간 제한, 요청 파일 단발성 검증으로 비용 폭증 방지.
- 워크플로가 GitHub의 \`GITHUB_TOKEN\`으로 결과 pointer를 push할 때 그 push는 통상 새 Actions 워크플로를 다시 트리거하지 않음. 다만 \`[skip ci]\`도 쓰고, 브랜치·경로·실행 횟수 제한을 함께 둔다. **완전한 트리거 방지책을 한 가지에만 의존하지 않는다.**
- \`.env\`, OAuth 토큰, PAT, 임시 서명 다운로드 URL, 사용자 비밀 또는 로컬 개인 경로를 커밋·로그·Artifact·캐시에 포함하지 않는다. 비공개 저장소여도 동일하다.
- 저장소 권한과 토큰 권한은 필요 최소화. v035 테스트의 \`contents: write\`는 **run pointer 커밋용**이다. 후속 제품 워크플로에서는 필요한 job에만 좁힌 권한을 제공하거나 pointer 없이 GitHub API 검색을 사용하는 구조를 우선 검토.

### 캐시 정확도·비용

- **두 캐시를 구별**한다: (A) Linux SimC **실행 바이너리** 캐시 = 컴파일 생략, (B) 완전히 동일한 **시뮬레이션 결과** 캐시 = 실제 SimC 재실행 생략. v035가 검증한 것은 **(A)뿐**.
- 바이너리 캐시는 SimC 전체 커밋, OS/아키텍처, 컴파일러와 빌드 옵션, 데이터·링크 의존성을 식별해야 한다. **현 v035 키는 컴파일러 세부 버전까지 묶는 완전한 생산형 키가 아니다.** 타 브랜치/환경 이동 시 재검증 필요.
- SHA256 검증은 **바이너리 바이트 동일성 확인**이지 출처의 완전한 보안 증명이 아니다. 검증된 빌드 경로로 생성하고 비신뢰 PR 캐시와 분리한다. 캐시가 사라지거나 무효화되면 다시 빌드할 수 있어야 한다.
- 캐시가 영구 저장되는 것으로 가정 금지. GitHub의 브랜치별 접근 범위, 저장 용량, 캐시 회수 정책, 시간 경과 후 퇴출을 고려한다.
- **Artifact는 실행 증거 보존용이지 영구 캐시가 아니다.** 현 테스트 워크플로는 보존 기간 \`retention-days: 7\`. 장기 증거는 별도 승인된 관리 공간으로 옮기는 방식 검토.
- Github Actions의 무료 실행시간/스토리지/예산은 요금제와 당시 정책에 따라 달라진다. 대량 후보 탐색 전 현재 사용량을 확인하고 bounded budget으로 시작.
- 새 런을 무조건 늘리는 것보다 **하나의 Actions job에서 여러 CHMV 후보를 일괄 계산**하고 진척·체크포인트·취소·재개를 제공하는 방향을 우선한다.
- 로컬 SimC가 실제로 수 초이고 외부 GitHub 단계가 불리한 경우 로컬 실행 방식은 계속 유효한 **fallback**이다. 클라우드 환경을 유일한 운영 의존성으로 만들지 않는다.

### 제품 정책·검증 수준

- SIMC SECONDARY OPTIMIZER의 목적은 장비 추천이 아닌 **DPS 최대화 CHMV 네 가지 절대 rating 최적화**. 탱커/힐러 전문화도 목적함수는 DPS. 특수 장비 고정 스탯·장신구 정책·기본 4세트·전투 조건·영약·기름 정책을 제품 승인 없이 바꾸지 않는다.
- \`Developer_Notes_v1.0.md\`를 사용자 승인 설계 기준으로 취급하고, 후속 사용자 승인 변경사항과 구분한다. \`v1.1_CANDIDATE\`를 승인된 새 기준 문서로 자동 승격하지 않는다.
- 제품 최신 보고 상태와 공식 \`M0_STAT_INJECTION_FEASIBILITY\` 운영 Gate는 독립이다. 이번 클라우드 일반 제품 시험 성공이 공식 M0 PASS를 뜻하지 않는다.
- 고정 프로필의 소수 iterations에서 우수한 DPS가 관측됐더라도 통계 오차 내 차이를 승패/최적화 완료로 선언 금지. 일반 제품 v032 적응형 엔진과 이후 CHMV 최적 실측은 **별도 검증 단계**.
- SimC 버전 동일, 코드 검사 PASS, GitHub job SUCCESS, 실제 DPS 계산 성공, CHMV/장비/버프 귀속 PASS, 적응형 탐색 성능 검증, 제품 완성은 **서로 다른 검증 상태**다.

## 5. 후속 개발 순서 (현재 미완료)

1. **v036 — 클라우드 CHMV 적응형 최적화 통합**: v032 엔진·고정된 룬 선택(기본 치명타)·프로필·스탯 하한·유효 CHMV 예산·JSON2 귀속과 v035 캐시 환경을 연결. 기존 v032 원본 코드/영수증을 확보하고 재현 검증 후 시작. **아직 실행·통과 아님.**
2. **생산형 캐시·브랜치 전략**: 검증된 캐시를 활용할 수 있는 단일 신뢰 개발 브랜치/워크플로, 도구 버전 고정, 컴파일러·빌드 설정 fingerprint 강화, 캐시 실패시 안전 재빌드.
3. **정확도·효율 동시 최적화**: 후보 중복 제거, 초기 적은 iterations, 유망 후보만 정밀 실행, 실행 포인트·시간·사용자 조작 횟수 측정. 동일 조건의 결과 재사용을 위해 시뮬레이션 캐시와 바이너리 캐시 분리.
4. **운영 안전화**: 요청 ID 단발성·최대 iterations/후보수/실행 횟수/동시성 제한·취소/재개, 신뢰성 있는 증거 보존, 실패 시 fail-closed.
5. **유지 보수**: \`actions/cache@v4\` Node.js 경고 제거, action 버전·SHA 고정, 정책 변경 검토. 시험 결과를 제품 정책/공식 Work OS 상태에 자동 반영하지 않음.

## 6. 운영 비용 최소화를 위한 사용자의 실제 행동

**목표 사용자 경험:** 사용자가 이 일반 Chat에서 "다음 개발 진행"이라고 요청 → Chat이 코드를 작성·GitHub 반영·SimC 시험·Artifact 회수·결과 분석을 한 번의 흐름으로 수행 → 사용자는 판정만 확인.

- **Work/Codex의 별도 실행은 필수가 아님**: 일반 Chat에서 GitHub 접근 가능한 환경일 때는 직접 사용. 다만 이 채팅도 자체 사용량 한도는 존재함.
- **사용자가 필요 없이 반복하면 안 되는 일**: GitHub Desktop 실행, 로컬 PowerShell 복붙, Actions의 Run workflow 버튼, 결과 ZIP 수동 다운로드·재첨부.
- **사용자가 필요한 때만 수행할 일**: GitHub 연결 권한 재인증, 제품 정책/고비용 실행/공식 운영 Gate 승격 승인, 도구 연결 또는 캐시가 막힌 경우 fallback 로컬 시험.
- **핵심 평가 기준**: 정확성·재현성·전체 완료시간·GitHub Actions 실행분·모델 사용량·사용자 직접 조작 횟수. 기술적으로 복잡한 설계를 도입하더라도 사용자 작업이 늘고 속도가 나빠지면 재검토한다.

## 7. 다음 채팅을 위한 최소 복원 절차

1. 이 MD를 먼저 읽는다. **실증된 기능과 아직 시험 브랜치에만 존재하는 기능을 분리**한다.
2. \`main\`의 v033 워크플로, v034·v035 시험 브랜치, 위 네 개 성공 Run ID를 GitHub 직접 읽기만으로 확인한다.
3. 개발자 노트 v1.0 및 사용자 승인 최신 정책을 읽고, 제품 코드 원본(v032)을 확보한다. 소스 파일·해시·실제 SimC 영수증 확인 전 "통합 검증 완료"로 표시하지 않는다.
4. 실증된 v035 cache key와 SHA는 **그 브랜치에서만 재사용이 실증됐음**을 기억한다.
5. 새 기능을 가장 작은 격리 실험으로 추가하되 기존 v003·공식 Work OS·main 안정 상태를 함부로 바꾸지 않는다.
6. Run 완료를 기다리기 위해 새 트리거를 중복 생성하지 않는다. 이미 시작한 Run ID를 조회하고 Artifact가 나오면 직접 회수한다.

---

**외부 기술 근거 (현재 적용 대상은 GitHub 공식 문서):**

- [GitHub Actions workflows and triggers](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows)
- [GitHub Actions cache scoping / cache security](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)
- [GITHUB_TOKEN events and recursive workflow prevention](https://docs.github.com/en/actions/concepts/security/github_token)
- [GitHub dependency caching vs. workflow artifacts](https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching)

**End — GitHub Chat Direct Execution Playbook v1.0.**