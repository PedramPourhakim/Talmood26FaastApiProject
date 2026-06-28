import SlimSelect from 'slim-select';
import Swal from "sweetalert2";

// ====================== Variables ======================
let paymentTypeSlim = null;
let paymentAccountSlim = null;

const paymentModal = document.getElementById("paymentModal");
const closePaymentModal = document.getElementById("closePaymentModal");
const cancelPayment = document.getElementById("cancelPayment");

const paymentTypeSelect = document.getElementById("paymentTypeSelect");
const paymentAccountSelect = document.getElementById("paymentAccountSelect");
const paymentAmountInput = document.getElementById("paymentAmount");
const paymentDescriptionInput = document.getElementById("paymentDescription");
const submitPaymentButton = document.getElementById("submitPayment");

const currentUser = window.currentUser;
let paymentTypes = [];

// ====================== Event Listeners ======================
document.querySelectorAll(".sedagha").forEach(card => {
    card.addEventListener("click", async (event) => {
        event.preventDefault();

        if (!currentUser) {
            await Swal.fire({
                icon: "warning",
                title: "ورود لازم است",
                text: "برای پرداخت ابتدا وارد حساب کاربری شوید."
            });
            return;
        }

        openPaymentModal();
        await loadPaymentTypes();
    });
});

closePaymentModal.addEventListener("click", closePaymentModalHandler);
cancelPayment.addEventListener("click", closePaymentModalHandler);

paymentModal.addEventListener("click", (e) => {
    if (e.target === paymentModal) closePaymentModalHandler();
});

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !paymentModal.classList.contains("hidden")) {
        closePaymentModalHandler();
    }
});

// ====================== Modal Functions ======================
function openPaymentModal() {
    paymentModal.classList.remove("hidden");
    paymentModal.classList.add("flex");

}

function closePaymentModalHandler() {
    if (paymentTypeSlim) paymentTypeSlim.close();
    if (paymentAccountSlim) paymentAccountSlim.close();

    paymentModal.classList.remove("flex");
    paymentModal.classList.add("hidden");
}

// ====================== Load & Initialize ======================
async function loadPaymentTypes() {
    if (paymentTypes.length > 0) {
        initializeSlimSelects();
        return;
    }

    try {
        const res = await fetch("/payment_type/get_all_payment_types", {
            credentials: "include"
        });
        if (!res.ok) throw new Error();

        paymentTypes = await res.json();
        initializeSlimSelects();
    } catch {
        await Swal.fire({
            icon: "error",
            title: "خطا",
            text: "دریافت اطلاعات پرداخت با مشکل مواجه شد."
        });
        closePaymentModalHandler();
    }
}

function initializeSlimSelects() {
    if (paymentTypeSlim) paymentTypeSlim.destroy();
    if (paymentAccountSlim) paymentAccountSlim.destroy();

    paymentTypeSelect.innerHTML = '';
    paymentAccountSelect.innerHTML = '';

    // پر کردن نوع پرداخت
    paymentTypes.forEach(type => {
        const opt = document.createElement('option');
        opt.value = type.id;
        opt.textContent = type.title;
        paymentTypeSelect.appendChild(opt);
    });

    // ==================== نوع پرداخت ====================
    paymentTypeSlim = new SlimSelect({
        select: '#paymentTypeSelect',
        settings: {
            placeholderText: 'نوع پرداخت را انتخاب کنید',
            allowDeselect: true,
            searchPlaceholder: 'جستجو کنید...',
            searchText: 'موردی یافت نشد',
            dir: 'rtl',
            showSearch: true,
            searchHighlight: true,
        },
        events: {
            afterChange: (newVal) => {
                handlePaymentTypeChange(newVal?.[0]?.value);
            }
        }
    });

    // خیلی مهم: بعد از ساختن، هیچ گزینه‌ای انتخاب نشود
    paymentTypeSlim.setSelected('');

    // ==================== صندوق پرداخت ====================
    paymentAccountSlim = new SlimSelect({
        select: '#paymentAccountSelect',
        settings: {
            placeholderText: 'صندوق پرداخت را انتخاب کنید',
            allowDeselect: true,
            searchPlaceholder: 'جستجو کنید...',
            searchText: 'ابتدا نوع پرداخت را انتخاب کنید',
            dir: 'rtl',
            showSearch: true,
            searchHighlight: true,
        }
    });

    // خالی کردن اولیه صندوق پرداخت
    paymentAccountSlim.setData([]);
}

