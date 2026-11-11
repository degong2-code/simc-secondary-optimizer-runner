# v319 신규 풍운 수도사 프로필 기반 v290/v318 Native A/B — 실행 계약

- **사용자 직접 승인:** 모든 후속 실제 Native 알고리즘 비교에서 새로운 **전문화 사용자 프로필을 환경 구축 엔진 v113→v216/v217→v212→v098으로 직접 생성**한다. 역사 완성 프로필·최고 CHMV·DPS 결과는 입력에 주입하지 않는다. 단일 실험 내 v290/v318은 동일 새 profile SHA 사용.
- **이번 신규 전문화:** `monk/windwalker` (풍운 수도사), v313 4전문화 및 v314 8전문화 어디에도 없는 대상. 인간, ilvl334, 수동 최종 T3450, 보석 일반4/특수 없음, Oil0, 치/가/특/유 최종 상한45%, 단일 타깃300초, 기본 제공 특성·장신구. 실제 제품 사용자 source controls 및 검증된 시즌 데이터 사용. 기존 70783 source/Native 프로필 파일 재생·재사용 아님.
- **구현:** [한 번만 실행되는 source-first A/B](../../../integration_probes/p2_v319_new_windwalker_v290_v318_real_once.py); 64 Native/arm, 총128 최대; 각각 35 scout/320 confirm, v316 timing optin. `v291` 별도 seal/cache-only 재생 0 new Native, 각 arm 원본 input·JSON2·journal·timing ZIP 보존 7일. 환경 G/J/F/O 실 Native 상한3, 일치 확인 후 동일 `context` 재사용. current season live build drift·인증정보 미비 시 원문 차단.
- **공정 비교:** 양쪽 Native 호출수 동일과 **실제 총 iterations 동일 여부**를 별도로 검사한다. 상태가 다르면 절대 같은 계산 예산의 우위로 해석하지 않는다. 양쪽 320 최고 DPS±SEM·CHMV·실제 실행시간·원본 SHA·명목95 및 탐색후 최고선택 편향 한계를 보존. 단일 신규 전문화라 26 DPS 일반화/전역 최적/제품 승격 불가. 추가 비교가 필요하면 다음에도 *또 다른 신규 전문화 프로필*을 생성한다.
- **증거 상태:** 코드·시나리오·오프라인 가드 및 push-trigger [Actions 워크플로](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/workflows/p2_v319_new_windwalker_native_ab_once.yml) 등록 예정. 이 노트는 **실제 실행/성공/Native PASS 증거가 아님**. Actions run ID·job 상태·artifact 원본을 조회 후 결과 업데이트.
- **효율:** v290 원형 유지, 추가 120 iterations 단계 없음, 원본 26/1008 전수 재실행 없음. v318 실효성은 선행 focused synthetic PASS + 새 전문화 독립 Real A/B 이후 판정.
