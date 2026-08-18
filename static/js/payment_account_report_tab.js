import * as picker from "persian-datepicker-element/dist/persian-datepicker-element.min.esm.js";

window.__picker = picker;


const fromPicker =
    document.getElementById("paymentReportFromDate");

const toPicker =
    document.getElementById("paymentReportToDate");

if (fromPicker != null && toPicker != null) {
    stylePicker("paymentReportFromDate");
    stylePicker("paymentReportToDate");
    fromPicker.addEventListener("change", (e) => {

        const g = e.detail.gregorian;

        paymentReportState.fromDate =
            `${g[0]}-${String(g[1]).padStart(2, "0")}-${String(g[2]).padStart(2, "0")}`;

        resetReportCursor();

        loadPaymentReport();

    });
    toPicker.addEventListener("change", (e) => {

        const g = e.detail.gregorian;

        paymentReportState.toDate =
            `${g[0]}-${String(g[1]).padStart(2, "0")}-${String(g[2]).padStart(2, "0")}`;

        resetReportCursor();

        loadPaymentReport();

    });
}

const paymentReportContainer =
    document.getElementById("paymentReportContainer");

const paymentReportPagination =
    document.getElementById("paymentReportPagination");

const paymentReportState = {

    pageSize: 1,
    currentPage: 1,
    cursorDate: null,
    cursorId: null,

    previousCursors: [],

    hasNext: false,

    status: "",

    search: "",

    fromDate: "",

    toDate: "",

    sortOrder: "desc"

};

export async function loadPaymentReport() {

    paymentReportContainer.innerHTML = `

<div class="rounded-3xl border border-gray-200 p-8 text-center">

    <div class="animate-pulse text-gray-500">

        در حال بارگذاری...

    </div>

</div>

`;

    try {

        const params = new URLSearchParams({

            page_size: paymentReportState.pageSize,

            sort_order: paymentReportState.sortOrder

        });

        if (paymentReportState.cursorDate) {

            params.append(
                "cursor_date",
                paymentReportState.cursorDate
            );

        }

        if (paymentReportState.cursorId) {

            params.append(
                "cursor_id",
                paymentReportState.cursorId
            );

        }

        if (paymentReportState.status) {

            params.append(
                "status",
                paymentReportState.status
            );

        }

        if (paymentReportState.search.trim()) {

            params.append(
                "search",
                paymentReportState.search.trim()
            );

        }

        if (paymentReportState.fromDate) {

            params.append(
                "from_date",
                paymentReportState.fromDate
            );

        }

        if (paymentReportState.toDate) {

            params.append(
                "to_date",
                paymentReportState.toDate
            );

        }

        const response = await fetch(
            `/payments/payment-report?${params.toString()}`,
            {
                credentials: "include",
                method: "Get"
            }
        );

        if (!response.ok)
            throw new Error();

        const data = await response.json();

        paymentReportState.hasNext = data.has_next;

        paymentReportState.nextCursor =
            data.next_cursor;

        // document.getElementById(
        //     "paymentReportCounter"
        // ).textContent =
        //     `${data.items.length.toLocaleString("fa-IR")} پرداخت`;

        renderPaymentReports(data.items);

        paymentReportContainer.classList.add("opacity-0");

        requestAnimationFrame(() => {

            paymentReportContainer.classList.remove("opacity-0");

            paymentReportContainer.classList.add(
                "transition-opacity",
                "duration-300"
            );

        });

        renderReportPagination();

    } catch {

        paymentReportContainer.innerHTML = `

<div class="rounded-3xl border border-red-200 bg-red-50 p-8 text-center">

    <div class="text-5xl mb-4">
        ⚠️
    </div>

    <h3 class="text-xl font-bold text-red-700">

        دریافت گزارش با خطا مواجه شد

    </h3>

    <p class="mt-2 text-red-600">

        لطفاً چند لحظه دیگر دوباره تلاش کنید.

    </p>

    <button
        id="retryPaymentReport"
        class="mt-6 rounded-xl bg-red-600 px-5 py-3 text-white hover:bg-red-700">

        تلاش مجدد

    </button>

</div>

`;

        document
            .getElementById("retryPaymentReport")
            ?.addEventListener(
                "click",
                loadPaymentReport
            );

    }

}

