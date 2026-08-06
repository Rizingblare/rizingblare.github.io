---
name: 김정도 — Developer & Knowledge Builder
description: 이력서·포트폴리오·블로그·개념 위키를 하나의 정적 사이트로 묶는 2-테마 지식 시스템 (frontmatter 색상은 기본 테마 "Knowledge Atlas"의 라이트 모드만 정규 값으로 담음; 전체 4개 팔레트는 Colors 섹션 표를 참고)
colors:
  bg: "#eef2f7"
  paper: "#ffffff"
  paper-2: "#f7f9fc"
  paper-3: "#eef3ff"
  ink: "#172033"
  ink-soft: "#425067"
  muted: "#5f6b7d"
  soft: "#8792a5"
  line: "#dce2eb"
  line-strong: "#c7d0dd"
  brand: "#315eea"
  brand-2: "#6d47e5"
  cyan: "#0797b8"
  green: "#008f68"
  orange: "#d95c12"
  red: "#cf3e56"
  purple: "#6d47e5"
  mint: "#2bbf93"
  blue: "#315eea"
  yellow: "#f0b429"
  viz-bg: "#11151d"
  viz-panel: "#171c26"
  viz-text: "#e9edf5"
  viz-muted: "#a8b1c2"
typography:
  display:
    fontFamily: "Inter, Pretendard, \"Noto Sans KR\", system-ui, sans-serif"
    fontSize: "clamp(55px, 8.8vw, 132px)"
    fontWeight: 700
    lineHeight: 0.92
    letterSpacing: "-0.08em"
  headline:
    fontFamily: "Inter, Pretendard, \"Noto Sans KR\", system-ui, sans-serif"
    fontSize: "clamp(44px, 6vw, 82px)"
    fontWeight: 700
    lineHeight: 1.07
    letterSpacing: "-0.055em"
  title:
    fontFamily: "Inter, Pretendard, \"Noto Sans KR\", system-ui, sans-serif"
    fontSize: "clamp(29px, 4vw, 40px)"
    fontWeight: 700
    lineHeight: 1.25
  body:
    fontFamily: "Inter, Pretendard, \"Noto Sans KR\", system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.72
  label:
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
    fontSize: "13px"
    fontWeight: 800
    letterSpacing: "0.08em"
rounded:
  none: "0"
  chip: "10px"
  control: "11px"
  card: "16px"
  panel: "22px"
  hero: "30px"
  pill: "999px"
typeRamp:
  - "10px"
  - "11px"
  - "12px"
  - "13px"
  - "14px"
  - "15px"
  - "17px"
  - "18px"
  - "19px"
  - "23px"
  - "clamp(29px, 4vw, 40px)"
  - "clamp(44px, 6vw, 82px)"
  - "clamp(55px, 8.8vw, 132px)"
components:
  button-primary:
    backgroundColor: "{colors.brand}"
    textColor: "#ffffff"
    rounded: "11px"
    padding: "9px 16px"
  button-primary-hover:
    backgroundColor: "color-mix(in srgb, {colors.brand} 86%, #000)"
  card-surface:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "clamp(22px, 4vw, 34px)"
---

# Design System: 김정도 — Developer & Knowledge Builder

## Overview

**Creative North Star: "Knowledge Atlas"**

이 이름은 사용자가 확정한 것이 아니라, 사이트가 자체적으로 이미 선언한 기본 테마 이름을 그대로 옮긴 **잠정 표현**입니다. 정성적 확인 라운드(플레이북 Step 3)를 실행할 수 없었기 때문에, 아래 서술은 사용자 확정 전까지 관찰된 사실의 요약으로만 읽어야 합니다. 이 사이트는 자체적으로 두 개의 이름 있는 테마를 이미 선언하고 있습니다: 기본 테마 **Knowledge Atlas**(문서 지향, 차분한 정보 밀도)와 보조 테마로 보존된 **Pixel Portfolio**(원래 프로토타입의 하드엣지 네오브루탈리즘).

