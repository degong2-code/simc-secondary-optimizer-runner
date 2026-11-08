# P3-HN · 실제 G/J/F/O source→v212 installed READY 1건 (2026-11-08)

- **Capability:** `ENVIRONMENT.WEB`, `SOURCE.SEAL`, `PRODUCT.E2E`
- **Keywords:** P3-HN, real native, GJFO, J nominal, v271, v216, v222, v212/v217, G2850, J92, F165, B/T3107, next season engine
- **Prior evidence:** P3-HJ/HK packaged 명목 J owner와 P3-HL exact-build 설치 캐시; [이전 실제 T1 #42332836316](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42332836316) **FAILURE/NOT_READY**(원래 G2850/F165 Native3, J 부족). [P3-HK offline #42449427160](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42449427160) 400 PASS/2 SKIP, 실제 READY 미증명.
- **Decision:** `CONNECT` — 원래 `v113`에서 이미 사용 중인 정확한 게임 빌드의 `v271.load_packaged_season_nominal_source`를 실제 T1의 기존 `v216` Build에 전달. 새 J 계산/품질 인증/SimC 보석 효과 Gate, 새 최적화 엔진 또는 다른 빌드 하드코딩 금지.
- **Changes:** 격리 코드+테스트 `68daa4801709b7c2e03b92e2fb5971ea24020336` (`integration_probes/p3_fr_zero_base_t1_acceptance.py`, `tests/test_p3_gq_original_gjf_one_shot.py`), 선택한 특수보석이 있고 같은 빌드 패키지 원본이 있을 때만 기존 J source를 전달. 원본 없는 미래 빌드는 PENDING. T1 진단에 G/J/F 실제 source-owner 결과·상태 추가. 기존 v216/v222/v212/Native 엔진 무변경.
- **Verification:** [offline #42460176730](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42460176730) **404 tests = 402 PASS/2 SKIP/0 FAIL, DEV_LEDGER_PASS, Native0**. 기존 request JSON의 형식만 바꾼 trigger `c7fa97894f1fe6404b5cdda09e852e19b1609005`; 의미/ID/Native 상한 동일. [**실 #42460255527**](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42460255527) SUCCESS **ZERO_BASE_T1_PASS**, `source_stage=EXECUTED_AND_SEALED`, `source_compilation_missing=[]`, `zero_history_requires=[]`, `installed_status=FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY`, **environment_ready=true/installed=true**, 실제 Native **G1+F2=3회**. Artifact `13608778148`의 실제 JSON receipt 확인; ZIP은 감사용만, 휴대 캐시가 아님.
- **Remaining:** 실 **한 조건 70783/ilvl334/징벌 성기사**에 한정. 같은 빌드 정적 재사용은 가능하지만 미래 시즌 J 데이터 자동 공급·동일 콘텐츠의 패치간 증분 재봉인, 다른 ilvl/전문화 실제 G, 검증 선택지 **published count**와 특수보석 여러 선택 UI, 사용자별 `v098/v096/v094` 실제 READY→DPS E2E는 미완료. 특히 원래 v096은 옛 session v216/v223 receipt만 받아 **새 fresh v212 installed 타입 연결은 별도**. 기존 실패 영수증은 삭제하지 않음.
- **Efficiency:** 새 SimC 바이너리 컴파일 0; P3-FW 기존 `c20e2ad52e4c33711f74272309a5748125175fe8` 바이너리 SHA256 `980ed4640cecc3ed78b34ed0dc0363dbff2ed7d703174e9cc01f09d18570d36b` 재사용, G1/F2/O0 상한. T1 1회만 재검증, 기타 동일 Native/CI 소모 방지. `main`·v003 immutable·Project UI/Work OS·주 제품 개발 소유권 불변.

## 공식 설치 예산 / provenance — 단일 시즌·프로필

| 조건 | 관측된 공식 값 | 신뢰 범위 |
|---|---:|---|
| 게임/대표 | `12.1.5.70783`, Ret Paladin dwarf, ilvl334 | 현재 KR Retail; 해당 대표 장비만 |
| G | **2850** | Native1; SHA256 `d32a24587ea574efa5f65b6e0c121dad84d6598e176b78435ed65897925e3837` |
| J | **92** | 특수 `240967` 제외, 최고품질 일반 4종 각23; SHA256 `ee87a4b510088853e2724ebc86e6cf20c994beef4bc0eb3f188baa93a4f2ad8d` |
| F | **165** | 영약 물리 ItemID `241324`, Native2; SHA256 `cd8a9e7799fcdf4743c134cc866cbd5759dfd48f556b9de3194cacb757a10c8c` |
| O | **0** | 정확히 기름 미사용 |
| **B / T** | **3107 / 3107** | 원래 v222 공식 `B=G+J+F`, `T=B+O` |

**Next CONNECT:** 동일 설치의 `v217` 원본/단계영수증까지 검증하는 기존 `v216.find_verified_installed_season_environment`를 재사용하여 **새 fresh v212 installed 타입**을 기존 `v098/v096/v094` 사용자 실행 및 별도 DPS 캐시에 결합하고, 오프라인 다음 실 사용자 E2E 한 건만 한다. 실 Native G/F를 증거 없이 반복하지 않는다.
