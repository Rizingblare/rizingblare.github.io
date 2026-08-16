---
id: dec-0002-apply-forward-harness-correction-20260816
kind: decision
form: decision@1
created: 2026-08-16
status: active
gated_by: eval-0002-forward-correct-harness-closure-20260816
targets: [path:knowledge/guides/document-authoring.md, path:scripts/catalog_sync_check.py, path:schema/decisions/dec-0001-activate-harness-authoring-workflow-20260816.md]
required_checks: [catalog-sync, authoring-count-mismatch, event-reference, decision-receipt, public-surface, worktree-clean]
verification_receipt: obs-0003-authoring-count-candidate-review-20260816
---

# 결정 — 작성 규모 후보를 전진 적용

## 결정한 내용

독립 검토를 통과한 후보 `ecec0280b47fdd8b11b64144acf8cbf4ed985e1a`를 이 결정 커밋 뒤에 canonical `main`으로 적용한다. 작성 가이드의 규모는 실제 카탈로그 합계와 동적으로 일치해야 하며, `dec-0001`은 이 결정으로 대체한다. 기존 `obs-0001`과 `eval-0001`은 당시 기록으로 보존한다.

## 범위

이 결정은 작성 가이드의 프로그램 규모, 그 수치를 카탈로그 실집계와 대조하는 검사, 이전 결정의 상태 전이만 관할한다. 공개 UI, 카탈로그 항목 내용, 문서 발행 상태, 원격 push와 배포는 변경하지 않는다.

## 적용 위치

- 제안: `c7fa7b366f473a7a78968a753fdf0587db80b4a7`
- 후보: `ecec0280b47fdd8b11b64144acf8cbf4ed985e1a`
- 검토·평가: `obs-0003-authoring-count-candidate-review-20260816`, `eval-0002-forward-correct-harness-closure-20260816`
- canonical 적용: 이 결정 발급 다음의 별도 적용 커밋에서 후보 두 파일을 반영한다.

## 철회

적용 뒤 전체 게이트가 실패하거나 수치 검사가 오탐을 만들면 이 결정의 상태를 `rolled-back` 또는 `superseded-by <새 결정 id>`로 전이하고, 별도 평가와 결정으로 후보 적용을 되돌리거나 교정한다.

## English brief

This decision supersedes dec-0001 and authorizes the independently reviewed ecec028 candidate for canonical application in the next commit. It changes only the authoring-count guide and dynamic catalog-count gate, preserving earlier immutable evidence and all public UI behavior.
