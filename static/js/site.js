const menuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  const menuIcon = document.getElementById('menu-icon');

  function setIcon(open){
    if (!menuIcon) return;
    menuIcon.innerHTML = open
      ? `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M6 18L18 6M6 6l12 12"></path>`
      : `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"></path>`;
  }

  function openMenu(){
    if (!mobileMenu || !menuBtn) return;

    mobileMenu.classList.add('is-open');
    menuBtn.setAttribute('aria-expanded', 'true');
    setIcon(true);

    // ارتفاع دقیق (برای انیمیشن)
    mobileMenu.style.height = mobileMenu.scrollHeight + 'px';
  }

  function closeMenu(){
    if (!mobileMenu || !menuBtn) return;

    // از ارتفاع فعلی به 0 انیمیت شود
    mobileMenu.style.height = mobileMenu.scrollHeight + 'px';
    // force reflow
    mobileMenu.offsetHeight;

    mobileMenu.style.height = '0px';
    mobileMenu.classList.remove('is-open');
    menuBtn.setAttribute('aria-expanded', 'false');
    setIcon(false);
  }

  function toggleMenu(){
    const open = mobileMenu.classList.contains('is-open');
    open ? closeMenu() : openMenu();
  }

  if (menuBtn && mobileMenu) {
    // مقدار اولیه
    mobileMenu.style.height = '0px';
    menuBtn.setAttribute('aria-expanded', 'false');
    setIcon(false);

    menuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleMenu();
    });

    // کلیک روی لینک‌ها => بستن
    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => closeMenu());
    });

    // کلیک بیرون => بستن
    document.addEventListener('click', (e) => {
      if (!mobileMenu.classList.contains('is-open')) return;
      const clickedInsideMenu = mobileMenu.contains(e.target);
      const clickedBtn = menuBtn.contains(e.target);
      if (!clickedInsideMenu && !clickedBtn) closeMenu();
    });

    // Esc => بستن
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && mobileMenu.classList.contains('is-open')) {
        closeMenu();
      }
    });

    // اگر سایز صفحه رفت روی دسکتاپ، منو را ببند و استایل height را ریست کن
    const mq = window.matchMedia('(min-width: 768px)');
    mq.addEventListener?.('change', (ev) => {
      if (ev.matches) {
        closeMenu();
        mobileMenu.style.height = '';
      } else {
        mobileMenu.style.height = '0px';
      }
    });

    // بعد از باز شدن، height را "auto" نکن چون auto انیمیت نمی‌شود.
    // اما برای اینکه اگر محتوا تغییر کرد (فونت/لینک اضافه شد) درست بماند:
    // وقتی منو باز است و resize می‌شود، height را دوباره تنظیم می‌کنیم.
    window.addEventListener('resize', () => {
      if (mobileMenu.classList.contains('is-open')) {
        mobileMenu.style.height = mobileMenu.scrollHeight + 'px';
      }
    });
  }