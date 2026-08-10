<!-- harness:projection-begin harness-lint-v1 -->
<!-- harness:provenance {"schema":1,"target":".claude/skills/harness-lint/SKILL.md","sources":[{"path":".agents/skills/harness-lint/SKILL.md","sha256":"1dc91aae2184102053f68b554a88c2b1ebc42eb66ba7adbf80c634a89a9b6972"}],"generator":{"path":"scripts/harness_manifest.py","sha256":"3631ffe4309c99f99ebf08a5d89e6c084db0ff7bb556f6df67fd7587e6acd94f"},"body_sha256":"1dc91aae2184102053f68b554a88c2b1ebc42eb66ba7adbf80c634a89a9b6972"} -->
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
<!-- harness:projection-end harness-lint-v1 -->
