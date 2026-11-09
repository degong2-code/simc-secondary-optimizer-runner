# P1 · 죽음의 기사 룬벼리기 사용자 선택과 무기 마부 연결

- **Capability:** `CHARACTER.PROFILE`, `PRODUCT.E2E`.
- **Keywords:** deathknight, frost, unholy, runeforge, enchant_id, weapon, SimC.
- **Prior evidence:** v132 DK 냉기 무기 enchant_id 3368/3847, 부정 6245; v176 26 DPS 물리 Native 성공은 새 룬 선택 적용 증거가 아님. v055/v098/v106/v113 기존 무기 직렬화·세션·웹 UI 재사용.
- **Decision:** `CONNECT` — 사용자 명시 DK 룬을 해당 무기의 기존 SimC enchant_id로 전달. 룬 효과·DPS는 SimC에 위임하고 기본 룬/E를 추정하지 않는다.
- **Changes:** v294 클래스/손/ID·다른 마부 충돌검사, v106→v098→웹 2손 선택·세션 복원. 선택마다 프로필/세션 SHA 분리, 기존 미선택 세션 변화 없음.
- **Verification:** 새 Native 0, 변경 범위 focused/web CI 판정은 실행 영수증 확인 후 별도 기록. v294 및 웹 오프라인 회귀 추가.
- **Remaining:** 실제 70783 DK 룬 적용 Native·사용자 Windows 클릭 미증명. O>0은 기존 v281/v278/v286 물리 ID/손/정적 O 검증 및 v212/v096 접합 미완료; O0 유지.
- **Efficiency:** 신규 효과 모델·최적화 엔진·전수 Native 없음. 기존 serializer/캐시 재사용. main/불변 원본/Project UI/Work OS/주 개발 채팅 소유권 불변.