관찰된 사실만 정리하면: 이 사이트는 이력서, 포트폴리오, 블로그, 그리고 1,250개 canonical concept를 담은 개념 위키를 하나의 정적 셸(`site-header`/`site-footer`/`page-shell`) 아래 묶습니다. 시각 정체성은 코드 레벨에서 완전히 분리된 두 테마 스타일시트로 스위칭되며, 같은 HTML 컴포넌트가 테마에 따라 정반대의 표면 언어(평평한 대비형 vs. 부드러운 앰비언트형)를 입습니다. `wiki-document.css`는 모든 페이지 셸이 조건 없이 항상 로드하는 세 번째 레이어이며(과거 이를 로드하지 않던 레거시 v1 위키 페이지 7건은 2026-08-04 삭제됨), 그 안의 선택자가 전부 `.wiki-document-page`로 스코프되어 있어 실제로는 위키 문서 페이지에서만 발현합니다 — 항상 다크 표면인 `.lab` 실험 패널도 이 레이어에 속합니다.

**Key Characteristics:**
- 토큰 계약 기반 2-테마 시스템: Atlas(기본)와 Pixel(보조)이 동일 컴포넌트를 완전히 다른 표면 언어로 렌더링합니다.
- 색상 모드(라이트/다크/시스템)는 테마 선택과 독립적인 축이며, 두 축 모두 `localStorage`에 지속됩니다.
- 위키 문서는 항상 다크인 `.lab` 실험 패널과 SVG 개념 지도를 표준 섹션 스켈레톤 위에 얹습니다.
- 폰트는 세 갈래입니다: 본문/제목용 가변 산세리프, 라벨/코드용 모노스페이스, 그리고 수식(`.equation`) 전용 세리프(`STIX Two Text`) 한 종류.

## Colors

네 개의 팔레트가 실재합니다 — Atlas 라이트(기본), Atlas 다크, Pixel 라이트, Pixel 다크. frontmatter에는 기본 테마인 **Atlas 라이트**만 정규 값으로 담았습니다. 아래 표가 그 외 세 팔레트의 실제 소스입니다(frontmatter와 다른 값이라도 재정의가 아니라 다른 테마의 값입니다).

| 역할 | Atlas Light | Atlas Dark | Pixel Light (core.css 기반) | Pixel Dark |
|---|---|---|---|---|
| `--bg` (페이지 캔버스, `html`/`body` 배경) | `#eef2f7` | `#0d1118` | `--paper` 별칭 (`#f7f4ef`) | `--paper` 별칭 (`#15121b`) |
| `--paper` (카드·패널 표면) | `#ffffff` | `#131923` | `#f7f4ef` | `#15121b` |
| `--paper-2` | `#f7f9fc` | `#181f2b` | `--paper-strong` 별칭 (`#ffffff`) | `#201b28` |
| `--ink` | `#172033` | `#eef2f8` | `#1e1b26` | `#f4eef9` |
| `--muted` | `#5f6b7d` | `#b5becc` | `#756e7b` | `#a89eaf` |
| `--line` | `#dce2eb` | `#2a3342` | `#1e1b26` (ink 재사용) | `#f4eef9` |
| `--brand` | `#315eea` | `#82a4ff` | `--purple` 별칭 (`#a866ff`) | `#ba8cff` |
| `--brand-2` | `#6d47e5` | `#b49aff` | `#7f4bc8` | `#d2b3ff` |
| `--green` | `#008f68` | `#61deb9` | `#168b68` | `--mint` 별칭 (`#72ddba`) |
| `--orange` | `#d95c12` | `#ffa06a` | `#c95f22` | `#ffad71` |
| `--radius` | `22px` | `22px` | `0` | `0` |
| `--shadow` | `0 18px 55px rgba(30,44,74,.09)` | `0 18px 55px rgba(0,0,0,.25)` | `6px 6px 0 var(--ink)` | `6px 6px 0 #060507` |

### Primary
- **Brand Blue** (`#315eea`, Atlas light `--brand`): Atlas의 유일한 강조색. 액션 버튼, 링크 호버, 도메인 카드 호버 테두리, 진행률 바 그라디언트의 한쪽 끝에 쓰입니다.
- **Brand Violet** (`#6d47e5`, Atlas light `--brand-2`): `--brand`와 짝을 이루는 2차 강조색. 그라디언트(`.site-brand span`, `.reading-progress`)와 히어로 배경의 방사형 광채, 그리고 위키 문서의 의미론적 용법 두 곳 — math 콜아웃(`.callout[data-kind="math"]`)의 테두리·타이틀 틴트와 개념 지도 bridge 노드(`.map-node.bridge`) — 에 쓰입니다.