function renderReportPagination() {

    paymentReportPagination.innerHTML = `

<button
id="previousPaymentReport"
class="cursor-pointer px-4 py-2 rounded-xl border border-gray-300 hover:bg-gray-100 transition
${paymentReportState.previousCursors.length === 0
        ? "opacity-50 cursor-not-allowed"
        : ""}"
${paymentReportState.previousCursors.length === 0
        ? "disabled"
        : ""}>

قبلی

</button>

<div class="text-gray-700 font-semibold">

صفحه
${paymentReportState.currentPage.toLocaleString("fa-IR")}

</div>

<button
id="nextPaymentReport"
class="cursor-pointer px-4 py-2 rounded-xl border border-gray-300 hover:bg-gray-100 transition
${!paymentReportState.hasNext
        ? "opacity-50 cursor-not-allowed"
        : ""}"
${!paymentReportState.hasNext
        ? "disabled"
        : ""}>

بعدی

</button>

`;

    document
        .getElementById("previousPaymentReport")
        ?.addEventListener("click", previousReportPage);

    document
        .getElementById("nextPaymentReport")
        ?.addEventListener("click", nextReportPage);

}

async function nextReportPage() {
    if (!paymentReportState.hasNext)
        return;
    paymentReportState.currentPage++;
    paymentReportState.previousCursors.push({

        cursorDate:
        paymentReportState.cursorDate,

        cursorId:
        paymentReportState.cursorId

    });

    paymentReportState.cursorDate =
        paymentReportState.nextCursor.cursor_date;

    paymentReportState.cursorId =
        paymentReportState.nextCursor.cursor_id;

    await loadPaymentReport();

    paymentReportContainer.scrollIntoView({

        behavior: "smooth",
        block: "start"

    });

}

async function previousReportPage() {

    if (
        paymentReportState.previousCursors.length === 0
    )
        return;
    paymentReportState.currentPage--;
    const previous =
        paymentReportState.previousCursors.pop();

    paymentReportState.cursorDate =
        previous.cursorDate;

    paymentReportState.cursorId =
        previous.cursorId;

    await loadPaymentReport();

    paymentReportContainer.scrollIntoView({

        behavior: "smooth",
        block: "start"

    });

}

document
    .querySelectorAll(".payment-report-filter")
    .forEach(btn => {

        btn.onclick = () => {

            document
                .querySelectorAll(".payment-report-filter")
                .forEach(x => x.classList.remove("active"));

            btn.classList.add("active");

            paymentReportState.status = btn.dataset.status;

            resetReportCursor();

            loadPaymentReport();

        };

    });

document
    .getElementById("paymentReportSearch")
    ?.addEventListener("input", e => {

        paymentReportState.search =
            e.target.value;

        resetReportCursor();

        loadPaymentReport();

    });


document
    .getElementById("paymentReportSort")
    ?.addEventListener("change", e => {

        paymentReportState.sortOrder =
            e.target.value;

        resetReportCursor();

        loadPaymentReport();

    });

function resetReportCursor() {

    paymentReportState.cursorDate = null;

    paymentReportState.cursorId = null;

    paymentReportState.previousCursors = [];

}

function renderPaymentReports(payments) {

    if (!payments.length) {
        renderEmptyReportState();
        return;
    }

    paymentReportContainer.innerHTML = payments
        .map(buildPaymentReportCard)
        .join("");

}

