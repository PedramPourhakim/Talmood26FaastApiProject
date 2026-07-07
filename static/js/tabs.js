import { loadQAs } from "./qa";
import { loadPersonPayments } from "./payment_tab";
import { loadPaymentReport } from "./payment_account_report_tab.js";
import Swal from "sweetalert2";

const currentuser = window.currentUser;

document.querySelectorAll(".tab-btn").forEach(btn => {

    btn.addEventListener("click", async () => {

        document
            .querySelectorAll(".tab-content")
            .forEach(x => x.classList.add("hidden"));

        document
            .querySelectorAll(".tab-btn")
            .forEach(x => {

                x.classList.remove(
                    "border-blue-900",
                    "text-blue-900",
                    "border-b-4"
                );

                x.classList.add("text-gray-500");

            });

        document
            .getElementById(btn.dataset.tab)
            .classList.remove("hidden");

        btn.classList.remove("text-gray-500");

        btn.classList.add(
            "border-blue-900",
            "text-blue-900",
            "border-b-4"
        );

        if (btn.dataset.tab === "qa-tab") {

            if (currentuser) {

                await loadQAs();

            } else {

                await Swal.fire({
                    title: "خطا",
                    text: "ورود/ثبت نام الزامی می‌باشد",
                    icon: "error"
                });

            }

        }

        else if (btn.dataset.tab === "payments-tab") {

            if (currentuser) {

                await loadPersonPayments();

            } else {

                await Swal.fire({
                    title: "خطا",
                    text: "ورود/ثبت نام الزامی می‌باشد",
                    icon: "error"
                });

            }

        }

        else if (btn.dataset.tab === "payment-report-tab") {

            if (
                currentuser &&
                currentuser.payment_account_ids &&
                currentuser.payment_account_ids.length > 0
            ) {

                await loadPaymentReport();

            } else {

                await Swal.fire({
                    title: "خطا",
                    text: "شما مجوز مشاهده گزارش صندوق را ندارید.",
                    icon: "error"
                });

            }

        }

    });

});