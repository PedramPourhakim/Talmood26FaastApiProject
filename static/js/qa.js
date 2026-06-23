let editingQaId = null;
import Swal from 'sweetalert2';


const currentUser = window.currentUser;

export async function loadQAs() {

    const tbody = document.getElementById("qa-table-body");

    tbody.innerHTML = "";

    try {

        const response = await fetch("/qa/get_all_questions_answers", {
            credentials: "include"
        });

        if (!response.ok) {

            tbody.innerHTML = `
            <tr>
                <td colspan="5" class="p-8 text-gray-500">
                    ابتدا وارد حساب کاربری شوید
                </td>
            </tr>
            `;

            return;
        }

        const qas = await response.json();

        if (!qas.length) {

            tbody.innerHTML = `
            <tr>
                <td colspan="5" class="p-8">
                    هنوز سوالی ثبت نشده است
                </td>
            </tr>
            `;

            return;
        }
        let editButtonText = "ویرایش"
        if (currentUser) {
            editButtonText = currentUser.is_rabbie
                ? "ویرایش جواب"
                : "ویرایش سوال";
        }

        qas.forEach(q => {

            let otherSideName = "-";

            if (currentUser) {

                otherSideName = currentUser.is_rabbie
                    ? `${q.talmid.name} ${q.talmid.family_name}`
                    : `${q.rabbie.name} ${q.rabbie.family_name}`;

            }

            tbody.innerHTML += `
            <tr class="border-b">
                 
                 <td class="p-4">
            ${otherSideName}
                    </td>
                 
                <td class="p-4 w-80">
                    <div
                        class="question-preview preview-text"
                        data-text="${q.question}">
                        ${q.question}
                    </div>
                </td>

                <td class="p-4 w-80">
                    <div
                        class="question-preview preview-text"
                        data-text="${q.answer ?? "-"}">
                        ${q.answer ?? "-"}
                    </div>
                </td>

                <td class="p-4">
                    ${new Date(q.creation_date).toLocaleDateString("fa-IR")}
                </td>

                <td class="p-4">
                    ${q.is_answered ? `<span class="bg-green-100 text-green-700 px-3 py-1 rounded-full">
                            پاسخ داده شده
                           </span>` : `<span class="bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full">
                            در انتظار پاسخ
                           </span>`}
                </td>

                <td class="p-4">

                    <button
                        class="edit-btn bg-blue-700 text-white px-3 py-2 rounded cursor-pointer"
                        data-id="${q.id}"
                        data-question="${q.question}"
                        data-answer="${q.answer ?? ""}">
                        ${editButtonText}
                    </button>

                    <button
                        class="delete-btn bg-red-700 text-white px-3 py-2 rounded cursor-pointer"
                        data-id="${q.id}">
                        حذف
                    </button>

                </td>

            </tr>
            `;

        });

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