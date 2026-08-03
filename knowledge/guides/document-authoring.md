# 위키 문서 작성 청사진 (document-authoring blueprint)

1,157개 개념 문서 프로그램에서 **작성 에이전트가 문서를 만들기 전에 읽는 규범**이다.
이 문서의 규칙은 2026-08-03 결함 분석(라이브 사이트 Playwright 검증 + codex 적대적
리뷰)에서 실제로 깨졌던 지점들로부터 도출되었다 — 장식이 아니라 재발 방지다.

## English brief

Authoring blueprint for the ~1,157-document wiki program: canonical section
skeleton (v2), per-document co-located assets (`index.html` + `local.css` +
`labs.js`), the SVG/theming hard rules (no `var()` in presentation attributes,
`#map-arrow` marker id, token-only colors), catalog-first workflow, and the
review/versioning loop. Derived from real defect analysis, not convention.

## 1. 문서의 단위와 배치

- 한 문서 = 한 디렉토리: `wiki/<도메인 그룹>/<주제 그룹>/<concept-slug>/`
  - `index.html` — 문서 본문 (현재는 이것이 원본; 구조화 원본 포맷 도입 전까지)
  - `local.css` — 이 문서만의 스타일 (없으면 생략). **상대경로로 링크한다:
    `<link rel="stylesheet" href="local.css">` — 절대경로·트레일링 슬래시 금지
    (트레일링 슬래시는 GitHub Pages에서 404를 냈던 실결함이다).**
  - `labs.js` — 이 문서의 인터랙티브 랩 스크립트 (없으면 생략).
    `<script src="labs.js" defer></script>` 하나로 로드한다.
- 문서 자산은 다른 문서나 `scripts/`에 두지 않는다. **문서 디렉토리가 곧 작성·리뷰·
  재작성의 단위다.** (중복 사본은 codex 리뷰에서 이중 원본으로 지적되어 제거됐다.)
- URL·파일명은 영문 kebab-case.

## 2. 섹션 골격 (v2 canonical skeleton)

정착된 v2 골격 (pcm · osi-7-layer · tcp-udp · transaction-isolation 4개 문서가 준거):

```
overview            개요 히어로: eyebrow / h1 / hero-subtitle / hero-summary
concept-graph       선행→핵심→응용 개념 지도 (SVG, .concept-map)
<domain sections>   도메인 내용 섹션 2~5개 (문서마다 이름 다름)
worked-examples     풀이 과정이 있는 예제 (.worked, details.solution)
misconceptions      오개념 교정 (.callout[data-kind="warning"] 등)
document-connections 관련 문서 링크 (.connection-grid)
pending-concepts    아직 문서화되지 않은 참조 개념 (details로 접은 .glossary-grid)
sources             출처 (.source-list)
checkpoint          도착점 셀프체크 + 다음 문서 CTA (peak-end 마감)
```

각 섹션에는 모바일 TOC용 짧은 라벨 `data-toc-label="…"`을 반드시 단다(없으면
문장형 헤딩 전문이 TOC에 들어가 모바일 탐색이 붕괴한다). 마크업 원본은
[section-patterns.html](section-patterns.html)에서 복사하고, 살아 있는 완전한
예시는 PCM 문서를 참조한다.

- 새 문서는 이 골격에서 시작한다. 섹션 id는 위 이름을 그대로 쓴다 — TOC는
  기술적으로 임의의 `section[id]`를 스크롤 위치 기반으로 처리하므로(site.js)
  이 규칙은 동작 요건이 아니라 **문서 간 일관성 관례**다. 관례를 깨면 검색·
  비교·자동화가 어려워진다.
- 경량 문서(euler-formula, fourier-series형)는 concept-graph·worked-examples·
  misconceptions·pending-concepts를 생략할 수 있으나(현행 경량 2건이 실제로
  생략 중), **생략은 기본값이 아니라 판단이다** — 시험 대비 도메인
  (신호처리·전파·법규 등)은 worked-examples가 핵심 가치다.
- fourier-transform(73KB, 랩 7개)은 플래그십 실험형이다. 일반 문서의 기준으로
  삼지 않는다.

## 3. SVG·시각화 계약 (전부 실결함에서 도출된 강제 규칙)

1. **presentation attribute에 `var()` 금지.** `stroke="var(--x)"`·`fill="var(--x)"`는
   표준상 무효라 stroke는 none(투명), fill은 black으로 조용히 떨어진다.
   토큰은 반드시 클래스 CSS(`.plot-grid{stroke:var(--viz-grid)}`) 또는
   `style="stroke:var(--x)"`로 연결한다. (244곳을 이 규칙으로 교정했다.)
2. **개념 지도 화살표 마커 id는 `#map-arrow`.** 공유 CSS가
   `.map-edge{marker-end:url(#map-arrow)}`로 바인딩하므로 문서 SVG가
   `<marker id="map-arrow">`를 정의해야 화살표가 보인다. 문서별 변형 id
   (`#arrow`, `#tcp-map-arrow` 등)는 화살표를 조용히 죽였던 실결함이다.
