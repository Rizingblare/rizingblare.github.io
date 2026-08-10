---
nature: manifest
mode: manual
owners:
  - "contract:deferred-queue#status-table"
---

# 보류 대기열 — 상태

**항목 0개.**

대기열이 비어 있어도 이 파일, 이 header, 명시적인 0개 count 문장은 모두
그대로 유지한다. manifest가 없으면 fail-open이다. parser는 없는 파일을 조용히
건너뛰므로 이 파일을 삭제해도 error로 드러나지 않는다. 오히려 이 파일을 읽는
check 자체가 사라진다.

| id | title | opened | status | closed by |
|---|---|---|---|---|

## 이 표가 flag하면 안 되는 것

carrier별 contract가 없는 currency check는 추측할 수밖에 있다. 추측하는 check는
정당한 row를 끊임없이 flag하여 결국 무시되게 하거나, 모든 것을 통과시켜 장식에
그치게 한다. 따라서 이 carrier는 자신의 조건을 다음과 같이 선언한다.

- **고아(`orphan`)** — `_todo/` 또는 `done/` 아래에 있지만 여기에 row가 없는 파일.
- **죽은 행(`dead row`)** — `_todo/`와 `done/` 어느 directory에도 존재하지 않는 파일을 지목하는 row.
- **비교 대상 개수(`compared count`)** — status가 `open`인 row 수를 `_todo/` 아래의 파일 수와 비교한다.
- **표시하지 않음(`not flagged`)** — 위의 0개 count 문장과 row cell 안의 prose.

item이 두 directory 사이를 이동하므로 양쪽을 scan하여 재계산하는 것보다 대기열
counter를 여기에 두는 편이 비용이 적다. counter를 관측된 최댓값과 대조하며,
counter와 실제가 다르면 실제를 따른다.

## English brief

This manual manifest remains present when the deferred queue is empty, preserving an explicit zero-count state and preventing its check from failing open. Its currency contract defines orphan and dead-row detection, compares open rows with `_todo/` files, excludes prose and the zero-count sentence from flags, and treats observed reality as authoritative when it conflicts with the stored counter.
