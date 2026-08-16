---
id: fb-0008-proposed-document-exposure-boundary-20260816
kind: feedback
form: feedback@1
created: 2026-08-16
scope: recurring
source_locator: conversation://orca/run_a8c449e7f34e/user-message-08
source_sha256: 5cb500a67a0043f0bd6348284add05b45549fda40cca2afc43f0fa55f4ab0551
source_byte_count: 220
---

# 피드백 — proposed 문서 노출 경계 정정

## 원문

<!-- protected span: begin -->
1B, 3A 승인. 2는 publish 및 pending 까지는 ui에 노출되어도 괜찮지만 지금처럼 작업 진행중도 아니고, 언제 완성될지도 모르는 propose 문서가 ui에 노출되는 상황이 문제다.
<!-- protected span: end -->

## 맥락

publish·pending과 달리 완료 시점이 불명확한 proposed 문서의 UI 노출이 문제라는 경계를 명확히 한 정정이다.

## 즉시 적용한 로컬 수정

이 JSON 산출물 작성은 read-only로 수행되어 main, harness-adaptation branch, runtime에 수정·ID 발급·commit·push를 하지 않았다. 현재 worktree에는 이 작업의 소유가 아닌 기존 미커밋 변경이 있으나, 이 기록이 그것을 해결했다고 주장하지 않는다.

## 범위 판단

서로 다른 사용자 발화에서 같은 종류의 정보 노출·운영·소통 문제가 반복되어 recurring으로 분류한다. 이 분류만으로 전역 규칙을 만들지 않으며, 승격에는 추가 observation과 proposal 및 명시적 승인이 필요하다.

## English brief

The user raised a concern about the UI exposure boundary for proposed documents. This record preserves one utterance and does not claim a remedy beyond the verified current state.
