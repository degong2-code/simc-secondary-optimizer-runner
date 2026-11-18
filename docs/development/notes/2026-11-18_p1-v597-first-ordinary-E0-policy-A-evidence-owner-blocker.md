# P1 v597 — 일반 E0 반지 실행의 첫 생산자 단절 확인

2026-11-18 · 격리 브랜치 probe/chat-cache-v035-20261024. 실제 코드·역사 영수증 읽기, 별도 코드 수정/Native/HTTP/DB2 없음. **새 일반 E0 Native DPS E2E는 PENDING.**

## 정확히 확인된 기본 ZERO-SOURCE 경로

1. runner/v216_environment_build_coordinator.py의 _fresh_original_default_base_install_inputs는 trusted_policy_A_receipts_by_id={}를 반환한다. 일반 Windows v113 환경 빌드는 verified_install_provider가 없으면 이 기본 경로를 사용한다.
2. 동일 v216의 _fresh_source_owner_merge_policy_A_original_source_relation은 봉인 v217에서 가져온 source_relation 분야만 병합한다. 이는 원본 소스/ID/물리 슬롯 관계 증거이지 전체 Policy A 승인 영수증이 아니다.
3. runner/v220_catalog_auto_admission.py의 decide는 동일 item/season/build/catalog identity에 대해 source_relation, simc_input, product_input, chmv_budget 네 분야가 모두 필요하다. 따라서 기본 경로는 일반 E0 포함 영구 마부에 대해 세 분야가 미충족이다. 첫 미충족은 **simc_input**, 추가로 product_input와 chmv_budget가 미충족이다. 기존 코드 진단 V217_SOURCE_RELATION_ONLY_OTHER_PROOFS_PENDING과 일치한다.
4. v196→v212는 네 가족 및 품질/적용 조건이 검증된 항목만 published_verified_options에 등록한다. v113은 설치된 명시적 네 스탯 E0·CHMV SHA 반지만 installed_E0_final_finger_candidates로 반환한다. 등록 자료가 없으면 정상 BASE G/J/F/O·기본 SimC를 차단하지 않고 E0 선택지만 보류한다.
5. v596 실행 소비자(v098 최종 실물 반지·마스크 → v096 정확히 한 enchant_id, 예산·프로필·캐시 SHA → v093/v094 SimC)는 **오프라인 회귀 PASS**. 하지만 검증된 실제 일반 E0 등록 항목의 존재와 신규 Native E2E는 입증되지 않았다.

## 기존 Native 증거의 한계

- v529/v530 70783 생존 사냥꾼·finger1·실물 반지 268266·장신구 270175/270173·특정 SimC 바이너리 E0 정적 Native는 원본 한정 증거다. v532/v533/v534도 각 정확한 E+/수동 T 범위만 입증한다. 기존 좁은 런타임 경로는 유지하되 전 전문화/시즌/최고 품질 일반 Policy A 등록으로 확대하지 않는다.
- v570 Actions #44074372451은 실제 BASE 사용자 Chrome→SimC DPS 64회 PASS이나 공개된 요약 로그에는 설치 v212의 개별 published_verified_options 항목이 포함되지 않는다. **임의 사용자의 실제 설치 파일에 존재하는 E0 ID/개수는 현재 미확인**이다. 여기서 단정한 것은 최신 기본 코드의 확정적 원본 생산 범위다.

## 바로 다음 유효한 작업과 STOP

1. 먼저 실제 같은 빌드의 설치 v212 published_verified_options / optional_other_proof_pending_by_id와 봉인 v216/v217/v220 기존 증거를 읽고, E0 반지 한 정확 ID의 첫 미충족 가족을 확인한다. 실 설치 파일이 없으면 새 원본/가상 승인 데이터를 만들지 않는다.
2. 이미 신뢰된 원본만으로 simc_input(정확한 ID/slot/SimC 입력), product_input(최고 품질의 동일 효과·사용조건/적용 범위), chmv_budget(명시된 E0 스탯별 소유권·SHA) 중 실제 부족한 소비 연결만 채운다. **효과 발동 인증이나 새로운 Gate는 만들지 않는다.** 원본이 부족하면 해당 옵션만 PENDING.
3. 실제 v212 승인·설치 E0가 확인되면 v113→v098→v096 사용자 한 반지의 DPS/SEM/95%·프로필 SHA·캐시/재개를 기존 Native 재사용 우선으로 확인한다. 동일 범위 캐시가 없고 실행 결과가 필요할 때만 bounded Native 최소 1건, 좁게 PASS한 뒤 STOP.

기존 v567/v570/v572/v581 역사 PASS 재실행 금지, 전 마부×26전문화 Native 전수·새 탐색기·대형 원본 재수집 금지. 공식 15/78 COMPLETE 및 full_product_e2e=PENDING 불변. main·v003 immutable·Project UI·Work OS 및 기존 주 제품 개발 채팅 권한 불변.