### Secondary
- **Pixel Purple** (`#a866ff`, Pixel 테마의 `--purple` = `--brand` 별칭): Pixel 테마가 활성화되면 Atlas의 파랑 대신 이 보라가 브랜드 색 역할을 맡습니다. 두 테마는 브랜드 색상 자체가 다릅니다.

### Neutral
- **Bg** (`#eef2f7` Atlas light / `#0d1118` Atlas dark): Atlas에서 `html`/`body`의 페이지 캔버스 색이며 `--paper`(카드 표면)와는 별개 토큰입니다. `window.__SITE_THEME_CONFIG__`의 네 가지 `theme-color` 메타 값(`#eef2f7`/`#0d1118`/`#f7f4ef`/`#15121b`)이 정확히 이 네 팔레트의 `--bg` 값과 일치합니다. Pixel은 `--bg: var(--paper)`로 별칭 처리해 캔버스와 카드 표면을 같은 색으로 합칩니다 — 그래서 Pixel만 보면 이 구분이 보이지 않습니다.
- **Paper** (`#ffffff` Atlas / `#f7f4ef` Pixel): 카드·패널 표면. Atlas에서는 페이지 배경(`--bg`)보다 밝은 별도 색입니다.
- **Ink** (`#172033` Atlas / `#1e1b26` Pixel): 본문 텍스트, Pixel에서는 테두리 색으로도 재사용됩니다(`--line-strong: var(--ink)`).
- **Muted** (`#5f6b7d` Atlas / `#756e7b` Pixel): 보조 텍스트, 메타데이터, 캡션.
- **Line** (`#dce2eb` Atlas / Pixel은 `--ink`를 그대로 선/테두리 색으로 재사용): 구분선과 테두리.

### Named Rules
**The Domain-Color Neutralization Rule.** Pixel 테마는 도메인별 4색 코딩(purple/mint/blue/yellow)을 UI 아이덴티티로 씁니다 — `.domain-card.purple:hover`, `.wiki-article-header.mint` 등. Atlas 테마는 `!important`로 이 4색을 명시적으로 죽이고 하나의 `--brand` 강조색으로 통일합니다(`atlas.css`: `.status{background:var(--paper-2)!important}`, `.wiki-article-header{background:var(--paper)!important}`, `.domain-card.purple:hover{background:var(--paper)}` 등). 새 화면을 Atlas 기준으로 만들 때 도메인별 색상 분기를 기대하면 안 됩니다 — 그 분기는 Pixel 전용입니다.

**The Fixed Dark Lab Rule.** `.wiki-document-page` 안의 항상 어두운 표면 집합 — `.lab`(과 `--viz-panel`을 쓰는 자식 `.control`), 그리고 `.lab`과 무관하게 문서 안에 독립적으로 등장하는 `.code-block`, `.concept-tooltip` — 은 활성 테마·색상 모드와 무관하게 항상 어둡습니다. 이는 하나의 토큰이 아니라 두 가지 장치가 겹친 결과입니다: (1) 두 테마가 `--viz-bg/--viz-panel/--viz-text/--viz-muted`에 우연히 동일한 다크 값을 지정하고, (2) `.lab` 내부 다수 요소가 토큰이 아닌 리터럴 hex(`#0d1118`, `#111827`, `#9db6ff`, `#8dabff`, `#344054` 등)로 하드코딩되어 있습니다. 파도 시각화 색(`--wave-1/2/3/--wave-sum`)만 `.wiki-document-page`에 고정 선언되어 있고, `--viz-*`는 이름과 달리 테마가 각자 재정의하는 토큰입니다.

