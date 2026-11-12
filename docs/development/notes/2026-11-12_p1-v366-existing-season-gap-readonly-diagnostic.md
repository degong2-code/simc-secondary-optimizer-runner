# v366 — 기존 v163 시즌 소속 증거 갭의 비수집 국소 진단

- **Capability:** `ENVIRONMENT.SEASON`, `DEV.CONTINUITY`, `PRODUCT.E2E`.
- **Keywords:** v366, P1-A, source gap, v163, WSE, v274 compiler missing, v216 progress, no Native, read-only.
- **Prior evidence:** v365 parser [4/4 SUCCESS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/43203517263), v364 UI 7/7; 현재 사용자 Windows `SOURCE_SEASON_JOIN_PENDING`의 원본 JSON 및 봉인 receipt는 GitHub에 없음. 실제 로컬 인증 원본 미열람.
- **Decision:** `CONNECT` — 새 수집/인증/진입점/Gate 없이 이미 생성된 v163 후보·선택형 v274 컴파일러 상태·v216 진행 JSON에서 **명시적으로 지정된 필수 장비 ID**의 미해결 조건만 안전하게 출력. v163의 후보 부재는 시즌 부재 판정 아님; WSE 양의 ID는 해석·승격 금지. J/F/O는 v163 장비 후보 밖임을 표시.
- **Changes:** `integration_probes/p1_v366_existing_source_gap_report.py` 순수 CLI 및 `tests/test_p1_v366_existing_source_gap_report.py` 4개 국소 테스트 추가. 입력 JSON은 읽기만 하고 원본 SHA256 식별·스키마·파일 크기·심볼릭 링크·최대 64 ID 검사. 원본 내 임의 키·자격정보·경로를 보고서로 복사하지 않음. `runner/v163/v216/v274`, v212, v290, 웹 UI·캐시 변경 없음.
- **Verification:** 로컬 Python unittest **4 PASS/0 FAIL**(2026-11-12); 신규 GitHub Actions·Native·외부 수집 **0**. 실제 사용자 PC v217 원본 입력 **미실행**, 시즌 JOIN/READY 여전히 PENDING.
- **Remaining:** 사용자 환경의 실제 v163 후보 파일, v274 `source_compilation`, v216 `source_progress` 및 정확한 필수 장비 ID/원본 stage SHA를 같은 빌드로 확보·대조해야 실제 누락 조건 판단 가능. 이 CLI는 v217 seal을 재검증하지 않으며 SHA는 읽은 파일 정체성일 뿐 출처 승인 증거가 아니다. 이후 필요하면 별도 권위 있는 게임 조건 증거 최소 확보.
- **Efficiency:** 새 HTTP/Auth/SimC/Native/전체 CSV scan 없음; 선택된 ID 최대64, 소규모 기존 JSON만 1회 열람; 입력 파일 무변경. 기존 v217 봉인·캐시 재사용 원칙 보존, `main`/공식 승격 불변.
