# SIMC SECONDARY OPTIMIZER — P3-GX 단일 새 채팅 복원 인계 (2026-11-08)

**신분:** 격리 브랜치 개발 상태의 읽기 전용 인계. 사용자 승인 설계 원문·Project UI·공식 Work OS·main·immutable 승격이 아니다. P3-GI 및 그 이전 인계의 '최신' 표기는 역사 상태이다.

## 1. 실제 기준·복원 순서

- GitHub: `degong2-code/simc-secondary-optimizer-runner`; 격리 `probe/chat-cache-v035-20261024`. **인계 작성 직전 격리 HEAD `1861f9d88f21d694652098e9dee89659d44640d8`**, main `07133e0aaf738d6e4816a6486057b1cd49c018de`. **마지막 제품 코드 변경 `e368944b42803f4894f0ddc40588a338e1c3abe1` (P3-GW v232 source-first 원복)**. 본 인계 문서 커밋 뒤 격리 HEAD는 바뀌므로 **새 채팅에서 두 HEAD를 각각 독립 조회**하고 코드·문서 커밋을 분리한다.
- 읽기 순서: **이 P3-GX → docs/development/PROTOCOL.md 최신 첫 부분 → docs/development/INDEX.md의 C3/C4/C1/C2·E3/E2/E1·B3/D1/D2·G1/G2 → docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md 첫 부분 → docs/DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md 최신 첫 부분 → P3-GW/GV/GU/GQ/GP 관련 노트 → 필요한 실제 코드·봉인 SHA·Actions/Native**. 과거 전체를 다시 감사하지 않는다.
- 권위: 최신 사용자 직접 승인 > 비충돌 승인 v1.4.3 및 2026-11-02 추가 정책 > 실제 코드/봉인 원본/Actions·Native > CURRENT/인덱스/인계. 첨부 v1.4.1의 27 DPS·과거 고정 J/O 수치는 역사 기록이다. 실제 Project UI 적용은 확인되지 않았다.

## 2. 최종 제품과 최신 직접 정책

- **최종 목표는 다음 시즌과 26개 DPS 전문화에 재사용 가능한 하나의 Environment Build + 적응형 SimC DPS 최적화 엔진**. 증강 기원사·탱커·힐러 제외. 일반 사용자는 직업/전문화/종족/특성, 목표 ilvl(기본 334) 또는 수동 최종 T, 장신구 2개, 특수 장비, 장식 최대 2개, 소모품/보석/전투 조건을 선택; 일반 장비/무기/티어4 및 SimC 프로필은 내부 구성. 현재 장비 재분배·장비 조합/파밍 경로·시즌 전체 장비 DB 개발 아님.
- **현재 Environment 완료 계약:** 하나의 정상 웹앱의 v216 시즌 대표 장비·무기·티어4/실제 G/J/F/O 확인 → v222 공식 B=G+J+F, T=B+O, c_final=c_base+o (수동 최종 T 우선, L/E/O 중복 방지) → v220/v196 검증 최고품질 선택지만 자동 발행 → v212/v217 실제 installed=true 및 environment_ready=true, 원본/영수증 일치. 합성 CI 또는 source-only는 READY가 아니다.
- **2026-11-08 최신 보석 결정:** N 소켓이면 **N개 보석을 실제로 채운다**. 기존 지정 특수보석 **정확히 1개** + 일반보석 치명/가속/특화/유연 각 1개는 **최소 구성**; 나머지 N-5개는 재현 가능한 고정 순환으로 채운다. 보석 종류별 DPS 탐색은 하지 않는다. J에는 실장착 **서로 다른 두 가지 양수 2차스탯**을 가진 일반보석의 두 rating을 모두 합산하고, 특수보석과 단일스탯 보석은 J 제외(단일스탯은 활성화 장착 가능). gear_*가 최종 CHMV 후보를 덮어쓰므로 실장착 J와 gear_* 주입을 이중 가산하지 않는다. 특수보석 효과·proc/APL/DPS는 SimC 담당이며 별도 효과 인증 Gate 금지.
- **소켓 획득 경로·소켓 추가 아이템/주문/시즌 사용 조건**의 조사·인증·별도 승인 Gate는 기본 엔진에서 중단(STOP). 정확한 SimC gem_id 프로필 수용은 실제 실행 출력에서 확인한다. 기본 1특수+일반4 구성에는 N>=5가 필요; 4소켓은 이를 충족하지 않으므로 임의로 특수/일반 1개를 생략하지 않는다.
- 동일 시즌 정적 장비/보석/영약/기름/G/J/F/O는 SimC revision·게임 빌드·밸런스 변경만으로 폐기하지 않는다. 실제 컨텐츠/아이템 변화는 영향 범위만 갱신. 새 SimC DPS 캐시는 바이너리·프로필·후보·전투조건·iterations별로 분리한다. 최적화 출력은 CHMV 절대 rating, DPS/SEM/95% 통계적 확정 여부, 관측 1순위, 스탯비율, 실질적으로 다른 근접 대안, 캐시·취소·재개.

