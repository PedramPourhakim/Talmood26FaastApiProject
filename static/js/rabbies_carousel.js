import EmblaCarousel from 'embla-carousel'
import Autoplay from 'embla-carousel-autoplay'

document.addEventListener("DOMContentLoaded", async () => {

    const carousel = document.getElementById("rabbi-carousel");

    function getImageUrl(r) {
        return r.image || r.image_url || r.photo || "/static/images/default-rabbi.jpg";
    }

    function createCard(r) {

        const name = `${r.name || ""} ${r.family_name || ""}`.trim();

        return `
<div class="embla__slide">

    <div class="text-center">

        <div class="w-64 h-64 mx-auto rounded-full overflow-hidden border-4 border-yellow-400 shadow-xl">

    <img
        src="${getImageUrl(r)}"
        alt=""
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

        requestAnimationFrame(() => {

            const embla = EmblaCarousel(
                document.querySelector(".embla"),
                {
                    loop: true,
                    autoplay: true,
                    autoplaySpeed: 2000,
                    pauseOnHover: true,
                    direction: "rtl",
                },
                [Autoplay({delay: 2000})]
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
