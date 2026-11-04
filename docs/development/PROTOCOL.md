# 개발 연속성 규약 · 2026-11-03 사용자 직접 교정

**권위:** 최신 사용자 직접 결정. 이 문서는 GitHub 격리 브랜치의 **개발/인계 운영 규약**이며 승인된 제품 설계 v1.4.3의 원문, main, immutable v003, 원본 v016, Project UI/Work OS를 변경하지 않는다.

**환경 입력 관련 필수 선조회:** 레벨·종족·특성·음식/물약/증강·보석/가변 소켓·영약/기름·Omnium·품질/정책 A 작업 전에 [2026-11-04 환경 구축 입력 12항목 책임표](ENVIRONMENT_BUILD_INPUT_SCOPE_20261104.md)를 읽고, 각 항목의 REUSE/CONNECT/EXTEND/STOP·기본 G/J/F/O와 선택형 기능 경계를 확인한다. 이 문서는 승인 원문 교체가 아닌 기존 정책과 구현을 구분하는 개발 색인이다. 특히 P3-BN SimC 기본 level 및 P3-BZ 기존 가변 socket_plan 구현을 재개발하지 않는다.

## 매 논리적 작업 묶음마다 필수: 4단계

1. **선조회(작성·추가 검증보다 먼저).** [INDEX.md](INDEX.md)의 `Capability`와 한·영문 `Keywords`를 검색하고 해당 행의 **기존 증거 문서/원본 영수증**과 실제 관련 코드만 확인한다. 필요하면 GitHub 전체 코드/역사 기록으로 좁혀 검색한다. 검색어가 없으면 새 고정 capability 키를 추가한다. **현재 코드의 `false`, `PENDING`, 미완료 문구만으로 원본 증거 부재를 단정하지 않는다.**
2. **문제 구분·재사용 결정.** `Evidence`(어떤 사실을 어떤 시즌/빌드/옵션까지 확립했는가)와 `Integration`(제품에 연결되었는가)를 **따로** 판정한다. `REUSE`(이미 증명/구현된 부분), `CONNECT`(연결만 미완료), `EXTEND`(실제 부족한 근거만 보완), `NEW`(기존 대응 없음), `STOP`(불필요/범위 외) 중 하나와 근거를 선택한다. 새 인증 Gate·새 Native/HTTP는 실제 누락된 사실과 기존 증거로 해결 불가능한 이유가 특정된 경우에만 검토한다.
3. **한 작업 = 한 짧은 GitHub 노트.** `notes/YYYY-MM-DD_<task-slug>.md`를 작업 전부터 기록해 작업 범위·재사용 근거·결정·변경·시험·남은 과제·효율을 작성하고, 관련 `INDEX.md` 행의 `Last note` 링크를 갱신한다. 독립 가능한 여러 세부 작업은 하나의 **논리적 묶음**에 포함 가능하다. 파일별·커밋별 문서를 만들지 않는다. 기존 기록의 사실 오류는 후속 기록에서 교정하고 과거 영수증·실패 이력을 삭제하지 않는다. 새 GitHub 커밋 또는 작업 종료 전에 기록을 반영한다.
4. **인계는 INDEX 우선.** 새 채팅: 최신 권한/HEAD → 이 규약 → INDEX의 해당 capability 행 → 마지막 관련 note → 원본 영수증/코드 순서로 읽는다. `CURRENT`의 `미완료` 요약만으로 개발을 시작하지 않는다. 인계에는 **재사용 가능한 완료 사실·정확한 적용 범위 / 연결 미완료 / 실제 소스 부족 / 다음 최소 작업 / 검증 방식**을 각각 명시한다.

## 짧은 기록의 정형 필드

[노트 양식](TEMPLATE.md)의 8개 필드(`Capability`, `Keywords`, `Prior evidence`, `Decision`, `Changes`, `Verification`, `Remaining`, `Efficiency`)는 **모두 필수**, 본문은 가능한 20줄 내외, 최대 45줄. 기존 문서/Actions/커밋을 링크로 가리키며 내용을 중복 복사하지 않는다. `Verification`에는 **새 실행 PASS/FAIL, 역사 증거 재사용, 이번에 하지 않은 HTTP/Native**를 분리한다. CI 미확인이면 `NOT_RUN/NOT_VERIFIED`라고 쓴다.

**충돌 처리:** 인덱스는 증거 **위치와 요약**이지 원본보다 높은 진실 출처가 아니다. 최신 사용자 결정 > 승인 설계 > 해당 코드/실제 원본·Native·Actions 영수증 > 인덱스·인계 요약. 반례가 발견되면 관련 note에 교정·범위를 기록하고 INDEX 상태를 수정한다.

**경량 안전장치:** `python tools/check_development_ledger.py`로 INDEX/노트 구조·링크·상태를 네트워크/Native 없이 검사한다. `--since <task-base-ref>`는 해당 작업 범위의 코드·테스트 변경에 노트가 포함되었는지 점검한다. 이는 제품 READY/효과 인증 Gate나 반복 CI/Native 시험이 아니다. 작업 기준 커밋을 명시하지 않는 한 임의로 옛 main 전체 diff를 검사하지 않는다.

**성능·설계:** 기존 원본·동일 시즌 SHA/검증 결과·캐시·Native/CI를 재사용하고, 실제로 부족한 범위만 보완한다. 새 코드 변경마다 중복 HTTP/Native, 캐시 무효화, 메모리/I/O, 전체 시간·구조 간결성을 평가한다. 장기 목표는 **26 DPS용 하나의 재사용 가능한 시즌 G/J/F/O Environment Build → B/T → 기존 적응형 SimC**이며 별도 효과 엔진/전수 장비 DB/추가 인증기 개발이 아니다.

## 새 채팅 인계 복원 동작 · P3-DF 최신 (2026-11-04)

새 채팅의 단일 진입점은 [P3-DF 인계](../CHAT_CONTINUITY_HANDOFF_20261104_P3_DF_ENGINE_RESTORE.md). [P3-CV](../CHAT_CONTINUITY_HANDOFF_20261104_P3_CV_ENGINE_RESTORE.md)는 역사 자료. GitHub 격리 branch/main HEAD 각각 독립 조회 → 본 PROTOCOL → INDEX → P3-DE/P3-DD 관련 노트 → CURRENT/개발자 노트/승인 v1.4.3 → 실제 코드·영수증 순서로 **읽기 전용** 복원. PENDING 상태만으로 원본 증거 부재를 주장하지 말 것.

**P3-DE** [222 PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41767573431)는 새 시즌 gear/tier/budget/settings 교체형 26 DPS 대표 프로필 미리보기이지 실제 새 시즌 raw gear/tier SHA 인증/Native READY가 아니다. **P3-DD** [219 PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41764255684)는 기존 같은 시즌 승인 영수증에서 v098→v096→v094 실행 함수 연결. 실제 근거와 제품 접합을 구분하고 최신 26 DPS(증강 제외), G/J/F/O 전체 자동 구축, 정적≠buffed, 1 rating 후순위·SimC 효과 책임 준수.

**새 채팅 첫 응답에서는 HEAD·증거·완료/미완료·병목·효율 대안·로드맵 복원 결과만 보고하고 STOP. 사용자의 “진행” 전 코드/문서 수정·커밋/신규 수집/CI/Actions/Native/테스트·승격 금지.** GitHub 문서 작성은 Project UI·Work OS 등록·main 병합 증거가 아님.
