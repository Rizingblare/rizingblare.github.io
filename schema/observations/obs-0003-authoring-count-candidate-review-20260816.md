---
id: obs-0003-authoring-count-candidate-review-20260816
kind: observation
form: observation@1
created: 2026-08-16
unit: authoring-count-candidate-review
---

# 관찰 — 작성 규모 교정 후보 검토

## 이 작업 단위가 수행한 일

- 제안 커밋: `c7fa7b366f473a7a78968a753fdf0587db80b4a7`.
- 후보 커밋: `ecec0280b47fdd8b11b64144acf8cbf4ed985e1a`.
- 고정 검토 범위: `c7fa7b366f473a7a78968a753fdf0587db80b4a7..ecec0280b47fdd8b11b64144acf8cbf4ed985e1a`.
- 구현 작업: `task_7ebd4bbe8d26` / `ctx_a5d298d7924a`, requested/effective `codex`, `gpt-5.6-sol`, `xhigh`.
- 독립 검토: `task_8a4b8b446230` / `ctx_f1ca9713e52e`, requested/effective `codex`, `gpt-5.6-sol`, `xhigh`.
- 검토 보고서: `/tmp/authoring-count-candidate-review.md`, SHA-256 `309e541b9acd8841defa6ab44d2f9b7e9be2e8682e98573a2e2d7199de80a933`.

## 파일

- 읽음: `schema/proposals/prop-0002-forward-correct-harness-closure-20260816.md`, `knowledge/README.md`, `knowledge/catalog/*.json`, `knowledge/guides/document-authoring.md`, `scripts/catalog_sync_check.py`, `scripts/build_search.py`, `scripts/check.sh`.
- 후보 수정: `knowledge/guides/document-authoring.md`, `scripts/catalog_sync_check.py`.
- 검토 생성: `/tmp/authoring-count-candidate-review.md`.
- canonical 수정: 없음. 후보는 검토 시점에 `authoring-count-correction-main` 브랜치에만 존재했다.

## 품질 차원

- 후보 범위 격리: 통과.
- 카탈로그 실집계와 작성 가이드 수치: 통과.
- 불일치 음성 검사: 통과.
- 전체 저장소 게이트: 통과.
- 독립 검토: 통과, 발견 사항 없음.

## 해결하지 못한 사항

없다. 후보의 canonical 적용은 새 평가와 결정 뒤의 별도 단계로 남겨 두었다.

## 측정값

- 후보 diff: 파일 2개, 37줄 추가, 2줄 삭제.
- 카탈로그: 1,399건.
- 가이드: 한국어 `1,399개 개념 문서 프로그램`, 영어 `~1,399-document wiki program`.
- 음성 시험: 한국어만 1,398로 바꾼 경우 `catalog-sync` finding 1건; 영어만 1,398로 바꾼 경우 finding 1건; 원본 후보는 finding 0건.
- `git diff --check c7fa7b3..ecec028`: exit 0.
- 후보 작업 트리 `sh scripts/check.sh`: 실패 0, 경고 0.
- 독립 검토 판정: PASS, HIGH/MEDIUM/LOW 0건.

## 조회로 복구할 수 없는 사항

- 첫 시도 `ctx_1aa53a1137ef`은 Orca의 새 작업 트리 기본 Git 기준이 현재 브랜치가 아니라 저장소 기본 기준점이라는 사실을 놓쳐 `8556c68`에서 시작했다. 수정 전 중단·release했고, `--base-branch main`을 명시한 `ctx_a5d298d7924a`로 다시 시작해 HEAD가 `c7fa7b3`과 일치함을 확인했다.
- 동적 검사는 특정 성공값을 하드코딩하지 않고 실제 `knowledge/catalog/*.json` 배열 길이 합계를 기준으로 두 명시 문구를 대조하는 최소 구현을 선택했다.

## 사고

- 잘못된 기준점의 첫 작업 트리는 파일 수정·커밋 전에 중단됐다. 산출물은 사용하지 않았고 작업 터미널은 release했다.

## 포인터

- 승인 제안: `schema/proposals/prop-0002-forward-correct-harness-closure-20260816.md`
- 후보: `ecec0280b47fdd8b11b64144acf8cbf4ed985e1a`
- 검토 작업: `task_8a4b8b446230` / `ctx_f1ca9713e52e`

## English brief

This receipt binds the isolated authoring-count candidate and its independent PASS review. The candidate dynamically rejects Korean or English guide counts that differ from the actual 1,399-item catalog and was not yet applied to main at review time.
