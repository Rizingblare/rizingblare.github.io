<!-- harness:projection-begin harness-sync-v1 -->
<!-- harness:provenance {"schema":1,"target":".claude/skills/harness-sync/SKILL.md","sources":[{"path":".agents/skills/harness-sync/SKILL.md","sha256":"e351355cf3075c68cd11d892355eb2260c49e3705920a8f16324336a1d4272d9"}],"generator":{"path":"scripts/harness_manifest.py","sha256":"3631ffe4309c99f99ebf08a5d89e6c084db0ff7bb556f6df67fd7587e6acd94f"},"body_sha256":"e351355cf3075c68cd11d892355eb2260c49e3705920a8f16324336a1d4272d9"} -->
---
name: harness-sync
description: 범용 하네스 정본 변경 뒤 generated tool skill을 결정적으로 동기화하고 전체 gate를 검증한다.
---

# 하네스 동기화

canonical source, project Manifest 또는 generator config를 승인된 범위에서 변경한 뒤 다음 명령을 순서대로 실행한다. 각 명령의 전체 출력과 종료 상태를 읽으며, 실패하면 다음 단계로 진행하지 않는다.

```sh
python3 scripts/harness_manifest.py preflight --root .
python3 scripts/harness_manifest.py sync --root .
sh scripts/check.sh
python3 scripts/harness_manifest.py sync --root . --check
```

최초 도입에는 일반 sync를 사용하지 않는다. 승인된 immutable bootstrap plan과 digest를 사용하는 one-time bootstrap 절차를 따른다. Generated target은 직접 편집하지 않는다.

## English brief

This skill runs deterministic source preflight, skill sync, the repository gate, and the final no-drift check in order. First adoption uses the separately approved immutable bootstrap plan instead of ordinary sync.
<!-- harness:projection-end harness-sync-v1 -->
