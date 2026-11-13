# SIMC 78개 요소 완료 계약 — 자동 생성

> 상태 정본: [78_ELEMENT_COMPLETION_CONTRACTS.json](78_ELEMENT_COMPLETION_CONTRACTS.json). 수동 편집 금지. 생성 명령: python integration_probes/v401_completion_contract_gate.py --write.

> 각 축의 PASS는 전체 제품 완료가 아닙니다. 역사 실행은 범용성이나 현재 시즌 검증을 대체하지 않습니다.

- 범용 기능 PASS: **7/78**
- 현재 원본 검증 PASS: **7/78** (범용 PASS와 중복 집계 가능)
- 개별 제품 통합 PASS: **0/78**
- 역사적 범위 PASS: **4/78**
- 세 축을 모두 완료한 요소: **0/78**
- 최종 제품 E2E: **PENDING**
- 다음 검토 요소: **A8** (A7 범용·현재 원본 검증 완료; 제품 통합은 별도 PENDING)

| ID | 기능 | 적용 | 범용성 | 현재 원본 | 제품 통합 | 역사 증거 | 요소 완료 |
|---|---|---|---|---|---|---|---|
| A1 | 확장팩·시즌 | BASE | PASS | PASS | PENDING | PENDING | INCOMPLETE |
| A2 | 현재 게임 빌드 | BASE | PASS | PASS | PENDING | PENDING | INCOMPLETE |
| A3 | 활성 콘텐츠 | BASE | PASS | PASS | PENDING | PENDING | INCOMPLETE |
| A4 | Blizzard 원본 | BASE | PASS | PASS | PENDING | PENDING | INCOMPLETE |
| A5 | WCL 원본 | BASE | PASS | PASS | PENDING | PENDING | INCOMPLETE |
| A6 | DB2 원본 | BASE | PASS | PASS | PENDING | PENDING | INCOMPLETE |
| A7 | 시즌 관계 검증 | BASE | PASS | PASS | PENDING | PENDING | INCOMPLETE |
| A8 | SimC 실행 식별·결과 스냅샷 | BASE | PENDING | PENDING | PENDING | PASS | INCOMPLETE |
| A9 | SimC 원본 파일 | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| A10 | 원본 통합 컴파일 | BASE | PENDING | PENDING | PENDING | PASS | INCOMPLETE |
| A11 | 원본 영수증 | BASE | PENDING | PENDING | PENDING | PASS | INCOMPLETE |
| B1 | 26 DPS 계약 | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| B2 | 목표 ilvl | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| B3 | 일반 방어구 | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| B4 | 무기 형태 | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| B5 | 무기 성능 | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| B6 | 주능력치 | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| B7 | 티어 5부위 원본 | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| B8 | 티어 4세트 착용 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| B9 | 촉매 변환 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| B10 | 대표 소켓 | BASE+USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| B11 | G 자동 예산 | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| B12 | G 시즌별 참조 | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| C1 | 일반 보석 최고품질 | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| C2 | 보석 예산 J | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| C3 | 소켓·보석 배치 | BASE+USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| C4 | 특수보석 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| C5 | 보석 색상 조건 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| C6 | 영약 F 수치 | BASE+USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| C7 | 대표 기본 영약 | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| C8 | 다른 영약 선택 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| C9 | 기름 O 수치 | BASE+USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| C10 | 기름 적용 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| C11 | 직업 무기 강화 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| C12 | 영구 마부 E | BASE+USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| C13 | 음식·물약 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| C14 | 증강 룬·기타 임시 효과 | OPTION | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| D1 | 장신구 두 개 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| D2 | 장신구 고정 스탯 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| D3 | 선택 특수효과 장비 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| D4 | 제작장비 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| D5 | 장식 최대 2개 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| D6 | 장착 부위 충돌 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| D7 | 시즌 특수 모듈 | OPTION | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| D8 | 정확한 수동 ItemID | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| D9 | 검증 선택지 자동 등록 | BASE+USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| E1 | 기본 예산 B | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| E2 | 최종 T | BASE+USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| E3 | 수동 최종 T | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| E4 | 특수장비 고정 L | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| E5 | 영구 마부 E | BASE+USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| E6 | 영약·기름 고정 하한 | BASE+USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| E7 | 후보 분배 가능성 | RUN | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| E8 | gear_* 정적 주입 | RUN | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| E9 | JSON2 정적 검증 | RUN | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| F1 | 캐릭터 정보 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| F2 | SimC 프로필 업로드 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| F3 | APL | RUN | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| F4 | 기본 전투조건 | RUN | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| F5 | 고급 전투조건 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| F6 | 실 SimC 바이너리 | RUN | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| F7 | 최종 사용자 프로필 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| G1 | 수집 스테이지 실행 | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| G2 | 기본 환경 READY | BASE | PENDING | PENDING | PENDING | PASS | INCOMPLETE |
| G3 | 개인별 환경 설치 | USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| G4 | 정적 아이템 캐시 | BASE+USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| G5 | 환경/DPS 캐시 identity | BASE+RUN | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| G6 | API 인증정보 | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| G7 | 환경 구축 UI | BASE+USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| G8 | 공식 한국어 표시 | BASE+USER | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| G9 | 시즌·SimC 갱신 | BASE | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| G10 | 오류·복구·배포 | BASE+RUN | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| H1 | 적응형 CHMV 최적화 | RUN | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| H2 | 실행 자원 관리 | RUN | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| H3 | 95% 통계 | RUN | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| H4 | 근접 대안 | RUN | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| H5 | 취소·재개 | RUN | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |
| H6 | 사용자 결과 | RUN | PENDING | PENDING | PENDING | PENDING | INCOMPLETE |

