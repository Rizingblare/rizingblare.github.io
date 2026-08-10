---
name: harness-lint
description: 범용 하네스 source, Manifest, registry pointer와 generated projection의 무결성을 읽기 전용으로 검사한다.
---

# 하네스 lint

다음 read-only leaf를 실행하고 전체 출력과 종료 상태를 읽는다.

```sh
python3 scripts/harness_manifest.py lint --root .
```

이 leaf는 `scripts/check.sh`를 호출하지 않는다. 전체 repository gate가 필요하면 별도 행위로 `sh scripts/check.sh`를 실행한다.

## English brief

This skill runs the read-only harness lint leaf for canonical sources, the project Manifest, registry pointers, and generated projections. The full repository aggregator remains a separate explicit command.
