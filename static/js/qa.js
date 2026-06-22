let editingQaId = null;
import Swal from 'sweetalert2';
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
        const currentUser = window.currentUser;
        qas.forEach(q => {

            const otherSideName = currentUser.is_rabbie ? `${q.talmid.name} ${q.talmid.family_name}` : `${q.rabbie.name} ${q.rabbie.family_name}`;

            tbody.innerHTML += `
            <tr class="border-b">
                 
                 <td class="p-4">
            ${otherSideName}
                    </td>
                 
                <td class="p-4 max-w-md">
                      <div
                    class="question-preview cursor-pointer"
                    title="${q.question}">
                        ${q.question}
                        </div>
                </td>

                <td class="p-4 max-w-md">
                     <div
                    class="question-preview cursor-pointer"
                    title="${q.answer ? q.answer : '-'}">
                        ${q.answer ? q.answer : '-'}
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
                        data-question="${q.question}">
                        ویرایش
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

    } catch (err) {

        console.error(err);

    }

}

function wireEvents() {

    document.querySelectorAll(".edit-btn")
        .forEach(btn => {

            btn.onclick = () => {

                editingQaId = btn.dataset.id;

                document.getElementById("edit-question").value = btn.dataset.question;

                document.getElementById("edit-qa-modal")
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

document.getElementById("save-edit-btn").onclick = async () => {

    const question = document.getElementById("edit-question").value;

    const qaResponse = await fetch(`/qa/${editingQaId}`, {
        credentials: "include"
    });

    const currentQa = await qaResponse.json();

    await fetch(`/qa/${editingQaId}`, {

        method: "PUT",

        credentials: "include",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            question: question,
            answer: currentQa.answer,
            rabbie_id: currentQa.rabbie_id,
            talmid_id: currentQa.talmid_id,
            is_answered: currentQa.is_answered
        })

    });

    document
        .getElementById("edit-qa-modal")
        .classList.add("hidden");

    await loadQAs();

};