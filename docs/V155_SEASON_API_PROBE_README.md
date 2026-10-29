# v155 — 실제 Blizzard + WCL 시즌 콘텐츠 식별 최소 조회

**현재 상태:** 인증정보 미등록 시 NO LIVE API. GitHub Actions의 오프라인
계약 테스트는 실제 시즌 응답 증거가 아니다. v154는 ID 비교 도구이고,
v155는 앞으로 계절 식별의 핵심 경로를 1회씩 탐색하는 진단 도구이다.
둘 다 기존 제품/SimC Native 실행과 독립.

## GitHub Settings에 등록 (값은 채팅에 보내지 않음)

Repository **Settings → Secrets and variables → Actions → Secrets**:
- `BLIZZARD_CLIENT_ID`
- `BLIZZARD_CLIENT_SECRET`
- `WCL_CLIENT_ID` (선택)
- `WCL_CLIENT_SECRET` (선택)

같은 페이지 **Variables**에 `SIMC_ALLOW_SEASON_API_PROBE=true`를
사용자가 명시적으로 설정할 때만 새 GitHub push가 실제 조회를 실행한다.
현재 격리 브랜치에는 `workflow_dispatch`도 있지만 GitHub UI에서
신규 workflow_dispatch의 표시/수동 실행은 default-branch 존재 여부에
제약이 있을 수 있다. 따라서 user secret/variable 등록 확인 후
개발자 격리 브랜치에서 작은 문서 commit으로 push-triggering하는
경로가 기본이다. main 병합 또는 사용자 인증 공유는 불필요.

## 단 1회에 수행하는 작은 요청

Blizzard OAuth token 1회와 KR Game Data **4 GET**:
- `mythic-keystone/season/index` dynamic-kr (current_season.id 탐색)
- `mythic-keystone/dungeon/index` dynamic-kr (전체 목록 vs 로테이션 구분)
- `mythic-keystone/period/index` dynamic-kr
- `journal-instance/index` static-kr

WCL Secret 2개가 모두 존재하면 OAuth 1회와 GraphQL **2 POST**:
- `worldData.expansions {id name}`
- Midnight expansion ID가 단 하나일 때만
  `worldData.zones(expansion_id: ID) { id name frozen encounters
  {id name journalID} }`

즉 WCL 사용 시 최대 인증 2회 + 자료 조회 6회.
기본값은 전체 던전/보스/아이템 일괄 enumeration이 아님.
정확한 API 응답 schema/권한/현재 시즌 ID가 확인되기 전에는
"이번 시즌 모든 보스 드롭 ID 확보"라고 주장하지 않는다.

**Evidence output:** `v155-live-season-api-evidence.json` (GitHub
Actions artifact, 14일). 토큰/Client Secret/원본 HTTP 헤더는 포함하지 않음.
WCL zone `frozen` 값만으로 시즌 소속을 판정하지 않는다.
Blizzard dungeon index만으로 현재 8개 로테이션을 확정하지 않는다.

## 사용자 로컬 대안

```powershell
$env:BLIZZARD_CLIENT_ID="(Windows local env)"
$env:BLIZZARD_CLIENT_SECRET="(Windows local env)"
# WCL credentials are optional
py -3 runner/v155_season_api_probe.py --out v155-live-season-api-evidence.json
```

단 이 명령을 사용자에게 실행하도록 요구할 필요 없이,
GitHub Secrets+허용 변수 등록 후 격리 Actions에서 한 번 실행한다.

## 다음 정밀 구현 판정

1. 실제 season/index current_season.id 가 노출되는가?
2. 실제 dungeon/period endpoints가 season→dungeon 관계를 노출하는가,
   아니면 단순 전체 목록인가?
3. WCL의 실제 Midnight zones→journalID가 정상 제공되는가?
4. Blizzard journal-encounter의 실제 items/loot JSON이 v154 파서와
   일치하는가? 일치하지 않으면 parser만 최소 수정한다.
5. 구렁의 REST 드롭 목록이 없다면 기존 증거로 보완할 수 있는가?

필요한 경우 두 번째 단계에서 딱 1개 실제
`journal-encounter/{journalID}` 조회로 item ID field를 확인한다.
작동 확인 전 레이드×던전×구렁 전체 호출·SimC Native 반복 실행 금지.

## 2026-10-29 사용자 등록 완료에 따른 첫 opt-in 실조회

사용자가 GitHub Actions Secrets 및 허용 Variable 등록 완료를 보고하여,
본 **문서 변경 push 1회**로 기존 workflow의 정확한 opt-in 조건을 평가한다.
실제 Secrets 값/조회 성공 여부는 Actions 결과로만 판정한다.
실패하거나 live job이 skipped되면 재시도 자동화 없이 멈추어 확인한다.
기존 제품 최적화 엔진과 Native 사용은 변경하지 않는다.