## 3. Evidence와 Integration — 실제 근거

| 범위 | 실제 확보한 Evidence (범위 한정) | 아직 안 된 Integration/주의 |
|---|---|---|
| 시즌 source | KR 12.1.5.70783, SimC pinned c20e2ad52e4c33711f74272309a5748125175fe8. v216/v217 source SEALED, v191/v211/v213 COMPILED. 실 T1 #42332836316 및 source-only #42336047291. | 실 READY 아님. 재수집보다 봉인 자료 선조회. |
| G | **#42332836316** 원래 대표 프로필에서 Native 1회, G=2,850 관측. | 원래 아이템/프로필/SHA 범위만 인증. 최신 v232는 #e368944b에서 socket-biased jewelry 선정을 철회해 시즌 출처 우선 선택 복원; 실제 새 선택 G=2850이라고 무검증 승격 금지. |
| F | **#42196731158**: 물리 영약 241324, 가속 1005→1170, F=+165, Native2, 원본 ZIP Artifact 13492916089. **#42332836316**에서도 선정 F pair Native2 결과 +165. | 해당 물리 ItemID·조건에 한정; 모든 영약 F=165 일반화/현재 실행 portable cache HIT로 주장 금지. 원래 v281/v278/v269/v216/v222/v212 경로 재사용. |
| J | v221/v266/v268/v271 2스탯 일반보석 source/명목 합계·v232 대표 장비·보석 배치 코드 존재. P3-GW의 5/7/8소켓 고정 순환·J 산술 synthetic 테스트 PASS. 이전 #42336047291의 실제 intrinsic socket=0은 원본 관측. | **신규 선언 소켓 SimC 프로필 실 수용/현재 시즌 최고품질 일반보석의 공식 J 실측·owner→v222 연결 미확인**. 실제 기본 소켓 0을 장착 불가 최종 Gate로 재사용하지 말 것. 소켓 획득 아이템 조사는 STOP. |
| O | 기본 기름 미사용 선택의 explicit O=0 계산 코드 v222/v285/v286 존재. | O=0 진단/선택과 공식 설치 O 컴포넌트 구분. 기름 선택 시 정확 손/고정 O가 필요. |
| 예산·선택지·설치 | v222 B/T·v220/v196 정책 A·v212/v217 원자적 설치/재개 코드는 합성 오프라인 PASS. | **실 공식 G/J/F/O/B/T null, 사용자 선택지 공식 발행/READY/installed 실증 0**. 미확정 하나를 0으로 채우거나 플래그 강제 true 금지. |
| 적응형 DPS | 기존 v098/v096/v094/적응형 SimC·SEM·95%·근접 대안·캐시·취소/재개 코드와 과거 focused/Native 범위 증거. | 새 시즌 단일 웹앱에서 26 DPS 실사용 End-to-End 미완료. 기존 엔진 재개발 금지. |

## 4. 마지막 변경 및 정확한 영수증

