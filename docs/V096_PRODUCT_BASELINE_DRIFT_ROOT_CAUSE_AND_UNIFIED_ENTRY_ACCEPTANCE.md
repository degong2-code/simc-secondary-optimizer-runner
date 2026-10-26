# v096 — 개발 기준선 혼선 원인 감사 및 공통 제품 진입점 통합

**2026-10-26 KST · 사용자 요청: 기능 중복 검증보다 제품 통합 우선.**

## 1. 혼선 원인: 권한 문제가 아니라 다층 문서 및 해석 불일치

1. **Project Instructions 우선순위 미갱신:** 현재 대화에 공급되는 프로젝트 지침은 여전히 `SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.2_PROJECT_SOURCE_REPLACEMENT.md`를 최신 승인 Source로 지목한다. 사용자 2026-10-26 직접 승인 `T=G+J+F+O`와 신규 v1.3은 내용으로 확정됐지만 **Project UI에 실제 정식 Source 교체가 확인되지 않았다**. 구형 우선권 문장은 후속 채팅에서 혼란을 일으킬 수 있다. 직접 사용자 승인은 유효하고 기존 MAIN 반복 승인 요구 사항은 이번 정책 변경에 대해 해제된다.
2. **v1.3 파일도 '정적 스냅샷':** 전체 교체본 최상단은 v092, §14.2의 예전 실험 상태는 v059 사례, §18도 'GitHub 최신 v059'로 남았다. §14가 최신 상태는 GitHub `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md`를 확인하라고 경고하지만 사람/AI가 v1.3만 읽으면 상태가 오래됐다고 잘못 결론 내릴 수 있다. **v1.3은 승인 설계 계약, CURRENT는 실제 개발 진행 상태**로 역할을 고정해야 한다.
3. **최신 단일 시험을 제품 전체로 확대해석한 조정 실패:** v092~v095가 Fury 중심의 실험인 건 사실이지만 v071-v086에서 이미 Rogue, Elemental Shaman, BM Hunter, Fury Warrior, Retribution Paladin, Frost Mage의 실제 SimC 증거를 확보했다. v078/v082/v083/v084는 정적 예산 → 실제 SimC 후보 → v015-derived scout → DPS·SEM 및 SHA cache까지 증명했다. BM Hunter의 초기 talent/buffed_stats 오류는 v080/v081에서 static-c와 출력 버프 수치로 분리·수정했고 v086 random-secondary gear 교정, 과거 실패영수증은 그대로 보존했다. **이를 모두 미검증으로 취급하거나 새 전문화 전체 Native 시험부터 다시 하자는 것은 부정확하다.**
4. **계보·실험 완료/원본 제품 통합을 혼동:** 별도 원본 제품 최신은 사용자 보고 `v016_SCENARIO_CONTRACT`이고 **원본 바이트·receipt 독립 확인 전**. 격리 v059~v096 코드/Actions 성공은 원본 v015/v016 직접 소스 합치기 완료나 공식 Windows GUI 완성을 뜻하지 않는다. 공식 Work OS M0 운영 Gate는 제품 개발 단계와 분리되며 이 우선순위 착오의 원인/차단 Gate로 취급하지 않는다.
5. **후속 시험 중심 로드맵 편향:** 'v095 SEM 정밀도 → v096 반복횟수 자동 증가'는 국소적인 기술연결로 가능하지만 지금 필요한 것은 '이미 실증한 계산·입력·캐시·탐색을 사용자 입력 하나에서 전체 실행으로 이어가는 것'. 더 많은 정밀 SimC는 미검증 실제 정확성 결함이나 사용자 요구가 생겼을 때만.

**결론:** Project Source/Instructions 미반영은 실질적 원인 중 하나이지만 **최신 CURRENT 및 과거 성공증거를 묶어서 읽지 못한 개발 판단**이 직접 원인이다. '더 많은 과거 전문화 반복 Native' 혹은 '95%를 넘는 신뢰수준·SEM 반복세분화'로 해결할 문제가 아니다.

## 2. v096 구현: 기존 제품 기능을 단일 입력으로 재사용

신규 **`runner/v096_unified_product_entry.py`**는 사용자 제공 단일 JSON manifest에 포함된 정확 SimC `profile_simc`, typed `scenario_json`, 장비 `fillers_json`, 선택 `static_cache_json`, 무기 구조·오일 적용 손, 정적 영약 F, 초기 B 후보 2개, 정확 SimC 바이너리/기대 revision, Native 총호출 제한, 결과 폴더를 기존 모듈에 전달한다. 각 입력 파일 경로는 manifest 기준 상대경로 또는 절대경로 허용.

