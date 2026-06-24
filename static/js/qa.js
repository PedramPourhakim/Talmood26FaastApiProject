let editingQaId = null;
import Swal from 'sweetalert2';

const currentUser = window.currentUser;
let currentPage = 1;

const pageSize = 5;

let currentFilter = "";

export async function loadQAs(page = currentPage) {

    const container = document.getElementById("qa-table-body");
    container.innerHTML = "";

    try {

        const params = new URLSearchParams();

        params.append(
            "limit",
            pageSize
        );

        params.append(
            "offset",
            (currentPage - 1) * pageSize
        );

        if (currentFilter !== "") {

            params.append(
                "is_answered",
                currentFilter
            );
        }

        const response = await fetch(
            `/qa/get_all_questions_answers?${params}`,
            {
                credentials: "include"
            }
        );

        if (!response.ok) {

            container.innerHTML = `
                <div class="text-center text-gray-500 p-10">
                    ابتدا وارد حساب کاربری شوید
                </div>
            `;

            return;
        }

         const result = await response.json();

        const qas = result.items;
        const total = result.total;

        const totalPages =
            Math.ceil(total / pageSize);

        document.getElementById("page-number")
            .innerText =
            `صفحه ${currentPage} از ${totalPages || 1}`;

        const nextBtn =
            document.getElementById("next-page-btn");

        const prevBtn =
            document.getElementById("prev-page-btn");

        nextBtn.disabled =
            currentPage >= totalPages;

        prevBtn.disabled =
            currentPage <= 1;

        nextBtn.classList.toggle(
            "opacity-50",
            nextBtn.disabled
        );

        prevBtn.classList.toggle(
            "opacity-50",
            prevBtn.disabled
        );

        if (!qas.length) {

            container.innerHTML = `
                <div class="text-center p-10 text-gray-500">
                    نتیجه‌ای یافت نشد
                </div>
            `;

            return;
        }

        const editButtonText =
            currentUser?.is_rabbie
                ? "ویرایش پاسخ"
                : "ویرایش سؤال";

        let html = "";

        qas.forEach(q => {

             const otherSideName =
                currentUser?.is_rabbie
                    ? `${q.talmid.name} ${q.talmid.family_name}`
                    : `${q.rabbie.name} ${q.rabbie.family_name}`;

            html += `

<div class="qa-card">

    <div class="flex justify-between items-center mb-6">

        <div>

            <div class="text-sm text-gray-400">

                ${
                currentUser.is_rabbie
                    ? "تلمید"
                    : "ربی"
            }

            </div>

            <div class="font-bold text-xl text-blue-900">

                ${otherSideName}

            </div>

        </div>

        ${
                q.is_answered
                    ?
                    `
                <span class="bg-green-100 text-green-700 px-4 py-2 rounded-full">

                    پاسخ داده شده

                </span>
                `
                    :
                    `
                <span class="bg-yellow-100 text-yellow-700 px-4 py-2 rounded-full">

                    در انتظار پاسخ

                </span>
                `
            }

    </div>


    <div class="space-y-4">

        <div>

            <div class="mb-2 font-bold text-blue-900">

                ❓ سوال

            </div>

            <div
                class="question-bubble preview-text cursor-pointer"
                data-text="${q.question}">

                ${q.question}

            </div>

        </div>


        <div>

            <div class="mb-2 font-bold text-gray-700">

                💬 پاسخ

            </div>

            <div
                class="
                answer-bubble
                preview-text
                cursor-pointer
                ${!q.answer ? "empty-answer" : ""}
                "
                data-text="${q.answer ?? "-"}">

                ${q.answer ?? "هنوز پاسخی ثبت نشده است"}

            </div>

        </div>

    </div>


    <div class="mt-8 flex flex-wrap justify-between items-center gap-4">

        <div class="text-gray-400 text-sm">

            📅
            ${new Date(q.creation_date).toLocaleDateString("fa-IR")}

        </div>

        <div class="flex gap-3">

            <button
                    class="edit-btn cursor-pointer bg-blue-800 text-white px-5 py-2 rounded-xl"

                    data-id="${q.id}"
                    data-question="${q.question}"
                    data-answer="${q.answer ?? ""}">

                ${editButtonText}

            </button>


            <button
                    class="delete-btn cursor-pointer bg-red-700 text-white px-5 py-2 rounded-xl"
                    data-id="${q.id}">

                حذف

            </button>

        </div>

    </div>

</div>

`;
        });

        container.innerHTML = html;

        wireEvents();

        wirePreviewEvents();

    } catch (err) {

        console.error(err);

    }

}

