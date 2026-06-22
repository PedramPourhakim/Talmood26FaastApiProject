import Swal from 'sweetalert2';


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
    const stepRegister = document.getElementById("step-register");
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
    document.getElementById("go-register").onclick = () => {
        emailStep.classList.add("hidden");
        stepRegister.classList.remove("hidden");
    };

    document.getElementById("back-login").onclick = () => {
        stepRegister.classList.add("hidden");
        emailStep.classList.remove("hidden");
    };
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

    document.getElementById("register-btn").onclick = async () => {
        // گرفتن مقادیر از ورودی‌ها
        const name = document.getElementById("reg-name").value;
        const family = document.getElementById("reg-family").value;
        const email = document.getElementById("reg-email").value;
        const phone = document.getElementById("reg-phone").value;

        // بررسی ساده برای خالی نبودن فیلدها (Client-side validation)
        if (!name || !family || !email || !phone) {
            alert("لطفاً تمامی فیلدها را پر کنید.");
            return;
        }

        try {
            // نمایش حالت بارگذاری (اختیاری)
            const registerBtn = document.getElementById("register-btn");
            registerBtn.disabled = true;
            registerBtn.innerText = "در حال ثبت‌نام...";

            // ارسال یک درخواست واحد برای ساخت Person و User با هم
            const response = await fetch("/AddPersonRegisterUser", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    name: name,
                    family_name: family,
                    email: email,
                    phone: phone,
                    is_admin: false, // مقادیر پیش‌فرض
                    is_rabbie: false
                })
            });

            const result = await response.json();
            console.log(result);
            if (!response.ok) {
                // استخراج پیام خطا از detail که در FastAPI تعریف کردیم
                const errorMessage =
                    result?.message ||
                    result?.detail?.[0]?.msg ||
                    result?.detail ||
                    "خطا در ثبت‌نام";

                throw new Error(errorMessage);
            }

            // اگر موفقیت‌آمیز بود
            alert("ثبت نام با موفقیت انجام شد ✅");

            // ۱. مخفی کردن فرم ثبت نام
            document.getElementById("step-register").classList.add("hidden");
            // ۲. نمایش فرم ایمیل (ورود)
            document.getElementById("step-email").classList.remove("hidden");
            // ۳. قرار دادن ایمیل ثبت‌نام شده در فیلد ورود برای راحتی کاربر
            document.getElementById("auth-email").value = email;

        } catch (error) {
            console.error("Registration Error:", error);
            alert(error.message);
        } finally {
            // فعال کردن مجدد دکمه
            const registerBtn = document.getElementById("register-btn");
            registerBtn.disabled = false;
            registerBtn.innerText = "ثبت نام";
        }
    };

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

document.querySelectorAll(".logout-btn").forEach(btn => {
    btn.addEventListener("click", async function (e) {

        e.preventDefault();

        const result = await Swal.fire({
            title: "خروج از حساب",
            text: "آیا مطمئن هستید که می‌خواهید خارج شوید؟",
            icon: "question",
            showCancelButton: true,
            confirmButtonText: "بله",
            cancelButtonText: "انصراف",
            reverseButtons: true
        });

        if (!result.isConfirmed)
            return;

        try {

            const res = await fetch("/logout", {
                method: "POST",
                credentials: "include"
            });

            if (!res.ok) {
                await Swal.fire(
                    "خطا",
                    "خروج از حساب انجام نشد",
                    "error"
                );
                return;
            }

            window.location.reload();

        } catch (err) {

            console.error(err);

            await Swal.fire(
                "خطا",
                "ارتباط با سرور برقرار نشد",
                "error"
            );
        }
    });
});