**The Code Syntax Palette (2026-08-06 확립).** `.code-block`은 `site.js`의 자체 경량 토크나이저(외부 라이브러리 금지)로 하이라이팅되며, 토큰 색은 항상-다크 배경(`#111827`) 전용 고정 리터럴입니다: 키워드 `#7ba4ff`(=`--wave-1`), 문자열 `#53d8b1`(=`--wave-3`), 숫자 `#f2b866`, 주석·언어 라벨 `#94a3b8`(이탤릭). 마크업 계약은 `<pre class="code-block" data-lang="js|sql|python|c|bash"><code>…` — `data-lang`이 있으면 좌상단에 언어 라벨이 뜨고 하이라이팅이 적용되며, 없으면 무장식 코드로 남습니다. 가로 오버플로 표면(`.svg-scroll`, `.table-wrap`)에는 `site.js`가 스크롤 힌트(`.scroll-hint`, 첫 스크롤에 소멸)와 상시 표시 스크롤바를 자동 부착합니다 — 문서 쪽에서 할 일은 없습니다.

## Typography

**Display/Body Font (Atlas):** `Inter, Pretendard, "Noto Sans KR", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`
**Display/Body Font (Pixel, core.css 상속):** `-apple-system, BlinkMacSystemFont, "Pretendard Variable", Pretendard, "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif`
**Label/Mono Font:** `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace` (Pixel은 `--font-mono` 토큰으로 명시 선언; Atlas는 토큰을 쓰지 않고 라벨류 선택자 목록에 같은 스택을 직접 반복 지정합니다 — `.page-eyebrow,.hero-kicker,.portal-index,.section-label,...{font-family:ui-monospace,...}`)
**Equation Font:** `"STIX Two Text", Cambria, "Times New Roman", serif` — `.equation` 블록 전용. 시스템 전체에서 유일한 세리프.

**Character:** 본문/제목은 가변폭 산세리프로 통일해 문서 가독성을 우선하고, 라벨·메타데이터·코드류만 모노스페이스로 분리해 "본문은 읽는 글, 라벨은 기계적 태그"라는 위계를 만듭니다. Pixel 테마는 여기에 더해 헤딩·버튼 텍스트에도 모노스페이스를 적극적으로 섞어 터미널/프로토타입 느낌을 강조합니다.

### Hierarchy
- **Display** (h1 기본 굵기 700 — 어떤 테마도 `.landing-title`에 `font-weight`를 재지정하지 않음, `clamp(55px,8.8vw,132px)` Atlas / `clamp(48px,9.5vw,148px)` Pixel, line-height 0.92~0.93, letter-spacing `-0.08em`은 core.css에서 상속되어 Atlas에서도 그대로 유지됨): 랜딩 페이지 `.landing-title`.
- **Headline** (`.page-heading h1` 기준: 700, `clamp(44px,6vw,82px)`, line-height 1.07, letter-spacing `-0.055em`): 포트폴리오·위키·블로그 페이지 제목. 위키 문서 히어로(`.wiki-document-page .hero h1`)는 별도 컴포넌트로 `clamp(42px,7vw,76px)`·`-0.035em`을 쓰고, `.wiki-article-header h1`(구 v1 위키 헤더)은 `clamp(45px,7vw,82px)`를 씁니다 — 셋 다 비슷하지만 같은 규칙이 아니므로 섞어 평균 내지 않습니다.
- **Title** (`.wiki-document-page h2` 기준: 700~850, `clamp(29px,4vw,40px)`): 위키 문서 섹션 제목. 포트폴리오/이력서의 `.section-label h2`는 별도로 고정 `18px` 모노스페이스입니다.
- **Body** (400, `17px`, line-height 1.72~1.85, `.prose p`/`.prose li`는 최대 `76ch`): 본문 문단.
- **Label** (`.page-eyebrow` 기준: 800, `13px`, letter-spacing `0.08em`): 칩, 태그, 메타 정보, 네비게이션. 위키 문서 전용 `.eyebrow`는 별도로 `12px`/900/`0.13em`을 씁니다 — 같은 "라벨" 역할이라도 v1 셸과 위키 문서 셸이 각각 자기 값을 갖습니다.

### Named Rules
**The Mono-Label Rule.** 본문(가변폭 산세리프)과 라벨(모노스페이스)은 폰트 패밀리로 구분되어 절대 섞이지 않습니다. 새 라벨류 요소를 추가할 때 모노스페이스 스택을 임의로 생략하면 안 됩니다.

