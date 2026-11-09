# P1 · 검증된 O>0 설치증거 → 기존 v096 실제 사용자 프로필 연결

- **Capability:** `O.OIL`, `BUDGET.GJFO`, `PRODUCT.E2E`.
- **Keywords:** oil, v281, v278, v286, physical item, hand, exact O, v212, v096.
- **Prior evidence:** P3-CN/CO/CP/CY/CT의 v278 Phoenix Oil 주무기 고정 치16/가17은 당시 프로필·빌드 한정, v286 mask는 source-only. P3-HAR 70783 O0·수동 T3500 웹 Native2 PASS, v212 설치 Ready와 v091 source-only serializer 재사용.
- **Decision:** `CONNECT` — v212의 이미 검증된 O>0 source owner가 손별 물리 ItemID/SimC 토큰/정적 CHMV 벡터를 제공할 때만 추가 봉인하고 v096에 연결. O0 기존 v212 문서 바이트/해시 형식 그대로.
- **Changes:** v212 positive-only 공식 O 물리 메타 투영·원본 SHA/합계/손 검증, v096 fresh 서명된 O metadata↔v098 실제 `temporary_enchant`↔B/T/프로필 정합. 사전 원본 없는 항목은 변함없이 보류.
- **Verification:** 신규 Native0/외부 수집0. synthetic 설치·손/ID 변조·프로필 drift 오프라인 테스트 추가. 실 Actions 상태는 코드 HEAD 별도 조회 후 판정하며, synthetic PASS는 실제 물리 item 승인 증거가 아님.
- **Remaining:** **실제 70783 선택 기름의 게임상 무기/손/사용조건·품질·정적 O 원본 생산자는 아직 미완료**, 사용자 UI 자동등록·O>0 실 DPS Native도 미완료. 기름 O0 기본 정상 실행 보존. 첫 사용자 O>0 제품 수용 전 새 시즌 원본 소유자 연결 필요.
- **Efficiency:** 기존 v222/v212/v091/v098/v096와 v281/v278/v286 증거를 재사용; 별도 효과 모델/추가 Gate/고정 숫자 복사/전수 Native 없음. source SHA·세션별 캐시 분리 유지, main/Project UI/Work OS/소유권 불변.