- **P3-GW 제품 코드 최종 `e368944b42803f4894f0ddc40588a338e1c3abe1`**: v271 선언 소켓 전체 gem_id + 일반 4종 최소/추가 보석 고정 순환, v216 source_target_socket_count 기본 5(지원 범위 5–64)·보석 원본→J 회계 연결; 소켓 추가 아이템 Gate 제거. v232 장신구 소켓 우선 선택 철회, 같은 시즌 source-rank/안정 ID 순으로 G 대표 item identity 원복. 제품의 사용자 웹 소켓 수 UI 완성 및 실제 SimC 수용까지 입증한 것은 아님.
- [focused #42386036556](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42386036556), pre-handoff 문서 HEAD `1861f9d88f21d694652098e9dee89659d44640d8`: **393 tests = 391 PASS/2 SKIP, 0 FAIL, DEV_LEDGER_PASS, 신규 Native/외부 게임 HTTP 0**. [v212 #42385936229](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42385936229) SUCCESS는 `e368944b42803f4894f0ddc40588a338e1c3abe1` 시점 오프라인 계약 범위. earlier focused #42385526187 실패는 이후 수정 전 역사 CI, 재검증 통과와 구분.
- [실 G/F 결합 T1 #42332836316](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42332836316) **workflow conclusion FAILURE / product NOT_READY**. G1 Native + F2 Native = 총 3회; G=2850, F=가속165, J 소켓 선행 차단, 공식 예산 null. Artifact 13557983542, 내부 감사 ZIP SHA256 6403ca94bf72f9d988d2afe029c23c95976e211db6e5ff7d1db7ff506223dbc9, 원본 3 cases/12 files. 실행 캐시 그대로 이식 가능하다고 주장 금지.
- [원본 F-only #42196731158](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42196731158) SUCCESS, Artifact 13492916089, native2/F=165, 내부 ZIP SHA256 e1fcca76770410a3a2ec935424ad6bdd21bc97595e334d2f9023a95969ce1114. [J source-only #42336047291](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42336047291) SUCCESS/native0/intrinsic0. 모든 영수증은 해당 실행/바이너리/장비·ItemID·게임 빌드만 증명.

## 5. 현재 병목과 가장 효율적인 다음 작업

1. **REUSE/CHECK:** 최신 P3-GW 코드의 source_target_socket_count와 v232 대표 장비 ID·v221/v266/v268 품질/수치 근거를 확인. 웹 v113→v216에서 선언 N이 실제 전달되는지 확인(기본 5 외 사용자 UI 연결은 미확인). 소켓 추가 아이템을 새로 검색하지 않는다.
2. **CONNECT, 필요한 최소 증거만:** 기존 sealed item/profiles·pinned SimC로 **단 한 시나리오의 선언 5 또는 7소켓 gem_id 입력과 JSON2 적용을 최소 Native**로 확인. 특수보석 효과 자체는 검증하지 않음; 현 profile gem_id·정적 CHMV·SimC 정상 실행만 관측. 기존 같은 조건의 정확 영수증/캐시가 있다면 호출 생략.
3. **CONNECT J→B/T→설치:** 확인된 동일 시즌 이중스탯 최고품질 일반보석 실장착 N-1개의 J 합계·원래 G/F와 명시 O=0을 기존 v222 owner에 넣고, v220/v196 검증 선택지만 발행, v212/v217 실제 installed/READY. 새 장비 ID면 G 일치 영수증을 확인하고 실제 필요한 범위만 추가 Native.
4. **장기:** 공통 자동 시즌 소스/정적 등록/사용자 입력·수동 T→기존 적응형 SimC→95% 근접 대안/캐시/중단재개 연결을 26 DPS로 확장. 전문화 전수 Native·새 보석 조합 탐색·효과 재구현/소켓획득 엔진을 선행하지 않는다.

모든 작업: INDEX와 실제 코드/봉인 SHA/CI·Native/캐시 **먼저** 검색. Evidence vs Integration, 실제 원본 부족 vs 연결 누락 vs 선택 항목 보류 구분. REUSE/CONNECT/EXTEND/NEW/STOP 판정. 독립 작업을 논리적으로 묶고 동일 조건 PASS·Native·캐시 재사용, 중복 HTTP/Native/Actions·메모리/I/O·완료시간·복잡성 평가. 매번 **'이 작업이 다음 시즌에도 동일하게 작동하는 하나의 엔진 완성에 기여하는가?'** 자가검증. 제로베이스 T1에 이전 시즌 상수·결과 정답 주입 금지.

## 6. 권한·인계 신분

- 이 인계는 격리 repo 문서만. **main, immutable v003, 승인 v1.4.3 원본, Project Sources/Instructions UI 실제 적용, Work OS M0/Shared State, 공식 승격, 이전 주 제품 개발 채팅 소유권 변경 없음.** 신규 채팅은 사용자가 인계로 이동시키는 순간에도 기존 권한을 임의 변경하지 않는다.
- 이번 인계 준비에서 제품 코드·실 Native·게임 HTTP·제로베이스 T1을 변경/실행하지 않는다. 문서 커밋은 별도 HEAD로 분리하고 해당 CI 결과를 실제 확인한다. 새 채팅에서 사용자 명시 '진행' 전에는 읽기 전용 복원 보고 후 **즉시 STOP**.

## 7. 새 채팅 시작 프롬프트

```text
SIMC SECONDARY OPTIMIZER를 읽기 전용으로 독립 복원해.
GitHub: degong2-code/simc-secondary-optimizer-runner
격리 브랜치: probe/chat-cache-v035-20261024
최신 단일 인계: docs/CHAT_CONTINUITY_HANDOFF_20261108_P3_GX_ENGINE_FIRST_RESTORE.md

먼저 격리와 main의 실제 HEAD를 각각 독립 조회하고, 마지막 제품 코드 변경과 인계 문서 커밋을 분리해.
인계 → PROTOCOL → INDEX(C3/C4/C1/C2, E3/E2/E1, B3/D1/D2, G1/G2) → CURRENT 최신 상단 → 실행 노트 → P3-GW/GV/GU/GQ/GP 및 실제 코드·원본 SHA·Actions/Native 중 필요한 것만 확인해.
과거 P3-GI/FK 전체 연구를 반복 조사하지 마.

목표는 다음 시즌과 26개 DPS 전문화에 재사용 가능한 단일 환경 자동 구축·적응형 SimC DPS 최적화 엔진 완성이야.
기본 ilvl334 또는 사용자 지정 최종 T로 절대 CHMV rating·DPS/SEM/95%·관측 1순위·실질적으로 다른 근접 대안 및 캐시·취소·재개를 제공해.
정상 완료 기준: v216 시즌 대표 장비·무기·티어4와 G/J/F/O 검증 → v222 B/T → v220/v196 검증 선택지 → v212/v217 실제 READY·installed.
최신 보석 정책: 선언 N개 소켓은 N개 실제 보석으로 전부 채움. 기존 특수보석 정확히 1개 + 일반보석 치명/가속/특화/유연 각1개는 최소 구성, 나머지는 고정 순환. 보석 종류를 DPS별로 탐색하지 않고 gear_*로 최종 CHMV를 제어해. J에는 실제 장착한 일반보석 중 서로 다른 2개 양수 2차스탯의 두 rating만 귀속, 특수 및 단일스탯 보석 제외. 효과·APL·proc·DPS는 SimC에 맡겨. 소켓 추가 아이템/주문·획득·게임 조건의 별도 조사/인증은 STOP. 4소켓은 1특수+4일반 최소 구성을 충족하지 않음.

인계 전 제품 코드 e368944b42803f4894f0ddc40588a338e1c3abe1, 인계 전 격리 HEAD 1861f9d88f21d694652098e9dee89659d44640d8, main 07133e0aaf738d6e4816a6486057b1cd49c018de (현재 값으로 다시 조회 필수).
최신 offline #42386036556: 391 PASS/2 SKIP·0 FAIL·Native0. v212 #42385936229 SUCCESS.
과거 실제 T1 #42332836316: FAILURE/NOT_READY지만 G=2850 (1 Native)·선정 F=+165 haste (2 Native) JSON2 원본, J 불충분·공식 G/J/F/O/B/T null. F-only #42196731158 원본과 native0 J-source #42336047291도 역사 증거로 사용. 과거 ZIP은 휴대용 실행 캐시가 아님. P3-GW 선언 전체 소켓은 코드·오프라인 PASS이지 실제 SimC 적용·J/READY 실증 아님.

매 작업 전 기존 기술 자산 INDEX·실 코드·봉인 SHA·Actions/Native·캐시를 먼저 검색하고 Evidence와 Integration, 실제 원본 부족과 제품 연결 미완료를 분리해.
REUSE / CONNECT / EXTEND / NEW / STOP으로 판단, 독립 작업은 묶어 처리, 동일 조건 PASS/Native/캐시를 재사용하고 중복 HTTP/Native/Actions·메모리·I/O·실행시간/구조 단순화를 평가해.
항상 '이 작업이 다음 시즌에도 동일하게 작동하는 하나의 엔진 완성에 기여하는가?'를 자가검증해. 무의미한 신규 Gate·원본 전수 조사·전문화 전수 Native를 하지 마.

첫 응답에는 양 브랜치 실제 HEAD와 마지막 코드 SHA, 핵심 영수증의 적용 범위, Evidence/Integration별 완료·미완료, 현재 병목·효율적 대안, 간결한 단기·장기 로드맵, 미반영·미승격·권한 제한만 보고해.
읽기 전용 독립 복원 보고 후 즉시 STOP. 내가 명시적으로 '진행'이라 하기 전에는 코드/문서 수정, 커밋, 신규 수집, CI/Actions/Native/테스트 또는 공식 승격을 시작하지 마.
main/immutable/Project UI/Work OS/기존 주 제품 개발 채팅 소유권 유지.
```