**The Heading Emphasis Rule (2026-08-04 교체).** 페이지 제목의 강조 스팬(`.page-heading h1 span`, `.landing-title span:last-child`)은 **단색 `var(--brand)`** 로 강조합니다 — Atlas에선 파랑, Pixel에선 보라로 테마를 따라갑니다. 과거의 보라→파랑→민트 그라디언트 텍스트는 사용자 결정으로 제거되었습니다(강조는 색 하나와 굵기로 충분하고, 그라디언트 종단부의 대비 저하 문제가 있었음). 새 페이지 제목은 `<h1>텍스트<br><span>강조 텍스트</span></h1>` 패턴을 그대로 쓰면 단색 강조가 적용됩니다. 그라디언트는 로고 마크(`.site-brand span`)와 진행바(`.reading-progress`) 같은 **비텍스트 표면에만** 남아 있습니다.

## Layout

**타입·반경 램프 (2026-08-04 확립, 점진 이주 정책).** frontmatter의 `typeRamp`와 `rounded`가 이제 정규 척도다: 관찰된 사용 빈도 클러스터에서 도출했고, **새 코드와 새 문서는 램프 값만 쓴다**. 기존 리터럴은 오류가 아니라 이주 대기 상태이며, 각 파일을 실질적으로 손대는 단위에서 가장 가까운 램프 값으로 옮긴다(디자인 훅의 잔여 지적이 이주 백로그 역할을 한다). 일괄 치환은 하지 않는다 — 시각 회귀를 검증 없이 만들기 때문이다.

명시적인 spacing 스케일 토큰은 여전히 없습니다 — 여백값은 컴포넌트별 리터럴(`7px, 9px, 12px, 13px, 17px, 18px, 21px, 22px, 26px, 30px, 34px...`)로 흩어져 있으며, 새 컴포넌트를 만들 때 기존 값 중 가장 가까운 리터럴을 참고하되, 이를 하나의 통일된 스케일인 것처럼 문서화해서는 안 됩니다.

**컨테이너 폭:** `--page: 1240px` (core.css)가 기준 폭이고 `.page-shell`이 `width:min(calc(100% - 40px), var(--page))`로 패딩을 얹습니다. 위키 문서는 별도로 `.wiki-document-page .shell{max-width:1380px}`를 씁니다. 블로그/카탈로그류 v2 콘텐츠는 `.prose-shell{width:min(calc(100% - 40px),900px)}`로 더 좁습니다.

**그리드 모델:** 위키 문서 본문은 `238px 사이드바 + 980px 본문`(`.shell`), 포트폴리오는 `1fr + 210px 레일`, 이력서는 `1.8fr + 0.8fr`, 위키 문서 사이드는 `1fr + 280px` — 페이지마다 고정 비율의 2단 그리드가 반복되되 정확한 값은 페이지별로 다릅니다.

**반응형 브레이크포인트가 파일마다 다릅니다** (통일되어 있지 않다는 사실 자체를 그대로 기록합니다): `core.css` 본문 규칙은 `1050px / 820px / 560px`, 같은 `core.css` 하단의 v2 콘텐츠 블록은 `980px / 700px`, `wiki-document.css`는 `1040px / 760px`, `atlas.css`는 `850px / 760px`를 각각 씁니다. 새 컴포넌트를 추가할 때 어느 파일에 넣느냐에 따라 인접 브레이크포인트 관례가 달라진다는 점을 유의해야 합니다.

**헤더:** 토큰 `--header-height: 66px`가 고정값이고 사이드바/목차류(`.toc`, `.wiki-article-rail`, `.portfolio-rail`)의 스티키 오프셋(`top: calc(var(--header-height) + 24~28px)`)은 이 토큰 값으로 계산됩니다. 다만 실제 렌더링된 헤더 높이는 다릅니다 — Atlas는 `min-height:64px`로 재정의하고, `820px` 이하 브레이크포인트(core.css)에서는 `min-height:58px`로 더 줄어듭니다. 즉 오프셋 계산은 토큰 기준이지 실측 헤더 높이 기준이 아닙니다.

## Elevation & Depth

두 테마는 깊이 표현에서 정반대 철학을 씁니다 — 이 대비가 이 시스템에서 가장 진술 가치가 높은 사실입니다.

