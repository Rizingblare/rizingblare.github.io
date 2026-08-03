(() => {
  'use strict';

  const root = document.documentElement;
  const config = window.__SITE_THEME_CONFIG__ || {};
  const allowedThemes = new Set(config.themes || []);
  const media = window.matchMedia?.('(prefers-color-scheme: dark)');

  const safeStorage = {
    get(key) {
      try { return window.localStorage.getItem(key); } catch { return null; }
    },
    set(key, value) {
      try { window.localStorage.setItem(key, value); } catch { /* localStorage is optional */ }
    }
  };

  const resolvedMode = (preference) => {
    if (preference === 'light' || preference === 'dark') return preference;
    return media?.matches ? 'dark' : 'light';
  };

  const updateThemeColor = () => {
    const theme = config.themeDetails?.[root.dataset.theme];
    const color = theme?.themeColor?.[root.dataset.colorMode];
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta && color) meta.content = color;
  };

  const updateResponsiveMedia = () => {
    document.querySelectorAll('img[data-media-responsive][data-media-variants]').forEach((image) => {
      let variants = [];
      try { variants = JSON.parse(decodeURIComponent(image.dataset.mediaVariants)); } catch { return; }
      const theme = root.dataset.theme;
      const mode = root.dataset.colorMode;
      const score = (variant) => {
        const themeExact = variant.themeIds?.includes(theme);
        const themeAny = variant.themeIds?.includes('*');
        const modeExact = variant.colorModes?.includes(mode);
        const modeAny = variant.colorModes?.includes('*');
        if (!(themeExact || themeAny) || !(modeExact || modeAny)) return -1;
        return (themeExact ? 2 : 0) + (modeExact ? 1 : 0);
      };
      const match = variants.map((variant) => [variant, score(variant)])
        .filter(([, value]) => value >= 0)
        .sort((a, b) => b[1] - a[1])[0]?.[0] || variants[0];
      if (match?.src && image.getAttribute('src') !== match.src) image.setAttribute('src', match.src);
    });
  };

  const updateControls = () => {
    document.querySelectorAll('[data-theme-picker]').forEach((picker) => {
      if (picker.value !== root.dataset.theme) picker.value = root.dataset.theme;
    });
    const preference = root.dataset.colorPreference || config.defaultColorMode || 'system';
    const labels = {
      system: ['◐', `시스템 색상 모드 사용 중 · 현재 ${root.dataset.colorMode === 'dark' ? '어두움' : '밝음'}`],
      light: ['☀︎', '밝은 색상 모드 사용 중'],
      dark: ['☾', '어두운 색상 모드 사용 중']
    };
    const [icon, label] = labels[preference] || labels.system;
    document.querySelectorAll('[data-color-mode-toggle]').forEach((button) => {
      button.textContent = icon;
      button.title = `${label}. 누르면 다음 모드로 전환합니다.`;
      button.setAttribute('aria-label', `${label}. 누르면 다음 모드로 전환합니다.`);
      button.dataset.preference = preference;
    });
  };

  const activateTheme = (themeId, { persist = true } = {}) => {
    const next = allowedThemes.has(themeId) ? themeId : config.defaultTheme;
    root.dataset.theme = next;
    document.querySelectorAll('link[data-theme-stylesheet]').forEach((link) => {
      link.disabled = link.dataset.themeStylesheet !== next;
    });
    if (persist) safeStorage.set(config.storageKeys?.theme, next);
    updateThemeColor();
    updateControls();
    updateResponsiveMedia();
    document.dispatchEvent(new CustomEvent('site:theme-change', { detail: { theme: next } }));
  };

  const activateColorPreference = (preference, { persist = true } = {}) => {
    const next = ['system', 'light', 'dark'].includes(preference) ? preference : 'system';
    root.dataset.colorPreference = next;
    root.dataset.colorMode = resolvedMode(next);
    if (persist) safeStorage.set(config.storageKeys?.colorMode, next);
    updateThemeColor();
    updateControls();
    updateResponsiveMedia();
    document.dispatchEvent(new CustomEvent('site:color-mode-change', {
      detail: { preference: next, resolved: root.dataset.colorMode }
    }));
  };

  document.querySelectorAll('[data-theme-picker]').forEach((picker) => {
    picker.addEventListener('change', () => activateTheme(picker.value));
  });
  document.querySelectorAll('[data-color-mode-toggle]').forEach((button) => {
    button.addEventListener('click', () => {
      const order = ['system', 'light', 'dark'];
      const current = root.dataset.colorPreference || 'system';
      activateColorPreference(order[(order.indexOf(current) + 1) % order.length]);
    });
  });
  media?.addEventListener?.('change', () => {
    if ((root.dataset.colorPreference || 'system') === 'system') activateColorPreference('system', { persist: false });
  });
  activateTheme(root.dataset.theme || config.defaultTheme, { persist: false });
  activateColorPreference(root.dataset.colorPreference || config.defaultColorMode || 'system', { persist: false });

  const navToggle = document.querySelector('.nav-toggle');
  const globalNav = document.querySelector('#global-nav');
  if (navToggle && globalNav) {
    const closeNav = () => {
      navToggle.setAttribute('aria-expanded', 'false');
      globalNav.removeAttribute('data-open');
    };
    navToggle.addEventListener('click', () => {
      const isOpen = navToggle.getAttribute('aria-expanded') === 'true';
      navToggle.setAttribute('aria-expanded', String(!isOpen));
      globalNav.toggleAttribute('data-open', !isOpen);
    });
    globalNav.addEventListener('click', (event) => {
      if (event.target.closest('a')) closeNav();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeNav();
    });
  }

  const dialogById = new Map(
    [...document.querySelectorAll('.certificate-dialog[id]')]
      .map((dialog) => [dialog.id.replace(/^certificate-/, ''), dialog])
  );
  document.addEventListener('click', (event) => {
    const openButton = event.target.closest('[data-certificate-open]');
    if (openButton) {
      const dialog = dialogById.get(openButton.dataset.certificateOpen);
      if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
      return;
    }
    const closeButton = event.target.closest('[data-dialog-close]');
    if (closeButton) {
      closeButton.closest('dialog')?.close();
      return;
    }
    if (event.target instanceof HTMLDialogElement && event.target.classList.contains('certificate-dialog')) {
      const box = event.target.getBoundingClientRect();
      const inside = event.clientX >= box.left && event.clientX <= box.right
        && event.clientY >= box.top && event.clientY <= box.bottom;
      if (!inside) event.target.close();
    }
  });

  const progress = document.querySelector('.reading-progress');
  const updateProgress = () => {
    if (!progress) return;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.width = `${max > 0 ? Math.min(100, window.scrollY / max * 100) : 0}%`;
  };
  window.addEventListener('scroll', updateProgress, { passive: true });
  window.addEventListener('resize', updateProgress);
  updateProgress();

  const article = document.querySelector('.wiki-document-page .article');
  const toc = document.querySelector('.wiki-document-page .toc');
  if (article && toc) {
    const headings = [...article.querySelectorAll('.article-body > section[id] > h2, .article-body > section[id] > .section-heading > h2')];
    const title = document.createElement('div');
    title.className = 'toc-title';
    title.textContent = '이 문서에서';
    toc.replaceChildren(title);
    headings.forEach((heading) => {
      const section = heading.closest('section[id]');
      const link = document.createElement('a');
      link.href = `#${section.id}`;
      link.textContent = heading.textContent.replace(/^\d+\.?\s*/, '');
      toc.append(link);
    });
    const links = [...toc.querySelectorAll('a')];
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        const visible = entries.filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (!visible) return;
        links.forEach((link) => link.setAttribute('aria-current', String(link.hash === `#${visible.target.id}`)));
      }, { rootMargin: '-16% 0px -70% 0px', threshold: [0, 0.1, 0.5] });
      headings.forEach((heading) => observer.observe(heading.closest('section')));
    }
  }

  const tooltip = document.querySelector('.concept-tooltip');
  let activeRef = null;
  const hideTooltip = () => {
    if (!tooltip) return;
    tooltip.dataset.open = 'false';
    activeRef = null;
  };
  const showTooltip = (ref) => {
    if (!tooltip) return;
    activeRef = ref;
    tooltip.querySelector('strong').textContent = ref.dataset.title || ref.textContent.trim();
    tooltip.querySelector('span').textContent = ref.dataset.body || '';
    tooltip.querySelector('em').textContent = ref.dataset.status === 'published'
      ? '클릭하면 독립 문서로 이동합니다.'
      : '독립 문서 작성 전: 도메인 카탈로그에서 해당 후보를 찾습니다.';
    tooltip.dataset.open = 'true';
    const rect = ref.getBoundingClientRect();
    const width = Math.min(330, window.innerWidth - 28);
    let left = rect.left + rect.width / 2 - width / 2;
    left = Math.max(14, Math.min(window.innerWidth - width - 14, left));
    let top = rect.top - tooltip.offsetHeight - 10;
    if (top < 10) top = rect.bottom + 10;
    tooltip.style.left = `${left}px`;
    tooltip.style.top = `${top}px`;
  };
  document.querySelectorAll('.concept-ref').forEach((ref) => {
    ref.addEventListener('mouseenter', () => showTooltip(ref));
    ref.addEventListener('mouseleave', hideTooltip);
    ref.addEventListener('focus', () => showTooltip(ref));
    ref.addEventListener('blur', hideTooltip);
  });
  window.addEventListener('scroll', () => activeRef && showTooltip(activeRef), { passive: true });
  window.addEventListener('resize', () => activeRef && showTooltip(activeRef));

  document.querySelector('[data-action="print"]')?.addEventListener('click', () => window.print());
  document.querySelectorAll('.code-block').forEach((block) => {
    const button = document.createElement('button');
    button.className = 'lab-button';
    button.type = 'button';
    button.textContent = '복사';
    button.style.cssText = 'position:absolute;right:10px;top:10px;padding:5px 9px;font-size:11px';
    block.style.position = 'relative';
    button.addEventListener('click', async () => {
      const text = block.textContent.replace(/^복사\s*/, '');
      try {
        await navigator.clipboard.writeText(text);
        button.textContent = '복사됨';
        window.setTimeout(() => { button.textContent = '복사'; }, 1200);
      } catch {
        button.textContent = '복사 실패';
      }
    });
    block.prepend(button);
  });

  document.addEventListener('knowledge:lab-ready', () => {
    document.body.dataset.labsReady = 'true';
  }, { once: true });
})();