3. **지도 노드는 실마크업으로.** `<a class="concept-ref" ...><g class="map-node ...">
   <rect/><text/></g></a>` — 마크업을 HTML 이스케이프된 문자열로 넣으면 텍스트로
   렌더된다(이중 이스케이프 실결함). 생성 파이프라인 산출물은 반드시 브라우저
   렌더로 검수한다.
4. **색은 토큰만.** 랩 파형은 `--wave-1/2/3/--wave-sum`(공유 기본값은
   `styles/wiki-document.css`, 문서 local.css가 오버라이드 가능). 일반 도해는
   `--brand/--brand-2/--cyan/--green/--orange/--line-strong/--ink/--muted/--paper`.
   리터럴 hex의 허용 범위는 **항상-다크 컴포넌트 내부**(`.lab`, `.code-block`,
   `.concept-tooltip` — 테마·모드와 무관하게 어두운 표면)와 브랜드 배경 위의
   흰 글자(`#fff`, 예: 지도 core 노드 텍스트)뿐이다.
5. **랩 스크립트 계약:** `labs.js`는 IIFE, 문서 내 요소 id 또는 문서 스코프
   셀렉터로만 접근하고 전역을 남기지 않는다. 축·격자·라벨은
   `.plot-grid/.plot-axis/.plot-label/.plot-muted` 클래스를 쓴다. 애니메이션은
   `prefers-reduced-motion` 미디어 규칙이 공유 CSS에 있으므로 CSS 전환에 의존하는
   부분은 자동 존중된다.

## 4. 테마 계약 (요약 — 전체는 DESIGN.md)

- 모든 색·반경·그림자는 토큰으로. 두 테마(Atlas/Pixel) × 두 모드(라이트/다크)
  네 팔레트에서 자동으로 맞물리는 유일한 방법이다.
- 도메인 4색 코딩(purple/mint/blue/yellow)은 Pixel 전용이다. Atlas 기준 설계에서는
  `--brand` 단일 강조를 쓴다.
- 콜아웃은 `data-kind="intuition|math|warning|practice"` 4종 — kind 색 틴트의
  1px 전체 테두리 + 배경 틴트 + kind 색 타이틀 (2026-08-04 확정 언어). 굵은
  좌측 보더와 그라디언트 텍스트는 사용자 결정으로 퇴역했다 — 새 문서에 쓰지
  않는다. 페이지 제목 강조는 단색 `var(--brand)` 스팬.
- 새 값은 DESIGN.md frontmatter의 `typeRamp`·`rounded` 램프에서만 고른다.
- 수식은 `.equation` 블록(전용 세리프)과 `<sub>/<sup>` 마크업. 외부 수식 라이브러리
  금지(정적 사이트, CSP·성능).

## 5. 카탈로그 우선 워크플로우

1. 문서화할 개념은 반드시 `knowledge/catalog/<domain>.json`에 항목이 먼저 있다.
   없으면 카탈로그 항목 추가가 선행 단위다.
2. 문서 발행 시 같은 단위에서 카탈로그 항목을 갱신한다:
   `status: "proposed" → "published"`, `route`와 `url` 기입.
3. `python3 scripts/build_search.py`로 샤드 재생성 → `sh scripts/check.sh` 0 실패
   확인 → 커밋. (산출물 직접 편집은 `catalog-sync` 게이트가 잡는다.)
4. 위키 인덱스(`wiki/index.html`)의 최근 발행 목록·카운트, 해당 도메인 페이지
   카운트도 같은 단위에서 갱신한다.

## 6. 재작성과 버전 관리

- **재작성은 예정된 일상이다.** 가이드라인·프로토타입·개별 문서 모두 이해 도달성을
  높이기 위해 수차례 전면 재작성될 수 있다는 전제로 운용한다.
- 전면 재작성은 원본(이 골격과 콘텐츠 요구사항)을 동결한 뒤, 원문을 읽지 않은
  에이전트에게 위임하고 결과를 누락 검수한다 (AGENTS.md 위임 규칙).
- 한 문서의 발행·재작성 = 한 커밋 = **§5의 발행 배선 전부를 포함한 문서 단위**:
  문서 디렉토리 + 카탈로그 항목 + 재생성된 샤드/manifest + 인덱스·카운트 갱신.
  여러 문서를 한 커밋에 섞지 않는다 — diff와 리뷰가 문서 단위로 남아야 한다.
- 발행 전 검증: 로컬 서버 + Playwright로 (a) 콘솔 에러 0 (b) 404 리소스 0
  (c) 미해결 `var()` 0 (d) 랩 경로 d 채움 (e) 라이트/다크 × Atlas/Pixel 스팟 확인.
- 작업 단위 완료 시 codex 적대적 리뷰 → 피드백을 미푸시 커밋에 폴딩.

## 7. 절대 하지 않는 것

- 검증 불가능한 사실·수치·출처를 만들어 넣지 않는다 (PRODUCT.md 원칙).
- 산출물(`search/wiki/*.json`, 파생 카운트)을 손으로 고치지 않는다.
- 레거시 v1 트리(`wiki/signal-processing/*` 등)에 새 문서를 만들지 않는다.
- 게이트 실패 상태로 커밋하지 않는다.
