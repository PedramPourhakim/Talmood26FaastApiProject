const paymentsContainer = document.getElementById("paymentsContainer");
const paymentsPagination = document.getElementById("paymentsPagination");
const paymentState = {
    page: 1,
    pageSize: 1,
    total: 0,
    status: ""
};


export async function loadPersonPayments() {
    paymentsContainer.innerHTML = `
<div class="rounded-3xl border border-gray-200 p-8 text-center">

    <div class="animate-pulse text-gray-500">

        در حال بارگذاری...

    </div>

</div>
`;

    try {
        const params = new URLSearchParams({

            limit: paymentState.pageSize,

            offset: (paymentState.page - 1) * paymentState.pageSize

        });

        if (paymentState.status) {

            params.append(
                "payment_status",
                paymentState.status
            );

        }

        const response = await fetch(
            `/payments/get_person_payments?${params.toString()}`,
            {
                credentials: "include"
            }
        );

        if (!response.ok)
            throw new Error();

        const data = await response.json();
        paymentState.total = data.total;
        document.getElementById("paymentCounter").textContent =
            `${paymentState.total.toLocaleString("fa-IR")} پرداخت`;

        renderPayments(data.items);

        paymentsContainer.classList.add("opacity-0");

        requestAnimationFrame(() => {

            paymentsContainer.classList.remove("opacity-0");

            paymentsContainer.classList.add(
                "transition-opacity",
                "duration-300"
            );

        });
        renderPagination();

    } catch {

        paymentsContainer.innerHTML = `
        <div class="rounded-3xl border border-red-200 bg-red-50 p-8 text-center">

            <div class="text-5xl mb-4">
                ⚠️
            </div>

            <h3 class="text-xl font-bold text-red-700">
                دریافت اطلاعات با خطا مواجه شد
            </h3>

            <p class="mt-2 text-red-600">
                لطفاً چند لحظه دیگر دوباره تلاش کنید.
            </p>

            <button
                id="retryPayments"
                class="mt-6 rounded-xl bg-red-600 px-5 py-3 text-white transition hover:bg-red-700">
                تلاش مجدد
            </button>

        </div>
    `;

        document
            .getElementById("retryPayments")
            ?.addEventListener("click", loadPersonPayments);

    }

}

function renderPagination() {

    const totalPages = Math.ceil(paymentState.total / paymentState.pageSize);

    if (totalPages <= 1) {
        paymentsPagination.innerHTML = "";
        return;
    }

    paymentsPagination.innerHTML = `
    
        <button
            id="previousPaymentsPage"
            class="cursor-pointer px-4 py-2 rounded-xl border border-gray-300 hover:bg-gray-100 transition
            ${paymentState.page === 1 ? "opacity-50 cursor-not-allowed" : ""}"
            ${paymentState.page === 1 ? "disabled" : ""}>
            قبلی
        </button>

        <div class="text-gray-700 font-semibold">

            صفحه ${paymentState.page.toLocaleString("fa-IR")}
            از
            ${totalPages.toLocaleString("fa-IR")}

        </div>

        <button
            id="nextPaymentsPage"
            class="cursor-pointer px-4 py-2 rounded-xl border border-gray-300 hover:bg-gray-100 transition
            ${paymentState.page === totalPages ? "opacity-50 cursor-not-allowed" : ""}"
            ${paymentState.page === totalPages ? "disabled" : ""}>
            بعدی
        </button>

    `;

    document
        .getElementById("previousPaymentsPage")
        ?.addEventListener("click", previousPage);

    document
        .getElementById("nextPaymentsPage")
        ?.addEventListener("click", nextPage);

}

async function previousPage() {

    if (paymentState.page <= 1)
        return;

    paymentState.page--;

    await loadPersonPayments();

    paymentsContainer.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}

async function nextPage() {

    const totalPages = Math.ceil(paymentState.total / paymentState.pageSize);

    if (paymentState.page >= totalPages)
        return;

    paymentState.page++;

    await loadPersonPayments();

    paymentsContainer.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });


}

function renderPayments(payments) {

    if (!payments.length) {
        renderEmptyState();
        return;
    }

    paymentsContainer.innerHTML = payments
        .map(buildPaymentCard)
        .join("");

}

function renderEmptyState() {
    paymentsContainer.innerHTML = `

<div
class="rounded-3xl border-2 border-dashed border-gray-200 py-16 px-6 text-center">

    <div class="text-6xl mb-5">
        💳
    </div>

    <h3 class="text-xl font-bold text-gray-700">

        هنوز پرداختی انجام نشده است

    </h3>

    <p class="mt-3 text-gray-500">

        اولین پرداخت شما اینجا نمایش داده خواهد شد.

    </p>

</div>

`;
}

function buildPaymentCard(payment) {

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

        ${buildStatusBadge(payment.status)}

    </div>

    <div
    class="mt-7 grid md:grid-cols-2 gap-5">

        ${buildInfoItem(
        "🏦",
        "صندوق",
        payment.payment_account.account_title
    )}

        ${buildInfoItem(
        "📅",
        "تاریخ ثبت",
        formatDate(payment.creation_date)
    )}

        ${buildInfoItem(
        "📝",
        "توضیحات",
        payment.description || "-"
    )}

        ${buildInfoItem(
        "✅",
        "تاریخ پرداخت",
        payment.paid_at
            ? formatDate(payment.paid_at)
            : "-"
    )}

    </div>

</div>

</article>

`;

}


function buildInfoItem(icon, title, value) {

    return `

<div
class="rounded-2xl bg-slate-50 p-4">

    <div
    class="flex items-center gap-2 text-gray-500 text-sm">

        <span>${icon}</span>

        ${title}

    </div>

    <div
    class="mt-2 text-gray-800 font-semibold">

        ${value}

    </div>

</div>

`;

}

function buildStatusBadge(status) {

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

function formatDate(dateString) {

    return new Date(dateString).toLocaleString("fa-IR");

}

document.querySelectorAll(".payment-filter").forEach(btn => {

    btn.onclick = () => {

        document.querySelectorAll(".payment-filter")
            .forEach(x => x.classList.remove("active"));

        btn.classList.add("active");

        paymentState.page = 1;
        paymentState.status = btn.dataset.status;

        loadPersonPayments();

    };
});