- `--plan-only`: **SimC 0회**, 실제 전체 소스 SHA, scenario, 15/16 슬롯·selected options, tier4/2trinkets, 대표 ilvl 참조 B, 고정 O, 최종 T=B+O, B 후보 하한 L/상한, SimC binary SHA, 신규 호출 예산을 한 번에 점검. 성공하면 source-bound 준비 정보를 출력하며 출력 디렉토리를 생성하지 않는다.
- `--manifest ...`: 사전검증 통과 후 기존 **v094**로 위임해 입력 생성·DPS·95% SEM·캐시·세션 봉인·중단 재개·cancel file·출력 파일을 실행. 이 모듈에 다른 SimC 실행기/탐색기/효과 모델을 추가하지 않는다.
- `--cache-only`: 기존 exact JSON2 + 입력 SHA 검증 재개만 수행. 존재하지 않는 Native 결과는 fail-closed.
- 사용자의 공식 총량 **T=G+J+F+O**, 현재 실행 경로의 내부 배분 B와 고정 벡터 O를 별도 표시. 97% 비교 출력 없음.
- **검증된 기존 두 다른 archetype을 재사용한 Source-Only 테스트**: 334 Fury 판금/dual twohand/오일2, B3350/O64/최종 T3414; 334 Frost Mage 천/onehand + nonweapon offhand/오일1, B3150/O32/최종 T3182. 유효한 다른 영약 F 벡터·소스/gear/options의 기존 SHAs, Native 실행 0회. 이전 v071-v086 진짜 Native 영수증은 그대로 보존, v096 새 Native이라고 주장하지 않는다.
- **한계:** 이 경로는 기존 **opt-in ilvl reference B**를 사용한다. 완전 exact Native G 자동 구성/수동 inclusive T/사용자가 편하게 선택하는 GUI/원본 v015-v016 실제 파일 통합은 아직 아니다. 전체 27+ 전문화를 새 테스트했다거나 전역 최적을 찾았다고 주장하지 않는다.

## 3. 검증과 결과

[Actions #40271512368](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40271512368) **SUCCESS; 545 tests = 543 PASS / 2 역사 SKIP / 0 FAIL**, existing pilot PASS. v096 신규 source-backed 두 전문화 실행 전 사전검사, SHA 변조·허가 Native 호출 상한 초과 차단, 잘못된 manifest 거부. **Actions Native0회**. Artifact `v096-unified-entry-proof-40271512368` ID 12628432935, SHA `b9dd47bca288f07c32840e9d6ac734f0712cae893986c71c95bcee168917f41f`.

## 4. 우선순위와 실제 적용 상태

**즉시 P1: 검증된 공통 제품 연결** — 사용자 입력 → 정확 source/profile & selected IDs → 총량과 L/O → 기존 v065 탐색 → SimC Native·통계 → 결과/캐시/재개. 기존 이미 측정된 전문화·장비 구조는 중복 새 Native 대신 문서/소스 테스트와 진짜 필수 gap만 새 Native.

**P2: 남은 실제 인터페이스 결함** — exact G/manual final T 경로, orig v015/v016 코드 바이트 계보, 사용자가 반복 실행 가능한 입력/UI/출력 패키징을 명확히 분리. 새 기능/성능 미세조정은 안정적인 전체 실행 뒤에 우선.

**P3: 이후** — 충분히 넓은/세밀한 탐색, SEM 기반 반복 실행량 조절, 범용 탱커/힐러 및 기타 미검증 새 스키마, 성능·UX. 다만 실제 정확성 결함은 P1에서도 즉시 수정.

**Project UI 적용 미확인:** 사용자가 승인한 v1.3 Source 내용과 Project Instructions의 v1.2→v1.3 우선권 변경은 **실제 UI 편집 권한/적용 영수증 확인이 안 됐으므로 미적용/미검증**. GitHub 개발 문서 갱신은 Project Source 교체를 대신하지 않는다. 별도 Windows 공식 Work OS Shared State도 실제 수정 안 됨; 운영 M0 PASS나 `main` 승격을 주장하지 않는다.

**간명한 새 프로젝트 우선권 문장(실제 Project Instructions 편집 시 반영):**
> 제품 설계 기준은 사용자가 2026-10-26 승인한 `SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.3_APPROVED_OIL_INCLUSIVE_PROJECT_SOURCE_REPLACEMENT.md`이며, 공식 총량 T=G+J+F+O, 내부 B=G+J+F, O 고정·95% 판단이다. v1.2는 역사 자료. **구현/시험의 최신 상태는 매번 GitHub 격리 브랜치 `docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md` 및 Actions/Native 실제 영수증**에서 확인한다. 이전 여러 전문화 Native 검증을 보존·재사용하고 최우선 과제는 기존 기능의 제품 통합이다. 사용자 승인 없이 불필요한 SEM 정밀 실행 또는 기존 전문화 전수 재시험을 다음 개발 단계로 선택하지 않는다. 원본 v015/v016 제품 계보·공식 Work OS 상태와 격리 연구 코드를 혼동하지 않는다.

**이 문서는 증거 기록과 적용 제안이며 Project UI/Work OS를 실제 수정한 완료 영수증이 아니다.**