function wireEvents() {

    document.querySelectorAll(".edit-btn")
        .forEach(btn => {

            btn.onclick = () => {

                editingQaId = btn.dataset.id;
                const title = document.getElementById("edit-modal-title");
                const textarea = document.getElementById("edit-question");
                const saveBtn = document.getElementById("save-edit-btn");
                if (currentUser != null && currentUser.is_rabbie) {

                    title.innerText = "ویرایش پاسخ";

                    textarea.placeholder =
                        "پاسخ خود را وارد کنید...";

                    textarea.value = btn.dataset.answer ?? "";

                    saveBtn.innerText = "ذخیره پاسخ";

                } else {

                    title.innerText = "ویرایش سوال";

                    textarea.placeholder =
                        "سوال خود را وارد کنید...";

                    textarea.value = btn.dataset.question;

                    saveBtn.innerText = "ذخیره سوال";

                }

                document
                    .getElementById("edit-qa-modal")
                    .classList.remove("hidden");

            };

        });

    document.querySelectorAll(".delete-btn")
        .forEach(btn => {

            btn.onclick = async () => {

                const result = await Swal.fire({
                    title: "حذف سوال",
                    text: "آیا از حذف این سوال مطمئن هستید؟",
                    icon: "warning",
                    showCancelButton: true,
                    confirmButtonText: "بله، حذف شود",
                    cancelButtonText: "انصراف",
                    reverseButtons: true,
                    customClass: {
                        confirmButton: "bg-red-700 text-white px-4 py-2 rounded mx-2 cursor-pointer",
                        cancelButton: "bg-gray-500 text-white px-4 py-2 rounded mx-2 cursor-pointer"
                    },
                    buttonsStyling: false
                });

                if (!result.isConfirmed)
                    return;

                const response = await fetch(`/qa/${btn.dataset.id}`, {
                    method: "DELETE",
                    credentials: "include"
                });

                if (response.ok) {

                    await Swal.fire({
                        title: "حذف شد",
                        text: "سوال با موفقیت حذف شد.",
                        icon: "success",
                        timer: 1500,
                        showConfirmButton: false
                    });

                    await loadQAs();

                } else {

                    await Swal.fire({
                        title: "خطا",
                        text: "حذف سوال با مشکل مواجه شد.",
                        icon: "error"
                    });

                }

            };

        });
}

function wirePreviewEvents() {

    document.querySelectorAll(".preview-text")
        .forEach(item => {

            item.onclick = () => {

                document.getElementById("full-text").innerText =
                    item.dataset.text;

                document.getElementById("text-modal")
                    .classList.remove("hidden");

            };

        });

}

document.getElementById("save-edit-btn").onclick = async () => {

    const text =
        document.getElementById("edit-question").value.trim();

    if (!text) {

        await Swal.fire({
            title: "خطا",
            text: currentUser.is_rabbie
                ? "لطفاً پاسخ را وارد کنید."
                : "لطفاً سؤال را وارد کنید.",
            icon: "warning"
        });

        return;
    }

    const qaResponse = await fetch(`/qa/${editingQaId}`, {
        credentials: "include"
    });

    const currentQa = await qaResponse.json();
    let payload;

    if (currentUser && currentUser.is_rabbie) {

        payload = {
            question: currentQa.question,
            answer: text,
            rabbie_id: currentQa.rabbie_id,
            talmid_id: currentQa.talmid_id,
            is_answered: true
        };

    } else {

        payload = {
            question: text,
            answer: currentQa.answer,
            rabbie_id: currentQa.rabbie_id,
            talmid_id: currentQa.talmid_id,
            is_answered: currentQa.is_answered
        };

    }
    await fetch(`/qa/${editingQaId}`, {

        method: "PUT",

        credentials: "include",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(payload)

    });

    document
        .getElementById("edit-qa-modal")
        .classList.add("hidden");

    await loadQAs();

};
document
    .getElementById("close-edit-btn")
    .addEventListener("click", () => {

        document
            .getElementById("edit-qa-modal")
            .classList.add("hidden");

    });
const modal = document.getElementById("edit-qa-modal");

modal.addEventListener("click", (e) => {

    if (e.target === modal) {

        modal.classList.add("hidden");

    }

});
document.addEventListener("keydown", (e) => {

    if (e.key === "Escape") {

        document
            .getElementById("edit-qa-modal")
            .classList.add("hidden");

    }

});

document.getElementById("close-text-modal")
    .onclick = () => {

    document.getElementById("text-modal")
        .classList.add("hidden");

};

const textModal = document.getElementById("text-modal");

textModal.addEventListener("click", e => {

    if (e.target === textModal) {

        textModal.classList.add("hidden");

    }

});
document.addEventListener("keydown", e => {

    if (e.key === "Escape") {

        document.getElementById("text-modal")
            .classList.add("hidden");

    }

});
document
    .getElementById("qa-filter")
    ?.addEventListener("change", async (e) => {

        currentFilter = e.target.value;
        currentPage = 1;

        await loadQAs();
    });
document
    .getElementById("next-page-btn")
    ?.addEventListener("click", async () => {

        currentPage++;

        await loadQAs();
    });

document
    .getElementById("prev-page-btn")
    ?.addEventListener("click", async () => {

        if (currentPage === 1)
            return;

        currentPage--;

        await loadQAs();
    });
