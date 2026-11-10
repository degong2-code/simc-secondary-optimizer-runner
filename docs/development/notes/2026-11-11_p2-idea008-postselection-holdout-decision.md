# 2026-11-11 P2 — IDEA-008 최종 의사결정 선택편향 독립 확인 아이디어

- **Capability:** `OPTIMIZER.POLICY`, `DEV.CONTINUITY`.
- **Keywords:** IDEA-008, winner's curse, post-selection, independent seed, SimC JSON2, sealed shortlist, selected 95, familywise.
- **Verified historical cause:** v313 [#42843524976](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42843524976) 8/8; v314 [#42846073820](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42846073820) 15/16 FULL + 1 partial. 완전 23조건 선택쌍 명목95 분리 0. **선택편향/다중비교 미보정**, 전역 최적 보장 없음.
- **NEW idea versus existing:** `IDEA-005`는 짝시드의 실제 공분산 검증, `IDEA-001`은 반복/정밀 예산, `BENCHMARK`의 새 프로필 홀드아웃은 정책 일반화. 이 아이디어는 **동일 새 프로필에서 최종 선택했던 CHMV 후보를 별도 미사용 SimC 표본으로 재검증**하는 독립 결정 단계라 중복되지 않음.
- **Work completed:** IDEA-008 상세 독립 파일, README 등록·심사·반증, BENCHMARK 통계 경계 반영. 아이디어 문서 등록만, 새로운 Native 실행/구현 PASS 아님.
- **Blocked:** 원본 v317 Native 계측 영수증 확인 전 이 아이디어 Native 실행 금지. 신규 정확 Native seed/iterations identity의 SimC 입력은 검증 선행 필요. 제품 v290/v291/default Windows 웹은 불변.
- **Next:** v317 실제 워크플로 run id/Native trace 증거 확보 → 독립 선택/홀드아웃 차단 오프라인 계약 → 이전 원본 캐시와 충돌 없는 소수 원본 Native 실증 → 동일 cost 실측 ablation.
- **Efficiency:** 독립 새 탐색 엔진/새 시즌 GJFO 중복 구축 없음. 한정 shortlist와 단일 v291 budget owner, 추가 Native의 실제 의사결정 가치 검증 후 옵션 승격. 10분 초과만으로 폐기하지 않음.
