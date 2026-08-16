---
id: obs-0002-final-review-and-browser-evidence-20260816
kind: observation
form: observation@1
created: 2026-08-16
unit: harness-forward-correction-input
---

# 관찰 — 최종 독립 검토와 고정 브라우저 증거

## 이 작업 단위가 수행한 일

- 고정 검토 범위: `8556c68a7c74f4efa915b3a5ed14059f99d7e2c3..a07e89763736fc03d5011fcb6a8f41f654a7cf97`.
- 검토 작업: `task_3a1e3b724c35` / `ctx_28204bfcadfd`.
- 검토 모델: requested/effective 모두 `codex`, `gpt-5.6-sol`, `xhigh`.
- 검토 보고서: `/tmp/final-assembly-review.md`, SHA-256 `d58fd9fbe7a22f62ec07143455fa8804a79cb9d869567485ab23c88a730ede17`.
- 브라우저 대상 커밋: `a07e89763736fc03d5011fcb6a8f41f654a7cf97`.

## 파일

- 읽음: `schema/proposals/prop-0001-complete-harness-adaptation-20260816.md`, `schema/observations/obs-0001-harness-ui-closure-20260816.md`, `schema/evaluations/eval-0001-harness-ui-closure-20260816.md`, `schema/decisions/dec-0001-activate-harness-authoring-workflow-20260816.md`, `knowledge/README.md`, `knowledge/guides/document-authoring.md`, `knowledge/catalog/*.json`, Home·네트워크 도메인·트랜잭션 격리 문서와 관련 JS/CSS.
- 생성: `/tmp/final-assembly-review.md`.
- 수정: 없음.

## 품질 차원

- 전체 정적 게이트: 통과.
- 공개 상태 경계: 통과.
- Home 내비와 격리 수준 정적 계약: 통과.
- 브라우저 실동작: 통과했으나 기존 관찰의 고정 결속은 불충분.
- 증거 사슬의 시간 순서: 실패.
- 작성 가이드 수치 정합성: 실패.
- 기존 관찰의 정본 경로 정확성: 실패.

## 해결하지 못한 사항

기존 `obs-0001`은 발급 뒤 불변이므로 그 안의 `knowledge/catalogs/*.json` 오기를 수정하지 않았다. 올바른 정본 경로는 `knowledge/catalog/*.json`이며 이 관찰이 시간 순서로 교정한다.

## 측정값

- 독립 검토 결과: HIGH 1건, MEDIUM 2건, LOW 1건.
- `git diff --check 8556c68..a07e897`: exit 0.
- `sh scripts/check.sh`: 실패 0, 경고 0.
- 카탈로그: `jq -s '[.[][]] | group_by(.status)' knowledge/catalog/*.json` 기준 1,399건; proposed 1,392, pending 0, published 7, 고유 id 1,399.
- 원격 상태: `origin/main` 대비 로컬 `main` 6커밋 앞섬. push·배포 수행 없음.

## 고정 브라우저 회귀 증거

- 실행 주체: 조정 세션 `term_e33f5501-0efb-484e-9a7f-5fca3d3978c7`.
- 브라우저 페이지: `df27a8a5-1c84-4b09-b0b8-d06a4287eeda`.
- 로컬 원점: `http://127.0.0.1:8765`, 대상 커밋 `a07e89763736fc03d5011fcb6a8f41f654a7cf97`.
- 네트워크 도메인: proposed 표기 false, pending 표기 false, proposed node 0, pending node 0, 공개 개념 2, 발행 링크 2.
- 격리 랩 초기값: anomaly `lost`, level `rc`; 판정은 갱신 분실 가능, 최종 counter 11과 증가 1회 분실을 표시.
- 격리 랩 변경값: anomaly `dirty`, level `ser`; SVG 단계가 `UPDATE balance=0`, `SELECT → 100 (커밋값)`, `ROLLBACK`으로 바뀌고 판정은 해당 수준에서 방지로 변경.
- 스냅샷 랩 변경값: level `rr`; 두 번째 읽기 `100 (유지)`, 새 버전 `T1에게 보이지 않음`, 트랜잭션 스냅샷 유지 원인을 표시.
- 접근성·코드: `.lab-readout` 2개 모두 `role="status"`; 코드 블록은 `data-lang="js"`, `<code>`, 복사 버튼을 모두 갖춤.
- 모바일: iPhone 12 에뮬레이션 390×844, 문서 전체 가로 넘침 0px. MENU를 열면 `aria-expanded="true"`, 내비 `display:flex`, HOME·RESUME·PORTFOLIO·BLOG·WIKI·SEARCH 6링크 표시. `← 가로로 밀어 전체 타임라인 보기 →` 안내 2개가 표시됨.
- 테마: dark에서 본문 `rgb(13, 17, 24)`, 랩 `rgb(17, 21, 29)`, SVG 텍스트 `rgb(233, 237, 245)`; light에서 본문 `rgb(238, 242, 247)`, 랩과 SVG 텍스트는 동일한 고정 다크 계측기 값 유지.

## 조회로 복구할 수 없는 사항

- 최종 검토는 코드가 아니라 시간 순서를 실패 원인으로 판정했다. 작동 중인 UI를 원복한 뒤 재적용하는 대안은 사용자 가치 없이 회귀 위험을 늘리므로, 새 제안부터 올바른 순서로 전진 교정하는 최소 범위를 선택한다.
- 검토자 도구 표면에는 Browser 스킬이 요구하는 실행 인터페이스가 없어 브라우저를 독립 재실행하지 못했다. 조정 세션이 이미 수행한 고정 커밋 브라우저 결과를 이 불변 관찰에 구체적인 입력·출력과 함께 보존한다.

## 사고

- 첫 폐쇄 단위는 기능 적용 뒤에 제안·평가·결정을 발급해 하네스가 요구하는 시간 순서를 역전했다.
- 작성 가이드의 프로그램 규모 두 곳과 관찰의 정본 경로 한 곳을 이전 검사에서 놓쳤다.

## 포인터

- 올바른 카탈로그 정본: `knowledge/catalog/*.json`
- 작성 정본: `knowledge/guides/document-authoring.md`
- 이전 독립 검토: Orca 작업 `task_3a1e3b724c35`, dispatch `ctx_28204bfcadfd`

## English brief

This immutable observation binds the final adversarial review and browser regression results to commit a07e897. It records one sequencing failure, two medium evidence/documentation defects, and one corrected catalog pointer without rewriting the earlier observation.
