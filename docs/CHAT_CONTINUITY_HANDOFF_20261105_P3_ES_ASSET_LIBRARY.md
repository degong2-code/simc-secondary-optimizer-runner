# SIMC SECONDARY OPTIMIZER · P3-ES 기술 자산 라이브러리 기반 새 채팅 인계

**2026-11-05 KST / 격리 개발 기록 / 공식 승격 아님.** 지난 [P3-EN 인계](CHAT_CONTINUITY_HANDOFF_20261105_P3_EN_ENGINE_FIRST.md)는 역사 자료이며, 이 파일은 인계 검색 순서를 가볍게 갱신한다.

## 1. 정본 및 읽기 순서

- 저장소 `degong2-code/simc-secondary-optimizer-runner`, 격리 `probe/chat-cache-v035-20261024`. 이 문서 작성 **전** 격리 HEAD `abffe43835f9553b8bbb2e3aa4c2e3443fbaada6`, `main` HEAD `07133e0aaf738d6e4816a6486057b1cd49c018de`. 최신 제품 코드 커밋 P3-ER `a30c6273f7f9e91a09df379ad4fcf49eddc597db`. **새 채팅에서는 두 HEAD를 실제로 독립 재조회**한다.
- 순서: 실제 두 HEAD → 이 인계 → [PROTOCOL](development/PROTOCOL.md) → [기능 라이브러리 INDEX](development/INDEX.md) 요청 관련 A~G 영역 → [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) 상단 → 해당 함수·원본 SHA·CI/Native. 모호한 경우에만 관련 [작업 노트](development/notes/)와 [시간순 이전 INDEX](development/HISTORICAL_INDEX_20261105_PRE_LIBRARY.md) 및 P3-EN을 연다. **과거 P3 전체 자동 전수 감사 금지**.
- 권위: 최신 사용자 결정 > 승인 [v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md) > GitHub 실제 코드·원본·Actions/Native > 인계/INDEX. 라이브러리는 증거 위치와 재사용 지도를 뜻하며 새 인증 결과가 아니다.

## 2. 제품 목적 및 현 Gate

26개 딜러 전문화(증강·탱커·힐러 제외)에 공통 적용되는 단일 엔진. 사용자는 목표 ilvl(기본 334) 또는 수동 최종 T와 캐릭터·장신구·일부 효과를 입력하고, 프로그램은 미래 파밍 목표의 **치명/가속/특화/유연 절대 rating**을 SimC DPS로 최적화한다. DPS·SEM·95% 판정(관측 1순위와 통계적 우위 분리), 비율, 근접 대안, 취소/재개·캐시 제공. 현재 장비 스탯 재분배·장비 추천/시즌 전수 DB·SimC APL/proc/효과 재구현은 범위 밖.

**현재 완료 판정 목표 T1:** 기존 정상 웹앱 `v216`으로 동일 시즌 대표 일반 장비·무기·티어4·필수 예산 **G/J/F/O** 확인 → 기존 `v222` 공식 `B=G+J+F`, `T=B+O` (수동 T 우선, L/E/O 중복 없음) → `v220/v196`에서 검증된 최고품질 사용자 선택지 실제 발행 → `v212` 원자적 설치·READY. **여전히 미완료.** `v098→v096/v094` 적응형 SimC는 이후 제품 통합이며 T1 필수 Gate가 아니다.

## 3. 라이브러리 A~G 재사용 지도

| 분야 | 지금 재사용 가능한 구현 | 실제 남은 제품 연결 |
|---|---|---|
| A 원본·캐시 | `v161/v229/v191/v211/v213/v217`, `v268` 원본 봉인·조인 재사용 | 새 시즌 필수 소스 증거·인증 |
| B 대표 장비/G | `v167/v251/v230/v232` 대표 13/14슬롯·티어·무기, `v277` 선택 exact G 또는 같은시즌 참조 | 현재 시즌 공식 G·예산 범위 |
| C 보석/소켓/J | `v221/v266/v268` 보석 ID↔효과, `v230` 품질·기본 소켓, `v271` 특수 **정확1** + 일반N. 열린 소켓은 일반/특수 모두 허용. P3-BX 4/4 Native는 SimC 입력 증거 | 검증된 최종 소켓 수, 최고 품질·정적/SimC-effective J, 특수효과 소유권 |
| D 영약/기름/E | `v281/v278` F/O 선택적 측정·캐시, `v285/v286` 손·무기, `v211` 영구 마부. **명시적 기름 미사용**만 O=0 | 새시즌 최고품질·정적 F, 선택 O 적용성, E/L 한 번 회계 |
| E 회계·발행·설치 | `v222` 계산·`v220` 정책 A 4-family·`v196` prepared·`v212` source stage | **공식 G/J/F/O/B/T, 실제 선택지 발행, 환경 READY/T1 모두 미완료** |
| F 사용자·최적화 | `v143/v139/v098` 대표 프로필, `v096/v094` 95%·적응형 SimC, `v113` 웹 API | 환경 READY 이후 실제 신규 시즌 통합 |
| G 검증·인계 | `tools/check_development_ledger.py`, 기능별 INDEX, GitHub Actions 영수증 | 변경된 범위만 검증하고 해당 자산 행만 갱신 |

