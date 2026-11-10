# P2 · 총량 비율 기반 경계 적응형 국소 후보 개선 (2026-11-10)

- **Capability:** `OPTIMIZER.POLICY`, `DEV.CONTINUITY`.
- **Keywords:** 26 DPS, fraction of freely movable B, strict T/2, feasible clipping, multiscale, exact integer CHMV, Native-call economy, search quality.
- **Prior evidence:** [기존 v290/v291 구조·최적화 품질 원칙](2026-11-09_p2-opt-reliability-first-open-search-policy.md), [국소 소진 전역 fallback](2026-11-09_p2-local-exhaustion-global-fallback.md), [실 Native10 한정](2026-11-09_p2-real-native-ten-case-region-audit.md), [기존 합성 6형상 감사](2026-11-09_p2-multimodal-equal-count-offline-audit.md). 실 Native·시즌 GJFO는 재수집하지 않음.
- **Decision:** `EXTEND` — 이미 `SCALES`가 자유분배 B의 비율임을 유지. 개별 L/E/F 하한 및 최종 T의 엄격 50% cap 근처에서 원하는 비율의 *정확한* 2-축 이동이 불가능하면 후보를 버리는 대신 **가능한 최대 이동량으로 clip**하여 합법적인 새 점을 탐색. 측정 전에는 DPS를 추정·승리 선언하지 않음.
- **Changes:** `v290`에 `_bounded_fraction_neighbors` (4축 정수 총량/하한/상한 유지), anchor 내 중복 제안 차단, 목표 해상도와 **실제 이동한 B 비율**의 로그 거리로 단계 점수 교정. 전역 pool/maximin, Native v291 실행·한 세션 2 iterations 신원, cache/취소·재개, 95%·전역 미입증 표시는 보존. `v094` 단기 legacy 기본 step100 호환성은 변경하지 않음.
- **Verification:** 코드 사전검토 및 JS 기하 사전검사 B3107과 B6214의 같은 비율, 기존 큰 단계 후보 0→새 합법 9, 엄격 T/2 유지; 새 `test_p3_hw_multiscale_policy` 2회계/0경계와 기존 국소고갈 반례 확장. **GitHub 신규 HEAD CI 결과는 푸시 후 확인**, 신규 SimC Native 0.
- **Remaining:** 9개는 *가능한 기하 후보 개수*이지 9회 SimC 실행/발견 DPS 개선 증거가 아님. 기존 합성 6형상/동일 iterations·실 Native 프로필 기반 탐색 품질 비교, 선택 편향·다봉형 발견력/종료 규칙 개선은 후속. `SCALES` 값 및 점수 가중치는 현재 구현의 휴리스틱이며 승인된 불변 최적값 아님.
- **Efficiency:** 최대 16 anchor×7 비율 단계×12 축이동의 작은 bounded 제안 공간, 동일 anchor·이동 중복 제거, 기존 관측 최소/최대 단일 집계 재사용. 신규 Native/DB 수집/상태 파일/캐시 키 변경 없음; 정수 후보의 정확 SimC 인증 경로 재사용.
