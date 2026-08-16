---
id: prop-0001-complete-harness-adaptation-20260816
kind: proposal
form: proposal@1
created: 2026-08-16
status: approved
evidence: [fb-0010-close-completed-sessions-and-harness-20260816, fb-0012-korean-harness-documentation-20260816, fb-0014-harness-feedback-recording-20260816, fb-0015-retroactive-harness-adaptation-20260816, fb-0022-continue-until-concept-docs-20260816]
---

# 제안 — 하네스 이식과 작성 확대 준비를 하나의 폐쇄 단위로 완료

## 근거

사용자는 완료 세션 정리, 피드백 영구 기록, 하네스의 저장소 맞춤 이식, 사람이 읽는 운영 문서의 한글 정본화, 추가 승인 없이 개념 문서 작성 확대가 가능한 상태까지의 연속 진행을 요청했다. 위 `evidence`의 피드백 기록이 원문과 범위를 보존한다.

## 진단

기존 조립본은 운영 계약의 일부를 구현했으나 구조 레지스트리가 소유권·출처·공개 범위를 충분히 표현하지 못했고, 실제 Orca 완료 기록과 모델 검증 필드가 어긋났으며, 피드백 기록이 0건이었다. 또한 하네스 설명 문서가 영어라 사용자가 변경 내용을 직접 검토하기 어려웠다. UI 변경만 먼저 끝내는 대안은 같은 운영 결함을 반복하므로 기각한다.

## 제안된 변경

`AGENTS.md`는 범용 한글 운영 계약으로, `CLAUDE.md`는 그 정본을 가리키는 짧은 도구 어댑터로 둔다. 저장소 고유 목적·언어·모델·도구 설정은 `schema/project/manifest.yaml`에 둔다. `schema/kernel/layout.yaml`은 모든 경로 그룹의 소유권·출처 계층·헌장·공개 범위·생산/공개 게이트를 표현한다. 한글 `harness-sync`와 `harness-lint` 스킬 및 검사 스크립트를 연결하고, 하네스 문서·양식은 한국어 정본과 2~4문장 `English brief`로 구성한다. 사용자 피드백은 `schema/feedbacks/`에 원문 바이트를 보존해 기록하며 공개 사이트에서는 제외한다. 기존 UI 개선 브랜치를 통합한 뒤 개념 문서 작성 워크플로우를 검증한다.

## 성공 기준 (동결됨 — 승인 후 수정 금지)

<!-- protected span: begin -->
1. `sh scripts/check.sh`가 0 failure로 끝나고, 커밋 뒤 `worktree-clean` 경고도 0이다.
2. `schema/kernel/layout.yaml`이 모든 추적 경로를 정확히 하나의 선언에 귀속시키며 owner, provenance, charter, schema, exposure, producer gate, exposure gate를 검증한다.
3. 실제 Orca 저장 실행 기록에서 rewrite/review는 `gpt-5.6-sol/xhigh`, routine은 `gpt-5.6-terra/high`의 requested/effective 값이 일치한다.
4. 하네스의 사람이 읽는 정본 문서와 양식은 한국어이며 각각 2~4문장 `## English brief` 또는 YAML 주석형 영어 요약을 갖는다. 사람용 영어 자리표시자는 남지 않는다.
5. 사용자 피드백 22건은 `fb-0001`부터 충돌 없이 발급되고 보호 영역의 SHA-256과 UTF-8 byte count 검사를 통과한다.
6. 공개 표면 검사는 `proposed` 0건 노출, `pending` 비링크 노출 허용, `published` 링크 노출만 허용하는 계약을 통과한다.
7. Home 전역 내비게이션과 트랜잭션 격리 문서 UI 개선을 main에 통합하고 정적 게이트와 브라우저 회귀 검증을 통과한다.
8. 카탈로그 1,399건의 proposed→pending→published 작성 절차, 필수 파일과 검증 명령이 확인되어 다음 개념 문서 작성 단위를 즉시 시작할 수 있다.
9. 원격 push나 배포는 수행하지 않는다.
<!-- protected span: end -->

## 회귀 위험

레지스트리 스키마 확장으로 기존 경로가 미선언되거나 잘못 공개될 수 있고, 양식 번역이 machine key·exact marker를 손상할 수 있다. 피드백 소급 발급은 번호 충돌과 원문 변형 위험이 있다. UI 브랜치 통합은 `scripts/site.js`와 공유 CSS의 회귀 위험이 있다. fixture, 전체 게이트, 고정 범위 독립 검토, 브라우저 회귀로 다룬다.

## 롤백

평가가 실패하면 `harness-adaptation`과 `transaction-isolation-ui`의 미통합 커밋을 main에 반영하지 않는다. 이미 main에 통합한 뒤 결함이 발견되면 새 결정과 명시적 되돌림 커밋으로 상태를 전이한다.

## English brief

This approved proposal closes the repository-specific harness adoption, Korean canonical documentation, retrospective feedback records, and UI stabilization as one bounded program. Its frozen criteria require zero gate failures, verified orchestration bindings, private feedback evidence, public-surface safety, integrated UI regression checks, and a ready concept-authoring workflow without any remote push or deployment.
