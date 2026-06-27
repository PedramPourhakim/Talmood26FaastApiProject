import Swal from "sweetalert2";

(async () => {
    const params = new URLSearchParams(window.location.search);

    const payment = params.get("payment");
    const refId = params.get("ref_id");

    if (payment) {

        if (payment === "success") {
            await Swal.fire({
                icon: "success",
                title: "پرداخت با موفقیت انجام شد",
                text: `کد پیگیری: ${refId}`
            });
        } else if (payment === "verified") {
            await Swal.fire({
                icon: "info",
                title: "این پرداخت قبلاً تأیید شده است",
                text: `کد پیگیری: ${refId}`
            });
        } else if (payment === "failed") {
            await Swal.fire({
                icon: "error",
                title: "پرداخت ناموفق بود"
            });
        }

        history.replaceState({}, "", window.location.pathname);
    }
})();