const menuBtn = document.getElementById('mobile-menu-btn');
const mobileMenu = document.getElementById('mobile-menu');
const menuIcon = document.getElementById('menu-icon');

function setIcon(open) {
    if (!menuIcon) return;
    menuIcon.innerHTML = open
        ? `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M6 18L18 6M6 6l12 12"></path>`
        : `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"></path>`;
}

function openMenu() {
    if (!mobileMenu || !menuBtn) return;

    mobileMenu.classList.add('is-open');
    menuBtn.setAttribute('aria-expanded', 'true');
    setIcon(true);

    // ارتفاع دقیق (برای انیمیشن)
    mobileMenu.style.height = mobileMenu.scrollHeight + 'px';
}

function closeMenu() {
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

function toggleMenu() {
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

document.addEventListener("DOMContentLoaded", () => {

    const modal = document.getElementById("auth-modal");
    const openBtns = document.querySelectorAll(".open-auth-modal");
    const closeBtn = document.getElementById("close-auth-modal");

    const form = document.getElementById("auth-form");
    const emailInput = document.getElementById("auth-email");

    const emailStep = document.getElementById("step-email");
    const codeStep = document.getElementById("step-code");

    const sendBtn = document.getElementById("send-code-btn");
    const verifyBtn = document.getElementById("verify-btn");

    const codeInputs = document.querySelectorAll(".otp-input");

    const timer = document.getElementById("timer");
    const resendBtn = document.getElementById("resend-code");

    let userEmail = "";
    let userId = null;
    let verifying = false;
    let timerInterval = null;


    /* ---------------- MODAL ---------------- */

    openBtns.forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            modal.classList.remove("hidden");
            modal.classList.add("flex");
        });
    });

    closeBtn?.addEventListener("click", closeModal);

    modal?.addEventListener("click", (e) => {
        if (e.target === modal) closeModal();
    });

    function closeModal() {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
    }


    /* ---------------- LOGIN STEP ---------------- */

    form?.addEventListener("submit", async (e) => {

        e.preventDefault();

        userEmail = emailInput.value.trim();
        if (!userEmail) return;

        sendBtn.disabled = true;
        sendBtn.textContent = "در حال ارسال...";

        try {

            const res = await fetch("/users/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({email: userEmail})
            });

            const data = await res.json();

            if (!res.ok && res.status !== 200) {
                throw new Error(data.detail || "login failed");
            }

            emailStep.classList.add("hidden");
            codeStep.classList.remove("hidden");

            codeInputs[0].focus();

            startTimer();

        } catch (err) {
            console.log("error response : ", err);
            alert("ارسال ایمیل با خطا مواجه شد");

        }

        sendBtn.disabled = false;
        sendBtn.textContent = "ارسال کد تایید";

    });


    /* ---------------- OTP INPUT ---------------- */

    codeInputs.forEach((input, index) => {

        input.addEventListener("input", () => {

            input.value = input.value.replace(/\D/g, "");

            if (input.value && index < codeInputs.length - 1) {
                codeInputs[index + 1].focus();
            }

            checkAutoSubmit();

        });

        input.addEventListener("keydown", (e) => {

            if (e.key === "Backspace" && !input.value && index > 0) {
                codeInputs[index - 1].focus();
            }

        });

        input.addEventListener("paste", (e) => {

            e.preventDefault();

            const paste = e.clipboardData.getData("text");
            const digits = paste.replace(/\D/g, "").slice(0, 4);

            digits.split("").forEach((d, i) => {
                if (codeInputs[i]) {
                    codeInputs[i].value = d;
                }
            });

            codeInputs[digits.length - 1].focus();
            checkAutoSubmit();

        });

    });


    function getCode() {
        return [...codeInputs].map(i => i.value).join("");
    }


    function checkAutoSubmit() {
        const code = getCode();
        if (code.length === 4) {
            verifyCode();
        }
    }


    /* ---------------- VERIFY ---------------- */

    async function verifyCode() {

        if (verifying) return;

        const code = getCode();
        if (code.length !== 4) return;

        verifying = true;
        verifyBtn.disabled = true;

        try {

            const res = await fetch(`/users/verify`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: userEmail,
                    verification_code: Number(code)
                }),
                credentials: "include"
            });
            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.detail || "invalid code");
            }

            window.location.reload();

        } catch (err) {

            shakeInputs();
            clearInputs();

        }

        verifyBtn.disabled = false;
        verifying = false;
    }


    verifyBtn?.addEventListener("click", verifyCode);


    /* ---------------- INPUT EFFECTS ---------------- */

    function clearInputs() {
        codeInputs.forEach(i => i.value = "");
        codeInputs[0].focus();
    }

    function shakeInputs() {

        codeInputs.forEach(input => {
            input.classList.add("animate-shake");
            setTimeout(() => {
                input.classList.remove("animate-shake");
            }, 400);
        });

    }


    /* ---------------- TIMER ---------------- */

    function startTimer() {

        let time = 120;

        resendBtn.classList.add("hidden");
        timer.style.display = "block";

        clearInterval(timerInterval);

        timerInterval = setInterval(() => {

            let m = Math.floor(time / 60);
            let s = time % 60;

            timer.textContent =
                `${m}:${s < 10 ? "0" : ""}${s}`;

            time--;

            if (time < 0) {

                clearInterval(timerInterval);

                timer.style.display = "none";
                resendBtn.classList.remove("hidden");

            }

        }, 1000);

    }


    /* ---------------- RESEND ---------------- */

    resendBtn?.addEventListener("click", async () => {

        resendBtn.disabled = true;

        await fetch("/users/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({email: userEmail})
        });

        startTimer();

        resendBtn.disabled = false;

    });

});

function showCodeStep() {
    document.getElementById("step-email").classList.add("hidden");
    document.getElementById("step-code").classList.remove("hidden");

    document.querySelector(".otp-input").focus();
}

async function apiFetch(url, options = {}) {

    let res = await fetch(url, {
        ...options,
        credentials: "include"
    });

    if (res.status === 401) {

        await fetch("/users/refresh-token", {
            method: "POST",
            credentials: "include"
        });

        res = await fetch(url, {
            ...options,
            credentials: "include"
        });
    }

    return res;
}