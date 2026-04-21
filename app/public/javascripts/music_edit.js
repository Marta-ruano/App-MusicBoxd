const input = document.getElementById("file");
const preview = document.getElementById("preview");

if(input && preview){
    input.addEventListener("change", () => {
        const f = input.files && input.files[0];
        if(!f) return;

        const url = URL.createObjectURL(f);
        preview.src = url;

        preview.onload = () => {
            URL.revokeObjectURL(url);
        };
    });
}