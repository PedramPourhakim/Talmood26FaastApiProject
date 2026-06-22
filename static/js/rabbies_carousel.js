import EmblaCarousel from 'embla-carousel'
import Autoplay from 'embla-carousel-autoplay'
import Swal from 'sweetalert2';

const modal = document.getElementById("question-modal");
const modalRabbiName = document.getElementById("modal-rabbi-name");
const questionText = document.getElementById("question-text");

let selectedRabbiId = null;

document.addEventListener("DOMContentLoaded", async () => {

    const carousel = document.getElementById("rabbi-carousel");

    function getImageUrl(r) {
        return r.image || r.image_url || r.photo || "/static/images/default-rabbi.jpg";
    }

    function createCard(r) {

        const name = `${r.name || ""} ${r.family_name || ""}`.trim();

        return `
<div class="embla__slide">

    <div class="text-center rabbie-card cursor-pointer"
         data-id="${r.id}"
         data-name="${name}">

        <div class="w-64 h-64 mx-auto rounded-full overflow-hidden border-4 border-yellow-400 shadow-xl">

            <img
                src="${getImageUrl(r)}"
                alt="${name}"
                class="w-full h-full object-cover object-center rabbie_image">

        </div>
    
        <h3 class="mt-5 text-lg font-semibold text-white">
            ${name}
        </h3>

    </div>

</div>
`;
    }

    try {

        const res = await fetch("/person/get_rabbies");
        const data = await res.json();

        if (!data.length)
            return;
        carousel.innerHTML = data.map(createCard).join("");
        const images = carousel.querySelectorAll("img");

        await Promise.all(
            [...images].map(img =>
                img.complete
                    ? Promise.resolve()
                    : new Promise(resolve => {
                        img.onload = resolve;
                        img.onerror = resolve;
                    })
            )
        );
        document.querySelectorAll(".rabbie-card")
            .forEach(card => {

                card.addEventListener("click", () => {

                    selectedRabbiId = card.dataset.id;

                    modalRabbiName.innerText =
                        `سؤال از ${card.dataset.name}`;

                    modal.classList.remove("hidden");
                });

            });

        requestAnimationFrame(() => {

            const autoplay = Autoplay({
                delay: 2000,
                stopOnInteraction: false,
                stopOnMouseEnter: true,
            });

            const embla = EmblaCarousel(
                document.querySelector(".embla"),
                {
                    loop: true,
                    direction: "rtl",
                },
                [autoplay]
            );

            document.getElementById("rabbi-next")
                .addEventListener("click", () => embla.scrollNext());

            document.getElementById("rabbi-prev")
                .addEventListener("click", () => embla.scrollPrev());


        });
    } catch (err) {
        console.error(err);
    }

});
document.getElementById("close-question-modal")
    .addEventListener("click", () => {

        modal.classList.add("hidden");

        questionText.value = "";
    });

document.getElementById("send-question-btn")
    .addEventListener("click", async () => {

        if (!window.currentUser) {

            await Swal.fire(
                "ورود لازم است",
                "ابتدا وارد حساب کاربری خود شوید.",
                "warning"
            );

            return;
        }

        const question = questionText.value.trim();

        if (!question)
            return;

        try {

            const response = await fetch("/qa", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    question: question,
                    answer: null,
                    rabbie_id: selectedRabbiId,
                    talmid_id: window.currentUser.person_id

                })
            });

            if (!response.ok)
                throw new Error();

            modal.classList.add("hidden");

            questionText.value = "";

            await Swal.fire(
                "ثبت شد",
                "سؤال شما با موفقیت ثبت شد.",
                "success"
            );

        } catch {

            await Swal.fire(
                "خطا",
                "ثبت سؤال با مشکل مواجه شد.",
                "error"
            );
        }

    });