// ====================== Handle Change ======================
function handlePaymentTypeChange(value) {
    if (!paymentAccountSlim) return;

    // همیشه لیست را بروزرسانی کن، اما هیچ گزینه‌ای را به صورت خودکار انتخاب نکن
    if (!value) {
        paymentAccountSlim.setData([]);
        return;
    }

    const selectedType = paymentTypes.find(t => String(t.id) === String(value));

    if (!selectedType?.payment_accounts?.length) {
        paymentAccountSlim.setData([]);
        return;
    }

    const options = selectedType.payment_accounts.map(acc => ({
        text: acc.account_title,
        value: String(acc.id)
    }));

    paymentAccountSlim.setData(options);

    // مهم: هیچ گزینه‌ای را به صورت خودکار انتخاب نکن
    paymentAccountSlim.setSelected('');
}

// ====================== بقیه توابع ======================
// (formatAmountInput, getAmountValue, validatePaymentForm, resetPaymentForm, buildPaymentPayload و ...)

paymentAmountInput.addEventListener("input", formatAmountInput);

function formatAmountInput() {
    let value = Number(this.value.replace(/\D/g, ""));


    this.value = value
        ? value.toLocaleString("en-US")
        : "";
}

function getAmountValue() {
    return Number(paymentAmountInput.value.replace(/,/g, "")) || 0;
}

async function validatePaymentForm() {
    const typeId = paymentTypeSlim?.getSelected()?.[0];

    const accountId = paymentAccountSlim?.getSelected()?.[0];

    if (!typeId) {

        await Swal.fire({
            icon: "warning",
            title: "نوع پرداخت را انتخاب کنید."
        });
        paymentTypeSlim.open();
        return false;
    }

    if (!accountId) {

        await Swal.fire({
            icon: "warning",
            title: "صندوق پرداخت را انتخاب کنید."
        });
        paymentAccountSlim.open();
        return false;
    }
    const MIN_AMOUNT = 26000;
    if (getAmountValue() <= MIN_AMOUNT) {

        await Swal.fire({
            icon: "warning",
            title: "حداقل مبلغ پرداخت ۲۶,۰۰۰ تومان است."
        });
        paymentAmountInput.focus();
        return false;
    }

    return true;

}

function resetPaymentForm() {

    paymentAmountInput.value = "";
    paymentDescriptionInput.value = "";

    submitPaymentButton.disabled = false;

    document.getElementById("submitPaymentText").classList.remove("hidden");
    document.getElementById("submitPaymentLoading").classList.add("hidden");

    paymentTypeSlim?.setSelected("");

    paymentAccountSlim?.setData([]);

    paymentAccountSlim?.setSelected("");

}

submitPaymentButton.addEventListener("click", submitPayment);

function getSelectedPaymentAccount() {

    const accountId = paymentAccountSlim.getSelected()[0];

    for (const type of paymentTypes) {

        const account = type.payment_accounts.find(a => a.id === accountId);

        if (account) return account;
    }

    return null;
}

function buildPaymentPayload() {
    const account = getSelectedPaymentAccount();
    return {
        person_id: currentUser.person_id,
        payment_account_id: account.id,
        payment_account_title: account.account_title,
        amount: getAmountValue(),
        description: paymentDescriptionInput.value.trim()
    };
}

async function submitPayment() {

    if (!await validatePaymentForm())
        return;

    submitPaymentButton.disabled = true;

    document.getElementById("submitPaymentText").classList.add("hidden");
    document.getElementById("submitPaymentLoading").classList.remove("hidden");

    try {

        const response = await fetch("/payments", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(buildPaymentPayload())
        });

        const result = await response.json();
        window.location.href = result.payment_url;
        resetPaymentForm();

        closePaymentModalHandler();
        await Swal.fire({
            icon: "success",
            title: "پرداخت ثبت شد."
        });
    } catch (err) {

        await Swal.fire({
            icon: "error",
            title: err.message
        });

    }

}