**Pixel:** 하드 오프셋, 블러 없음. `--shadow: 6px 6px 0 var(--ink)`, `--shadow-small: 3px 3px 0 var(--ink)`(다크 모드는 `#060507`). 테두리는 굵고(2~5px) 항상 `var(--ink)` 실선. 반경은 항상 `0`. 상호작용은 "눌리는" 방향입니다 — 호버 시 `transform: translate(2px,2px)`와 함께 그림자가 `6px→1px`로 줄어들어, 종이가 표면에 눌려 붙는 듯한 느낌을 줍니다.

**Atlas:** 확산형 앰비언트 섀도. `--shadow: 0 18px 55px rgba(30,44,74,.09)`, `--shadow-small: 0 10px 30px rgba(30,44,74,.07)`. 테두리는 얇고(1px) 옅은 `--line`. 반경은 `22px`(패널) / `999px`(필/뱃지). 상호작용은 "떠오르는" 방향입니다 — 호버 시 `transform: translateY(-1px)`~`translateY(-3px)`와 함께 그림자가 더 크고 진해집니다.

### Named Rules
**The Inverted Lift Rule.** 같은 카드/버튼 컴포넌트라도 Pixel은 호버 시 그림자가 줄며 눌리고, Atlas는 호버 시 그림자가 커지며 떠오릅니다. 두 방향은 의도적으로 반대이며, 하나의 테마 문법을 다른 테마에 그대로 이식하면 시각적으로 어색해집니다.

**The Radius-Is-Theme Rule.** `--radius`(위키 `.card`가 소비하는 그 토큰)는 Pixel에서 `0`, Atlas에서 `22px`입니다. 동일한 `.card`/`.wiki-article-header`/`.domain-card`가 테마에 따라 각지거나 둥글게 렌더링됩니다 — 컴포넌트 코드가 아니라 활성 테마가 형태를 결정합니다.

## Shapes

**Pixel:** 각진 형태가 기본값입니다. `--radius: 0`이고 대부분의 표면(`.surface-panel`, `.project-card`, `.action-button`)이 사각형입니다. `.status-dot`은 core.css에서 각진 10×10 사각형(2px `--ink` 테두리 + 하드 그림자)으로 정의되어 Pixel에서는 그대로 각집니다 — 이를 원으로 바꾸는 것은 오히려 Atlas(`atlas.css`의 `border-radius:50%`)입니다. Pixel에서도 살아남는 진짜 원형 예외는 위키 문서의 `.step::before`와 `.solution-step>span`(둘 다 `wiki-document.css`에서 `border-radius:50%`인 카운터 배지)입니다 — `pixel.css`가 `.step` 컨테이너 자체는 `border-radius:0`으로 각지게 만들지만, 그 안의 `::before`/`span` 배지까지는 건드리지 않기 때문입니다. 테두리는 두껍고(2~5px) 항상 `var(--ink)` 실선 — 테두리 자체가 형태 언어의 일부입니다.

**Atlas:** 둥근 형태가 기본값입니다. 패널·카드는 `22~32px`(히어로는 `30~32px`까지), 버튼/입력은 `10~11px`, 칩/뱃지/상태 표시는 `999px`(완전한 필 형태). 테두리는 얇고(1px) `--line` — 형태 구분은 주로 반경과 그림자가 담당하고 테두리는 옅은 경계 역할만 합니다.

**공통(테마 무관):** 위키 문서의 의미 블록(`.callout[data-kind]`, `.hero-summary`)은 **kind 색으로 틴트된 1px 전체 테두리 + 옅은 배경 틴트 + kind 색 타이틀**로 구분합니다(2026-08-04, 굵은 좌측 보더에서 교체 — 사용자 결정). 의미→색 매핑(intuition=brand, math=brand-2, warning=orange, practice=green)은 교체 전과 동일하게 유지됩니다.

## Components

### Buttons
- **Shape:** Atlas는 `border-radius: 11px`, Pixel은 `border-radius: 0`.
- **Primary (`.action-button`):** Atlas — 배경 `var(--brand)`, 글자 `#fff`, 테두리 없음(`1px solid var(--brand)`로 배경과 동색), `box-shadow:none`. Pixel — 배경 `var(--yellow)`, 글자 `var(--ink)`, 테두리 `3px solid var(--ink)`, `box-shadow: var(--shadow-small)`.
- **Hover / Focus:** Atlas는 `background`를 `color-mix(in srgb, var(--brand) 86%, #000)`로 살짝 어둡게 하고 `translateY(-1px)` + 그림자 증가. Pixel은 그림자를 `1px 1px 0`으로 줄이며 `translate(2px,2px)`로 눌림.

