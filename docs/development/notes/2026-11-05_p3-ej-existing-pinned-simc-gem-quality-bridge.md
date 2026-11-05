# 2026-11-05 · P3-EJ · 기존 v230 품질 속성을 선택 보석 환경 입력에 재사용

- **Capability:** `J.GEM`, `SOCKET.LAYOUT`, `SOURCE.SEAL`, `ENVIRONMENT.WEB`
- **Keywords:** P3-EJ, v229, v230, v256, gem, crafting_quality, highest quality, optional source, v217, cache, v216, v098
- **Prior evidence:** [PROTOCOL](../PROTOCOL.md) → [INDEX](../INDEX.md) → [P3-EI](2026-11-05_p3-ei-sealed-gem-property-to-season-input.md) → [P3-BX](2026-11-03_p3-bx-simc-socket-native-contrast.md). 기존 v230 파서는 `item_data.inc`의 정확 요청 item ID에 대해 `quality` 및 `crafting_quality`를 소스 SHA/SimC 빌드와 묶어 추출하고, v216의 원래 v256 전체 item seed는 이미 봉인·바이트 검사한다. 기존 v221은 물리 GemProperty join을 별도로 보유.
- **Decision:** `CONNECT` / `REUSE` — 원래 v256 full seed가 존재하고 실제 선택된 보석 ID가 v221 join에 연결된 경우에만 v230 결과를 원래 v217에 작은 `selected <=64` source-only stage로 봉인/재사용. 새 아이템 수집·품질 기준 추정·Native·효과 인증 Gate·전체 젬 DB는 `STOP`. `quality`/제작 품질 값만으로 최고 품질/효과 동일성/특수 역할/소켓 합법성 자동 승인 금지.
- **Changes:** 기존 v216 preflight에 내부 `pinned_gem_simc_source_folder` 선택 인자와 v230→v217 캐시 projection을 CONNECT; 정상 zero-history v216은 이미 수집한 v256 원본 폴더만 전달, 없으면 해당 품질만 PENDING. v221 물리/색상/최소 ilvl 자료와 동일 선택 ID의 v230 품질을 `selected_v221_gem_item_relation_unadmitted`에 투영하고 v098 source-only 설정의 독립 진단에 전달. 기존 v271 정확 특수 1개, J와 구 시즌 별도 기본 및 DPS 캐시 보존.
- **Verification:** 새 합성 오프라인 회귀에서 동일 선택3 ID의 v230 원래 품질/제작품질, original v217 staged cache hit(추가 parser 0), v216→v098 source-only 투영, 선택 ID 변경/불일치 차단 확인 예정. 신규 실행 `NOT_RUN/NOT_VERIFIED`; 이전 P3-EI [focused 247 PASS](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41967184128)·v212 양 OS 442 PASS/4 SKIP는 역사 범위 재사용, 신규 실제 Native/외부 HTTP 0.
- **Remaining:** 동일 효과/조건을 입증할 수 있는 기존 속성을 추후 더 연결하고 최고 품질만 공식 발행; 실제 특수 효과 역할·소켓 적법성/SimC-effective J 및 나머지 G/F/O·v220/v196 정책 A 발행·v212 READY/T1 미완료. 원본 품질 관측은 공식 J 인증/READY가 아님.
- **Efficiency:** 소스 없는 경우 추가 I/O 0, 선택 보석 있는 경우 original v230 1회 파싱을 v217 keyed stage에 봉인해 이후 동일 입력은 캐시 재사용. 새 시즌 반복 조회·아이템 전수 DB·Native/HTTP 없음. main/v003/v016/Project UI/Work OS·주 제품 개발권한 불변.
