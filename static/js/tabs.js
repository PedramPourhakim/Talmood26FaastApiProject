import { loadQAs } from "./qa";
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
            await loadQAs();
        }

    });

});