function renderEmptyReportState() {

    paymentReportContainer.innerHTML = `

<div
class="rounded-3xl border-2 border-dashed border-gray-200 py-16 px-6 text-center">

    <div class="text-6xl mb-5">
        📊
    </div>

    <h3 class="text-xl font-bold text-gray-700">

        پرداختی برای این فیلتر پیدا نشد

    </h3>

    <p class="mt-3 text-gray-500">

        تنظیمات جستجو یا فیلترها را تغییر دهید.

    </p>

</div>

`;

}

function buildPaymentReportCard(payment) {

    return `

<article
class="group rounded-3xl border border-slate-200 bg-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">

<div class="p-7">

<div class="flex items-start justify-between">

<div>

<div class="text-gray-500 text-sm">

مبلغ پرداخت

</div>

<div class="mt-2 text-3xl font-extrabold text-blue-900">

${Number(payment.amount).toLocaleString("fa-IR")}

<span class="text-base font-medium">

تومان

</span>

</div>

</div>

${buildReportStatusBadge(payment.status)}

</div>

<div class="mt-7 grid md:grid-cols-2 xl:grid-cols-3 gap-5">

${buildReportInfoItem(
        "👤",
        "پرداخت کننده",
        `${payment.payer.name} ${payment.payer.family_name}`
    )}

${buildReportInfoItem(
        "🏦",
        "صندوق",
        payment.payment_account.title
    )}

${buildReportInfoItem(
        "📝",
        "توضیحات",
        payment.description || "-"
    )}

${buildReportInfoItem(
        "✅",
        "تاریخ پرداخت",
        payment.paid_at
            ? formatReportDate(payment.paid_at)
            : "-"
    )}

${buildReportInfoItem(
        "💳",
        "شماره شبا",
        payment.payment_account.sheba_number
    )}

${payment.ref_id
        ? buildReportInfoItem(
            "🧾",
            "کد پیگیری",
            payment.ref_id
        )
        : ""}

${payment.authority
        ? buildReportInfoItem(
            "🔑",
            "Authority",
            payment.authority
        )
        : ""}

${payment.card_pan
        ? buildReportInfoItem(
            "💳",
            "شماره کارت",
            payment.card_pan
        )
        : ""}

${payment.fee != null
        ? buildReportInfoItem(
            "💰",
            "کارمزد",
            Number(payment.fee).toLocaleString("fa-IR")
        )
        : ""}

</div>

</div>

</article>

`;

}

function buildReportInfoItem(icon, title, value) {

    return `

<div
class="rounded-2xl bg-slate-50 p-4">

<div
class="flex items-center gap-2 text-gray-500 text-sm">

<span>${icon}</span>

${title}

</div>

<div
class="mt-2 text-gray-800 font-semibold break-all">

${value}

</div>

</div>

`;

}

function buildReportStatusBadge(status) {

    switch (status) {

        case "paid":

            return `

<span
class="rounded-full bg-green-100 text-green-700 px-4 py-2 font-bold">

🟢 موفق

</span>

`;

        case "pending":

            return `

<span
class="rounded-full bg-yellow-100 text-yellow-700 px-4 py-2 font-bold">

🟡 در انتظار

</span>

`;

        case "failed":

            return `

<span
class="rounded-full bg-red-100 text-red-700 px-4 py-2 font-bold">

🔴 ناموفق

</span>

`;

        default:

            return "";

    }

}

function formatReportDate(dateString) {

    if (!dateString)
        return "-";

    return new Date(dateString).toLocaleString(
        "fa-IR",
        {
            timeZone: "Asia/Tehran",
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        }
    );

}

function stylePicker(id) {

    const picker = document.getElementById(id);

    const style = document.createElement("style");

    style.textContent = `
        .picker-container{
            width:100%;
            height:100%;
        }

        #date-input{
            width:100%;
            height:100%;
            padding:0;
            margin:0;
            border:none;
            outline:none;
            box-sizing:border-box;
            font:inherit;
            background:transparent;
        }
    `;

    picker.shadowRoot.appendChild(style);

}