### Cards / Containers
- **Corner Style:** `var(--radius)` 소비 — Atlas `22px`, Pixel `0`.
- **Background:** `var(--paper)` (Atlas 흰색 계열, Pixel 아이보리/다크 계열).
- **Shadow Strategy:** Elevation & Depth 섹션 참조 — 테마별로 정반대.
- **Border:** Atlas `1px solid var(--line)`, Pixel `3px solid var(--ink)`.
- **Internal Padding:** 대체로 `clamp(22px,4vw,34px)`(위키 `.card`) 또는 `22px`(포트폴리오 카드 본문) 리터럴.

### Inputs / Fields
- **Style:** `.wiki-search input`/`.catalog-toolbar input` — Atlas는 배경 `var(--paper-2)`, 테두리 `1px solid var(--line)`, 반경 `11px`. Pixel(core.css 상속)은 배경 `var(--paper)`, 테두리 `3px solid var(--ink)`, 반경 `0`.
- **Focus:** Atlas — `border-color: var(--brand)` + `box-shadow: 0 0 0 3px color-mix(in srgb, var(--brand) 14%, transparent)`. Pixel — `box-shadow: 4px 4px 0 var(--blue)`(색이 바뀐 하드 섀도 오프셋).

### Navigation
- **Style:** `.global-nav`는 모노스페이스, 800~900 굵기, `13px`. 현재 페이지는 `a[aria-current="page"]`로 표시 — Atlas는 `color:var(--brand)` + 옅은 배경 틴트, Pixel은 `background:var(--yellow)` + 실선 테두리. 데스크톱은 가로 나열, `820px` 이하(core.css 브레이크포인트)에서 `.nav-toggle` 버튼이 나타나고 메뉴가 절대 위치 드롭다운으로 전환됩니다(`data-open="true"`).
- **Header:** `position:sticky; top:0`, 높이 `--header-height`. Atlas는 `backdrop-filter:blur(18px)` + 반투명 `--bg`, Pixel(core.css)은 `backdrop-filter:blur(12px)` + 반투명 `--paper` + `border-bottom:3px solid var(--ink)`.

### Wiki Lab Panel (Signature Component)
`.wiki-document-page .lab`은 항상-다크 표면 집합(위 Named Rule 참조 — `.lab`·`.code-block`·`.concept-tooltip`)의 대표 컴포넌트로, 테마·색상 모드와 무관하게 항상 다크입니다. 내부에 SVG 인터랙티브 시각화(예: PCM 문서의 표본화/양자화/비트 전송률 랩), 슬라이더 컨트롤(`.lab-controls .control`), 라이브 리드아웃(`.lab-readout`)을 담습니다. 각 문서 디렉토리에 동거(co-located)하는 `labs.js`가 상대경로로 로드되어 해당 SVG를 그립니다. **관찰된 하드 규칙:** 저장소 전체(HTML/JS/SVG)를 조사한 결과 SVG presentation attribute(`stroke="..."`, `fill="..."`)에 `var(--token)`을 직접 넣은 사례가 0건입니다 — 항상 클래스 기반 CSS(`.plot-grid{stroke:var(--viz-grid)}`) 또는 `style="stroke:var(--x)"` 인라인 스타일을 통해서만 토큰을 SVG에 연결합니다.

### Catalog Rows (`.concept-row`)
카탈로그·최근 문서 목록의 행 컴포넌트. 계약은 **2-자식 마크업**(내용 `span` + `.concept-row-meta`)에 2열 그리드(`minmax(0,1fr) auto`)이고, `820px` 이하에서는 메타를 숨기고 1열로 접습니다. 마커 열을 가정한 옛 3~4열 그리드는 내용 열이 마커 폭에 끼여 글자 단위 세로 붕괴를 일으켰던 실결함이므로 되살리면 안 됩니다.

