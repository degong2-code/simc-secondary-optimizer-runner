# 검증된 시즌 환경 구축 결과의 영구 보존 — 범위 영수증

GitHub Actions 아티팩트 유효기간이 끝나도 이미 성공한 환경 Build의 **수치와 성공 범위**를 재확인하도록 만든 작은 Git 추적 원본이다. 전체 시즌 DB나 완전한 환경 설치 묶음을 대표하지 않는다.

## 70783 / Ret / ilvl334 / 일반 보석4

- 원본 [Actions #42664089225](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42664089225): SUCCESS, 실제 환경 Native 3, verified READY·사용자 프로필 준비.
- 원본 아티팩트 ID 13694734495, 만료 예정: **2026-11-14 17:24:24 UTC**.
- 원본 1,217바이트 JSON의 SHA256: **48d19e40618d61ba7d6c6e206504c3346a9e34d2c05e98369ecd5986aa73c987**.
- 원본 Actions ZIP의 SHA256: **c674c0c944905f66c42b1f60bea708c71e9d3f4bb7898e533ad34c61dec198b4**.
- Git 영구 복사: [70783_ret334_ordinary4_p1_scope_receipt.json](70783_ret334_ordinary4_p1_scope_receipt.json).
- 적용 범위: 당시 12.1.5.70783, 목표 ilvl334, Ret334 대표 G2850/J92/F165/O0/B3107/T3107, 일반 보석 4·특수 없음. 새로운 시즌·다른 전문화의 exact G로 복사 금지.

## 보존과 복원은 다르다

이 JSON은 성공의 **범위 영수증**이다. 원본에 있는 G_native_status 중간 상태 문자열, source_selected_flask_id=null, new_season_completion_claim=false도 원문 그대로 보존한다. 이후 verified installed READY와 앞선 단계 중간 상태는 혼동하지 않는다.

완전한 v213 source/catalog·v212 설치 manifest·item IDs·전체 DB2/SimC 원본·Native JSON2가 이 1.2KB 안에 저장돼 있는 것은 **아니다**. 영구 정확 바이트 복원 및 새로운 시즌 자동 값 결정은 이 자료만으로 보장하지 않는다.

환경 엔진과 단계별 SHA·로컬 캐시 재사용 구현은 runner/v216_environment_build_coordinator.py, runner/v217_stage_execution_engine.py, runner/v212_environment_manifest.py, runner/v046_static_item_cache.py에 유지되어 있다. 기존 사용자 작업공간에 온전한 소스·설치 영수증이 남아 있으면 해당 범위에 한해 재검증 후 재사용 가능하다.

향후 실제 시즌 Build 완료 시에는 기존 v212/v217 검증 매니페스트와 v213 카탈로그, v222 예산·옵션 identity·기본 정적 캐시, source 취득 provenance를 **작은 검증 가능한 export 묶음**으로 남기고 읽기 전용 import·verify를 기존 경로에 연결하는 것이 적합하다. 전체 DB를 무조건 영구 저장하거나 별도 강제 Gate로 확대하지 않는다. **이 기능은 현재 미구현**이다.
