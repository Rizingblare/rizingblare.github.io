---
id: prop-0002-forward-correct-harness-closure-20260816
kind: proposal
form: proposal@1
created: 2026-08-16
status: approved
evidence: [fb-0022-continue-until-concept-docs-20260816, obs-0002-final-review-and-browser-evidence-20260816]
---

# 제안 — 하네스 폐쇄 순서를 전진 교정

## 근거

사용자는 개념 문서 작성 확대가 가능한 상태까지 추가 승인 없이 끝까지 진행하라고 지시했다. `obs-0002`의 독립 검토는 기능이 아니라 첫 폐쇄 단위의 시간 순서, 브라우저 증거 결속, 작성 가이드 수치와 정본 경로를 결함으로 판정했다.

## 진단

기존 UI와 공개 상태 경계는 전체 게이트와 브라우저 검사에서 정상이다. 이를 원복하고 재적용하면 사용자 가치 없이 회귀 위험만 증가한다. 따라서 기존 immutable 관찰·평가는 보존하고, 기존 결정을 새 결정으로 대체하며, 문서와 검사기의 실제 결함만 별도 후보에서 고치는 전진 교정이 최소 범위다.

## 제안된 변경

`knowledge/guides/document-authoring.md`의 프로그램 규모를 실제 1,399건으로 맞춘다. `scripts/catalog_sync_check.py`가 카탈로그 실집계와 작성 가이드 규모가 일치하는지 검사하도록 해 같은 회귀를 막는다. 수정 후보는 별도 작업 트리와 커밋으로 고정한 뒤 독립 검토하고, 그 결과로 새 평가와 결정을 먼저 발급한다. 이후에만 후보를 `main`에 적용한다. `dec-0001`은 새 결정으로 대체하되 이전 `obs-0001`과 `eval-0001`은 고쳐 쓰지 않는다. 브라우저 결과는 `obs-0002`의 고정 커밋·입출력 결속을 사용한다.

## 성공 기준 (동결됨 — 승인 후 수정 금지)

<!-- protected span: begin -->
1. 수정 후보는 이 제안 뒤 별도 커밋으로 만들어지며, canonical `main` 적용 전에 고정 범위 독립 검토를 통과한다.
2. `knowledge/catalog/*.json` 실집계 1,399건과 `knowledge/guides/document-authoring.md`의 한국어 본문·English brief 규모가 일치한다.
3. `scripts/catalog_sync_check.py`는 카탈로그 수와 작성 가이드 수치가 다르면 실패하는 회귀 검사를 포함한다.
4. `obs-0002`는 커밋 `a07e897`의 브라우저 입력·출력, viewport, task/dispatch와 검토 보고서 digest를 불변 기록으로 제공한다.
5. 새 평가는 후보 독립 검토 뒤에, 새 결정은 그 평가 뒤에 발급되며, 후보의 canonical 적용은 새 결정 뒤에 이루어진다.
6. 새 결정은 `dec-0001`을 대체하고, 기존 immutable `obs-0001`과 `eval-0001`을 수정하지 않는다.
7. 적용 뒤 `sh scripts/check.sh`는 실패 0·경고 0이고 공개 UI 계약과 기존 브라우저 대상 코드에는 변화가 없다.
8. 원격 push나 배포는 수행하지 않는다.
<!-- protected span: end -->

## 회귀 위험

동적 수치 검사가 작성 가이드의 다른 숫자를 잘못 읽거나 카탈로그 형식을 과도하게 가정할 수 있다. 검사는 명시적인 프로그램 규모 문구만 대조하고 기존 카탈로그 스키마 검증을 재사용한다. 기존 결정을 대체할 때 상태 문법과 event reference가 깨질 수 있으므로 전체 event fixture와 게이트를 적용 전후 모두 실행한다.

## 롤백

후보 검토나 새 평가가 실패하면 후보를 `main`에 적용하지 않고 `dec-0001` 상태도 바꾸지 않는다. 적용 뒤 실패하면 새 결정 상태 전이와 별도 교정 커밋으로 처리한다.

## English brief

This approved forward correction preserves the working UI while repairing the harness closure sequence and authoring-count contract. A fixed candidate must be independently reviewed before a new evaluation and superseding decision, and only then may it be applied to main without any remote push or deployment.