최신 코드 P3-EO는 동일시즌 G 재사용 시 불필요한 Native 억제, EP는 특수 보석 정적 CHMV 누락 예방, EQ는 **소켓 유형 적합성 허위 Gate 제거**, ER은 **이미 보유한 SimC 아이템 원본의 기본 소켓 필드**를 기존 대표 장비 경로에 연결. 이 작업들을 다시 연구할 필요가 없다. 기본 소켓만으로 충분한 경우 추가 소켓 연구도 필수 Gate가 아니다.

## 4. 실제 검증 적용 범위

- 직전 제품 코드: [focused #41985639086](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41985639086) **253 PASS/0 FAIL·DEV_LEDGER_PASS**. 문서 HEAD [#41986004769](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41986004769) 253 PASS.
- [v212 #41985639098](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41985639098): Ubuntu/Windows 각 **447 PASS/4 SKIP, Native0**. v113 API/v181 Windows/v182 UI SUCCESS. 모든 CI는 정해진 오프라인 범위이며 새시즌 READY가 아니다.
- 실 Native 역사 증거 [소켓 #41601140696](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41601140696), [영약/기름 #41666305288](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666305288)/[#41666925906](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41666925906)는 해당 게임 빌드/바이너리/프로필/옵션 범위만. **이번 P3-ES는 문서 개편만, 신규 Native·게임 HTTP·제품 코드·환경 T1 시험 0**. 이후 문서 HEAD CI 결과는 별도 확인.

## 5. 다음 가장 작은 개발 묶음

1. **INDEX의 E3→E2→E1**에서 새시즌 `v212` STAGED 종료 이유와 `v220/v196` 미발행·`v222` 미승인 G/J/F/O의 경계를 실제 코드로 분석. 각 문제를 증거 있음/전달만 누락/실제 부족/선택 항목 불필요로 분리.
2. 필요한 **B3/C4/D1·D2**만 확장해 기존 데이터·Native·SHA 캐시 재사용. 새로운 소켓 유형 인증 Gate, 효과 엔진·전체 시즌 DB·전문화×ilvl Native 전수·대규모 `v216` 재작성 금지.
3. 검증된 기본 환경의 공식 예산→정책 A 최고품질 발행→기존 `v212` 설치 READY→실제 정상 웹앱 T1을 완성. 선택 항목 부족은 해당 옵션만 보류; T1 후에 기존 적응형 `v098/v096/v094` 결합.
4. 변경마다 관련 **라이브러리 하위 항목과 16-key 호환 표의 note 링크만** 갱신. 동일 증거를 중복 수집하지 않는다.

## 6. 권한 및 새 채팅 첫 동작

격리 브랜치 문서 갱신은 `main` 병합, 원본 `v016` 직접 통합, `v003` immutable 변경, Project UI/Instructions 적용, 공식 Work OS M0/Shared State 승격, 기존 주 제품 개발 채팅의 소유권 이전을 뜻하지 않는다. M0 미통과는 일반 제품 개발 중단 이유가 아니다.

**새 채팅 첫 답변:** 격리/main HEAD 독립 조회, 실제 코드·최신 CI/Native 적용 범위, 기능별 Evidence와 Integration 차이, 즉시 필요한 E3→E2→E1 연결 및 남은 근거/로드맵·권한만 **읽기 전용 보고 후 STOP**. 사용자 명시적 ‘진행’ 전 개발·수정·커밋·수집·CI/Native/테스트·승격 금지.
