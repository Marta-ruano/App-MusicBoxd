const tipoSelect = document.getElementById("tipo");
const seccionCancion = document.getElementById("section-cancion");
const seccionAlbum = document.getElementById("section-album");

const fileInput = document.getElementById("file");
const preview = document.getElementById("preview");

function updateSections() {
    const valor = tipoSelect.value;
    seccionCancion.classList.add("hidden");
    seccionAlbum.classList.add("hidden");

    if (valor === "Canción") seccionCancion.classList.remove("hidden");
    if (valor === "Álbum") seccionAlbum.classList.remove("hidden");
}

function updatePreview() {
    const file = fileInput.files[0];

    if (!file) {
        preview.style.display = "none";
        preview.src = "";
        return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
        preview.src = e.target.result;
        preview.style.display = "block";
    };

    reader.readAsDataURL(file);
}

tipoSelect.addEventListener("change", updateSections);
fileInput.addEventListener("change", updatePreview);

updateSections();