### Callouts (`data-kind` 문서 콜아웃)
`.callout[data-kind="intuition|math|warning|practice"]`는 **kind 색 틴트의 1px 전체 테두리 + 6~7% 배경 틴트 + kind 색 `.callout-title`** 로 종류를 구분합니다(2026-08-04 좌측 굵은 보더에서 교체): intuition → `--brand`, math → `--brand-2`, warning → `--orange`, practice → `--green`. kind 규칙은 색상만 지정하므로 Pixel 테마의 3px 각진 테두리 굵기와도 그대로 합성됩니다. 같은 언어가 `.hero-summary`(brand 틴트 패널)에도 적용됩니다.

## Do's and Don'ts

### Do:
- **Do** 새 화면을 만들 때 `--bg/--paper/--paper-2/--paper-3/--ink/--muted/--soft/--line/--line-strong/--brand/--brand-2/--cyan/--green/--orange/--red/--shadow/--shadow-small/--radius/--viz-*` 토큰만 참조하고, 색상 리터럴을 하드코딩하지 않는다 — 두 테마 모두에서 자동으로 맞물리게 하려면 이 방법뿐입니다.
- **Do** SVG에 토큰 색을 넣을 때 항상 클래스 기반 CSS 선택자나 `style="stroke:var(--x)"` 인라인 스타일을 쓴다. `stroke="var(--x)"`처럼 presentation attribute에 직접 넣으면 렌더링이 조용히 깨진다(`none` 또는 검정으로).
- **Do** Atlas 기준으로 화면을 설계할 때 도메인별 4색 코딩(purple/mint/blue/yellow)을 기대하지 않고, 단일 `--brand` 강조색 하나로 위계를 표현한다.
- **Do** 라벨·메타·태그류 텍스트에는 모노스페이스 스택을, 본문에는 가변폭 산세리프를 쓴다.

### Don't:
- **Don't** `core.css`만 보고 전체 토큰 계약이 거기 있다고 가정하지 않는다 — `--paper-2/-3`, `--soft`, `--line-strong`, `--brand/-2`, `--cyan/--green/--orange`, `--viz-*`는 `core.css`에 없고 활성 테마 스타일시트(Atlas는 전량 재선언, Pixel은 core 값 위에 별칭만 추가)가 채운다.
- **Don't** 하나의 컴포넌트에 Pixel의 하드 섀도 호버(눌림)와 Atlas의 리프트 호버(떠오름)를 섞지 않는다 — 두 방향은 테마별로 의도적으로 반대다.
- **Don't** 브레이크포인트를 다른 파일의 관례로 통일하려 하지 않는다 — `core.css`(1050/820/560), v2 블록(980/700), `wiki-document.css`(1040/760), `atlas.css`(850/760)는 실제로 서로 다르며 이는 관찰된 현재 상태다.
- **Don't** spacing 값을 하나의 통일된 스케일 토큰인 것처럼 문서화하지 않는다 — 현재는 컴포넌트별 리터럴만 존재한다.

---

## 이 문서를 만들며 실행하지 못한 플레이북 단계 (건너뜀, 은폐하지 않음)

- **Step 3 (정성적 언어를 위한 사용자 인터뷰, 2라운드):** 실행 불가 — 실시간 사용자 확인이 필요하지만 이 실행에서는 대화형 확인 라운드를 열 수 없었습니다. Overview의 North Star와 색상 서술어("Brand Blue" 등)는 사용자 확정이 아니라 관찰된 이름·역할을 그대로 옮긴 잠정 표현이며, 사용자 확인 전에는 확정된 브랜드 언어로 인용되어서는 안 됩니다.
- **Step 4b (`.impeccable/design.json` 사이드카 작성):** 건너뜀 — 이번 실행의 쓰기 범위가 스크래치패드 경로 하나로 한정되어 있고 저장소 파일을 편집하지 않기로 되어 있어, 사이드카를 실제 저장소에 쓸 수 없습니다.
- **Step 1.7 (브라우저 자동화로 렌더링된 computed style 샘플링):** 건너뜀 — 이번 조사는 정적 파일 읽기로만 수행되었고 브라우저 자동화 도구를 쓰지 않았습니다. 다만 이 시스템의 토큰이 전량 선언적(CSS 커스텀 프로퍼티)이라 정적 분석만으로도 실제 계산값을 신뢰할 수 있는 수준으로 재구성할 수 있었습니다.
