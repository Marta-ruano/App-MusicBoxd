(() => {
    const stars = document.querySelectorAll("#stars-edit span");
    const input = document.getElementById("valoracion-edit-input");

    function setRating(value) {
        input.value = String(value);
        stars.forEach(s => {
            s.classList.toggle("active", Number(s.dataset.value) <= Number(value));
        });
    }

    if (input.value) setRating(input.value);

    stars.forEach(star => {
        star.addEventListener("click", () => setRating(star.dataset.value));
        star.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                setRating(star.dataset.value);
            }
        });
    });
})();
