# v350 — 승인된 환경 구축과 사용자별 소켓·영약·기름 분리 및 검증 설치 연결

- **Capability:** `ENVIRONMENT.WEB`, `PRODUCT.E2E`, `DEV.CONTINUITY`.
- **Keywords:** v350, user approved, common season environment, per-user total sockets, special gem, chosen flask, oil, verified v212 variant, J/F/O, B/T, resume, fail-closed.
- **Prior evidence:** 사용자가 승인한 두 가지 변경: 첫 시즌 선택은 동일 시즌 캐시를 재활용하는 자동 구축이며 과거 시즌 회계 복사가 아니다; 보석 소켓 수·특수보석·영약·기름은 시즌 환경 준비가 아니라 최적화 조건이다. [v349 사용자 Windows 화면 피드백](2026-11-12_p1-v349-user-season-progress-sockets-sourceitem-ux.md), [v348 소유 키 WinCred 연결](2026-11-12_p1-v348-user-owned-credentials.md); 검증 미완료 현 빌드 `12.1.5.70783`의 시즌 연결은 여전히 PENDING이다.
- **Decision:** `CONNECT` — 시즌 환경 버튼은 내부 대표 보석4·무기 기름 없음·기본 영약 검증만 요청하고 사용자 개별 소켓/아이템 선택을 소비하지 않는다. 최적화 사용자 양식에 소켓 전체 수(특수보석 포함), 특수보석 선택, 검증된 영약 선택 및 기름 선택/정확 ID 고급 입력을 둔다. 사용자별 변경 구성 검증·준비는 명시 버튼에서만 기존 v216 엔진으로 수행하고 그 결과에 필요한 Native는 사용자 확인 후 기존 상한 내에서 실행한다.
- **Changes:** `runner/webui/index.html`에 사용자 입력 이동 및 시즌 공통 버튼 명확화, `runner/webui/app.js`에 별도 시즌 공통/사용자 구성 요청 분리·소켓/영약 값 전달 및 세션 복원. `v113` Pydantic 사용자 선택과 exact v212 installed SHA + snapshot 소켓·특수보석·영약·기름 선별; 서로 다른 설치본·과거 카탈로그/원본 값 폴백 금지. 이용할 수 있는 정확한 설치본이 없으면 HTTP 422로 세션 생성 전 차단. 기존 원본 v216 보석 J·고정 F/O·B/T 계산과 SimC 담당 관계 자체는 변경하지 않음.
- **Verification:** Windows/Linux v113/v114, v181 실제 소스 ZIP·HTTP, v182 UI, v180/177/167, ledger 수행 전 **PENDING**. 새 Native 증거 0. 원본 통합 성공과 실사용 UI 결과는 CI PASS와 별개로 기록할 것.
- **Remaining:** 현 게임 빌드에 검증 설치본이 아직 없어 사용자 선택 8소켓·특수보석의 실제 G/J/F/O READY 또는 26 DPS Native는 미실증. 일반 아이템 이름 등록이 완결되지 않은 특수보석/영약/기름은 고급 재현용 ID 경로만 유지하고, 미확정 선택은 차단한다. 개별 선택에서 소켓·영약 변경 시 자동 승인하지 않으며 명시 검증 준비가 필요하다. 기존 검증 내역/세션을 변경하지 않는다.
- **Efficiency:** 원본 DB2·SimC 캐시 재사용; 사용자 선택이 동일하면 기존 SHA를 재사용한다. 새로운 시즌 원본 수집은 사용자가 환경 확인/선택 구성 준비를 클릭할 때만, 신규 Native는 검증 준비에 명시 승인한 기존 정적 G/F/O 최소 범위에서만. 사용자 세션 검증 및 원본 일치 조회는 Native0; DPS 연산은 실행 버튼을 별도로 눌러야 한다.
