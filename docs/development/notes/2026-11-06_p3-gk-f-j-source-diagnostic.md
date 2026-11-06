# 2026-11-06 · P3-GK · 기존 F 파동 및 J 특수보석 입력 누락 T1 원인 분리

- **Capability:** `F.FLASK`, `J.GEM`, `ENVIRONMENT.WEB`
- **Keywords:** P3-GK, F-wave, existing Native, J special ID, no source recollection, T1 receipt
- **Prior evidence:** [실 T1 #42170351404](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42170351404) 는 `AUTO_F_NEXT_MEASUREMENT_BATCH_PENDING`, Native8 보고, `user_selected_gem_ids=0`, `gem_layout=false`와 J/F 공식 미확정을 기록. [P3-GJ](2026-11-06_p3-gj-original-native-evidence-audit.md)는 후속 Native 실측 원본 감사를 위한 별도 보존.
- **Decision:** `CONNECT` 기존 `v216` F worklist/파동의 per-item status·attempted·remaining 및 기존 특수 ID 수신 여부만 **기존 T1 요약 receipt**에 투영한다. 원본 Native 캐시 재수집, 효과 인증, 특수보석 ID 탐색, 구시즌 정적 G/J/F/O 추론 금지.
- **Changes:** `integration_probes/p3_fr_zero_base_t1_acceptance.py:summarize_existing_f_and_j` 는 이미 반환된 `progress/source_compilation`만 읽어 F 잔여 개수/재사용 정보 및 J 기존 특수 ID 누락이 *테스트 입력 부재*임을 구분. 최대 8개 per-item 식별 정보만 전달, 로그·예상 rating·내부 경로/시크릿 미포함. 제품 계산·설치 코드 수정 없음. 재사용 확인은 독립 원본 v277/v278 영수증의 책임.
- **Verification:** 새 코드 focused CI 영수증을 별도 확인해야 함. 이번 변경 자체는 신규 Native/게임 HTTP/T1 실행을 시작하지 않음.
- **Remaining:** F 실제 다음 파동·측정 cache, 기존 특수보석 실 ID와 이중 2차 보석 4종 실제 장착, 공식 J/F/G/O 및 v212 설치 T1 미완료. T1에 임의 special ID를 주입해 '완성'이라고 하지 않음.
- **Efficiency:** 새 수집·Native 0, 기존 결과 dict의 O(8) 소형 투영, 반복 파동 이전 정확한 결손 진단. 다음 시즌에도 소스 제공 여부를 동일하게 분리.
