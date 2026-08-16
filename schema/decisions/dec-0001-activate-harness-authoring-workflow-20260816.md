---
id: dec-0001-activate-harness-authoring-workflow-20260816
kind: decision
form: decision@1
created: 2026-08-16
status: active
gated_by: eval-0001-harness-ui-closure-20260816
targets: [path:AGENTS.md, path:CLAUDE.md, path:schema, path:scripts, path:knowledge, path:index.html, path:wiki, path:styles/wiki-document.css]
required_checks: [harness-manifest, harness-language, event-chain, public-surface, catalog-sync, search-runtime, site-regression]
verification_receipt: obs-0001-harness-ui-closure-20260816
---

# 결정 — 하네스와 개념 문서 작성 절차를 활성화

## 결정한 내용

저장소 맞춤 하네스를 기본 운영 방식으로 활성화한다. 사용자 피드백은 비공개 증거 계층에 원문으로 보존하고, 공개 UI에는 `proposed`를 노출하지 않으며 `pending`은 비링크 상태로만 노출할 수 있고 `published`만 문서 링크를 제공한다. 다음 개념 문서는 `knowledge/README.md`와 `knowledge/guides/document-authoring.md`의 proposed→pending→published 절차로 곧바로 시작한다.

## 범위

이 결정은 운영 계약, 구조 레지스트리, 증거 체인, 검사 스크립트, 개념 작성 절차와 공개 UI 상태 경계를 관할한다. 개별 개념 문서의 사실 내용, 외부 출처 선택, 원격 push와 배포는 관할하지 않는다.

## 적용 위치

- `0038d42` — 공개 카탈로그 작업 상태 제거
- `bdbd3bd` — Home 전역 내비게이션 추가
- `f8a32d1` — 저장소 맞춤 하네스 이식
- `64c387a` — 사용자 피드백 22건과 한글 정본 마감
- `8ba967b` — 트랜잭션 격리 수준 학습 UI 개선
- 정본: `AGENTS.md`, `CLAUDE.md`, `schema/project/manifest.yaml`, `schema/kernel/layout.yaml`, `schema/feedbacks/`, `knowledge/README.md`, `knowledge/guides/document-authoring.md`

## 철회

전체 게이트나 공개 상태 경계가 실패하면 이 결정의 `status`를 `rolled-back` 또는 `superseded-by <새 결정 id>`로 전이하고, 새 평가와 결정에서 영향을 받은 경로를 다시 검증한다.

## English brief

This decision activates the repository-adapted harness and the proposed-to-published concept-authoring workflow as the default operating mode. It keeps feedback and proposed work private, permits non-linked pending visibility, and reserves public links for published documents; remote push and deployment remain outside its scope.
