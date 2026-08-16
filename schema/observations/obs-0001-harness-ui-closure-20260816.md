---
id: obs-0001-harness-ui-closure-20260816
kind: observation
form: observation@1
created: 2026-08-16
unit: harness-ui-closure
---

# 관찰 — 하네스 이식과 UI 안정화 마감

## 이 작업 단위가 수행한 일

- `0038d42 fix: keep catalog workflow off public surfaces`
- `bdbd3bd feat: add global navigation to home`
- `f8a32d1 schema: adapt harness to repository`
- `64c387a docs: preserve repository feedback history`
- `8ba967b feat: improve transaction isolation learning UI`

공개 카탈로그 상태 분리, Home 전역 내비게이션, 저장소 맞춤 하네스, 소급 피드백 22건, 트랜잭션 격리 수준 학습 UI를 로컬 `main`에 통합했다. 원격 push와 배포는 수행하지 않았다.

## 파일

- 읽음: `AGENTS.md`, `CLAUDE.md`, `schema/project/manifest.yaml`, `schema/kernel/layout.yaml`, `schema/proposals/prop-0001-complete-harness-adaptation-20260816.md`, `schema/template/events/{observation,evaluation,decision}.md`, `knowledge/README.md`, `knowledge/guides/document-authoring.md`, `wiki/domains/networking/index.html`, `wiki/database-systems/concurrency/transaction-isolation/{index.html,labs.js,local.css}`, `scripts/{check.sh,event_check.py,public_surface_check.py}`.
- 생성: `.agents/skills/{harness-sync,harness-lint}/`, `.claude/skills/{harness-sync,harness-lint}/`, `schema/project/manifest.yaml`, `schema/feedbacks/fb-0001`부터 `fb-0022`, `schema/proposals/prop-0001-complete-harness-adaptation-20260816.md`, `schema/stages/bootstrap/harness-bootstrap-plan.json`, `scripts/event_check.py`, `scripts/harness_manifest.py`, `scripts/public_surface_check.py`, 관련 검사 fixture.
- 수정: 루트 운영 계약과 제품·디자인 문서, `schema/` 정본과 양식, `scripts/` 검사기, 검색 산출물, Home·위키·도메인·발행 문서 HTML, `scripts/site.js`, `scripts/v2.js`, `styles/wiki-document.css`.
- 삭제: 사용자용 플레이스홀더 자격증 SVG 2개와 공개 카탈로그 작업 화면 `wiki/catalog/index.html`. 중복·통합 과정의 별도 데이터나 작업 세션 기록은 영속 자료로 추가하지 않았다.

## 품질 차원

- 구조 레지스트리와 소유권: 통과.
- 피드백 원문 무결성: 통과.
- 한글 정본과 영어 라우팅 요약: 통과.
- 공개 상태 경계: 통과.
- 데스크톱·모바일 탐색: 통과.
- 인터랙티브 학습 랩의 인과 표현: 통과.
- 개념 문서 작성 확대 준비도: 통과.
- 원격 반영: 해당 없음.

## 해결하지 못한 사항

없다. 다음 개념 문서의 실제 집필은 이 작업 단위의 후속 단위이며, 작성 절차를 시작할 수 있는 상태까지를 이번 범위로 삼았다.

## 측정값

- `sh scripts/check.sh`: 실패 0, 경고 0.
- 공개 표면 검사: 발행 7건, 작성 대기 0건, 제안 0건 노출, 활성 도메인 3개.
- 카탈로그: 전체 1,399건 = 제안 1,392건 + 작성 대기 0건 + 발행 7건. `knowledge/catalogs/*.json`과 준비도 점검으로 산출했다.
- 피드백: 22건. 각 보호 영역의 SHA-256과 UTF-8 바이트 수를 `scripts/event_check.py`로 검증했다.
- 언어 검사: 사람이 읽는 정본 25개와 `schema/kernel/layout.yaml`의 주석형 영어 요약을 검사했다. 5문장 영어 요약 음성 fixture는 의도대로 거부됐다.
- 네트워크 도메인 브라우저 검사: `proposed` 표기 0, `pending` 표기 0, 공개 개념 2, 발행 문서 링크 2.
- 격리 수준 브라우저 검사: `lost × rc`에서 `dirty × ser`로 바꾸자 SVG 제목·단계·원인·결과·판정이 함께 변경됐다. 스냅샷 수준을 `rr`로 바꾸자 두 번째 읽기가 `100 (유지)`로 바뀌고 새 버전에 `T1에게 보이지 않음`이 표시됐다.
- 접근성·코드 UI: 두 `.lab-readout` 모두 `role="status"`; 코드 블록은 `data-lang="js"`, `<code>`, 복사 버튼을 모두 갖췄다.
- 모바일 390×844: 문서 전체 가로 넘침 0px, 메뉴 열림 뒤 6개 전역 링크 표시, 타임라인 스크롤 안내 2개 표시.
- 테마: 어두운 문서 본문과 밝은 문서 본문 모두에서 고정 다크 랩의 SVG 텍스트가 `rgb(233, 237, 245)`로 유지됐다.

## 조회로 복구할 수 없는 사항

- 사용자에게는 작업 상태가 아니라 학습 가능한 공개 상태만 보여야 한다는 기준에 따라 `proposed`는 비공개로, `pending`은 비링크 노출 가능으로, `published`만 링크 가능으로 정착시켰다.
- 중복·통합 이력 자체는 제품 데이터가 아니므로 별도 영속 데이터로 보존하지 않았다. 대신 사용자의 피드백 원문, 승인된 제안, 평가와 결정만 증거 체인에 남긴다.
- `AGENTS.md`와 `CLAUDE.md`에 저장소 도메인 설명을 되풀이하지 않고, 저장소별 값은 `schema/project/manifest.yaml`로 분리했다.

## 사고

- main에서 잘못 적용한 임시 patch는 즉시 바이트 단위로 원복해 최종 차이에 남지 않았다.
- `scripts/event_check.py`를 처음 직접 실행할 때 필수 `--fixtures` 인자를 빠뜨렸으나, 전체 `scripts/check.sh`가 올바른 fixture 경로로 재검증했다.
- 재사용 터미널의 모델 메타데이터가 `null`로 저장된 실행은 중단하고, 모델과 추론 수준을 명시한 새 작업으로 대체했다.
- 범위가 넓어 판정을 내리지 못한 독립 검토 2건은 실패로 정리하고, 고정 커밋 범위와 동결 기준을 가진 검토로 대체했다.

## 포인터

- 운영 계약: `AGENTS.md`
- 저장소 매니페스트: `schema/project/manifest.yaml`
- 구조 레지스트리: `schema/kernel/layout.yaml`
- 사용자 피드백: `schema/feedbacks/`
- 승인 제안: `schema/proposals/prop-0001-complete-harness-adaptation-20260816.md`
- 작성 절차: `knowledge/README.md`, `knowledge/guides/document-authoring.md`

## English brief

This receipt records the completed repository-specific harness adoption, private feedback evidence, public-state boundary, and UI regression verification. The local main branch is ready to begin the next concept-authoring unit, while no remote push or deployment occurred.
