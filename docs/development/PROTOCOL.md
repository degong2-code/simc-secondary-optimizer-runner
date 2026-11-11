# SIMC 개발 지속성·지식 유지 프로토콜

> [START_HERE](START_HERE.md) · [INDEX](INDEX.md) · [FILE_MAP](FILE_MAP.md) · [EVIDENCE_INDEX](EVIDENCE_INDEX.md). 이전 누적 일자별 '최신' 설명·원문은 [역사 PROTOCOL](HISTORICAL_PROTOCOL_20261110_PRE_KNOWLEDGE_LAYER.md)에 보존한다.

## 매 작업 착수 전

1. 격리 브랜치와 `main`의 실제 HEAD·사용자 최신 승인·주 제품 개발 소유권을 구분한다.
2. INDEX에서 해당 기능 → FILE_MAP 핵심 소스/실제 호출·테스트 → EVIDENCE_INDEX 원본 SHA·조건·캐시/Native/Actions 선조회. **증거 미확보와 실제 재현 결함을 분리**한다.
3. `REUSE/CONNECT/EXTEND/REPLACE/NEW/STOP` 중 근거 있는 가장 작은 변경을 선택. 탐색 알고리즘 자체는 고정하지 않으나 결과 품질/신뢰성을 최우선으로 한다.
4. 한 묶음으로 수정하고 바뀐 코드·조건에만 최소 검증을 수행한다. Native 중복, 원본 HTTP/다운로드, CPU·메모리·I/O·실행시간, 정적/DPS 캐시 재사용을 검토한다.

## 제품·검증 불변

- 26 DPS, 목표 ilvl(기본334) 또는 수동 최종 T의 절대 CHMV rating SimC DPS 최적화. 전체 착용 장비 재분배/장비 조합 추천/전체 시즌 DB는 제외.
- 새 시즌의 G/J/F/O·원본 증명; `B=G+J+F`, `T=B+O`, 수동 T 우선, L/E/O 고정 소유·중복 금지. 기본 일반 보석 치명/가속/특화/유연 각1·특수 선택형.
- SimC가 APL/proc/아이템 효과/DPS 소유. 효과 메커니즘 재구현·별도 효과 인증 Gate·근거 없는 Native 전수/비슷한 시즌 수치 복사 금지.
- `CODE_IMPLEMENTED`/`OFFLINE_PASS`/`REAL_NATIVE_PASS`/`USER_WEB_E2E_PASS`/미실증/재현 결함을 엄격히 구별. 95% 선택쌍·SEM을 전역 최적/다중선택 확정이라 표현하지 않는다.
- 같은 시즌 정적 아이템 캐시는 SimC revision만으로 폐기하지 않는다. DPS 캐시는 정확 바이너리/프로필/환경/옵션/후보/O/전투조건/iterations identity를 분리.

## 기록과 검색 관리

- **논리적 작업 묶음당** 짧은 개발 노트 `notes/YYYY-MM-DD_slug.md` 1개와 INDEX Capability 행 갱신. 45줄 이내, `Capability`, `Keywords`, `Prior evidence`, `Decision`, `Changes`, `Verification`, `Remaining`, `Efficiency` 8필드 각각 1회.
- 현재 구현·미구현은 정본의 A~G, 파일 관계는 FILE_MAP, 실증과 한계는 EVIDENCE_INDEX, 채택/철회 이유는 DECISIONS에서 링크. 역사 자료는 삭제하지 않되 각 문서의 최상단에 날짜별 '최신' 내용 적층하지 않는다.
- FILE_INVENTORY는 정확 HEAD의 **정적 파일 발견 스냅샷**이지 항상 최신인 자동 인덱스나 새 필수 Gate가 아니다. 새 주요 파일·테스트가 실제 추가되면 변경한 부분만 갱신.
- 새 인계는 HEAD/현재 작업/실제 변경·영수증/남은 병목만 짧게 기록하고 위 탐색 지도에 링크. 문서 작성이 신규 Native/공식 승격·Project UI 적용의 증거가 아니다.

## 권한

main·immutable v003·원본 v016·Project Sources/Instructions·Work OS·공식 승격은 별도 승인 필요. 주 제품 개발 채팅의 실행 소유권 보존. 새 채팅이 읽기 전용 복원을 요청받으면 보고 후 즉시 STOP, 별도 '진행' 전 코드·문서·Native/Actions·커밋 작업 금지.

## 2026-11-11 직접 사용자 결정 — **매번 새 전문화 프로필을 생성한 뒤 시험**

- **실제 Native를 이용한 새로운 알고리즘 비교·성능·품질 실험마다**, 먼저 현재 제품의 사용자 입력→시즌 환경 구축/검증→대표 장비·특성·장신구·소모품→새 SimC 입력 프로필 경로를 직접 실행한다. 앞선 캠페인의 완성된 캐릭터 SimC 프로필·DPS 결과를 시작값/시험 프로필로 복제하지 않는다.
- 해당 캠페인에서 만든 **단일 신규 프로필과 원본 SHA를 모든 알고리즘 arm이 공유**한다. 정책별로 각각 프로필을 새로 만들면 동일 조건 비교가 성립하지 않으므로 금지. 새 캠페인에서는 가능한 한 과거 실험과 **다른 전문화**를 선정해 일반 26 DPS 입력·P1 시즌 Build 기능도 순차 회귀 검증한다.
- 정확한 같은 시즌 정적 데이터/캐시·원본 SimC 바이너리/검증 증거는 **유효 범위에서 재사용 가능**하다. 그러나 새 캐릭터/전문화 프로필이 실제 만들어진 증거, 고유 `source_profile_sha256`, 장비/예산 F/O/L/E·T의 정확한 회계 및 전투조건을 별도로 기록한다. 이전 최고 CHMV를 새 프로필의 초기 후보로 주입 금지.
- 오프라인 합성 회귀·기존 원본 영수증 대사는 실제 신규 프로필 Native 실험이 아니다. 오프라인 테스트마다 비싼 시즌 재구축/SimC Native를 요구하지 않는다.
- 공정 결과 판정은 **Native 호출수 동일**과 **총 SimC iterations 동일**을 구분한다. 새 원본 결과의 DPS/SEM·320 확인·시간 경과점/95(명목)와 비용을 함께 기록한다. 어느 쪽이 동일 예산이 아니면 이를 '동등 조건 실험'으로 주장하지 않는다.
- 첫 적용 캠페인: 기존 v313/v314 10전문화 밖의 **풍운 수도사 (monk/windwalker)**, 사용자형 신규 T3450/ilvl334/일반 보석4/특수0/O0. 실험 진행 영수증 및 새로운 Native PASS는 별도 확인해야 한다.