## 검증된 축의 원본·회귀 영수증

- **A1**: [CURRENT_SOURCE_REAL](notes/2026-11-13_p1-v394-a1-current-zero-source-engine-pass.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357639329)), [GENERALIZATION_REGRESSION](notes/2026-11-13_p1-v394-a1-current-zero-source-engine-pass.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43358446211))
- **A2**: [CURRENT_SOURCE_REAL](notes/2026-11-13_p1-v395-a2-current-retail-build-source-and-propagation-pass.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357639329)), [GENERALIZATION_REGRESSION](notes/2026-11-13_p1-v395-a2-current-retail-build-source-and-propagation-pass.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43358446211))
- **A3**: [CURRENT_SOURCE_REAL](notes/2026-11-13_p1-v396-a3-active-raid-mplus-current-source-scope-pass.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357639329)), [GENERALIZATION_REGRESSION](notes/2026-11-13_p1-v396-a3-active-raid-mplus-current-source-scope-pass.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43358446211))
- **A4**: [CURRENT_SOURCE_REAL](notes/2026-11-13_p1-v398-a4-blizzard-source-owner-base-scoped-ready.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43359408019)), [GENERALIZATION_REGRESSION](notes/2026-11-13_p1-v402-a4-a6-generic-scope-reassessment.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43364420119))
- **A5**: [CURRENT_SOURCE_REAL](notes/2026-11-13_p1-v399-a5-wcl-original-graphql-source-ready.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43365490208)), [GENERALIZATION_REGRESSION](notes/2026-11-13_p1-v402-a4-a6-generic-scope-reassessment.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43365447503))
- **A6**: [CURRENT_SOURCE_REAL](notes/2026-11-13_p1-v400-a6-db2-ten-table-source-provenance-scoped-ready.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43357639329)), [GENERALIZATION_REGRESSION](notes/2026-11-13_p1-v402-a4-a6-generic-scope-reassessment.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43366468001))
- **A7**: [CURRENT_SOURCE_REAL](notes/2026-11-13_p1-v405-a7-automated-current-source-selection-verified.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43375839959)), [GENERALIZATION_REGRESSION](notes/2026-11-13_p1-v405-a7-automated-current-source-selection-verified.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43375459029))
- **A8**: [HISTORICAL_SCOPED](notes/2026-11-13_p1-v407-a8-historical-source-binary-identity-and-alias-guard.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43114134208))
- **A10**: [HISTORICAL_SCOPED](notes/2026-11-13_p1-v383-a10-a11-g2-archived-native-receipt-reuse.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43114134208))
- **A11**: [HISTORICAL_SCOPED](notes/2026-11-13_p1-v383-a10-a11-g2-archived-native-receipt-reuse.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43114134208))
- **G2**: [HISTORICAL_SCOPED](notes/2026-11-13_p1-v383-a10-a11-g2-archived-native-receipt-reuse.md) ([실행](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43114134208))
