const LS_KEY = "musicboxd_favs";

function loadFavs(){
    try { return JSON.parse(localStorage.getItem(LS_KEY)) || {}; }
    catch { return {}; }
}

function saveFavs(favs){
    localStorage.setItem(LS_KEY, JSON.stringify(favs));
}

const favs = loadFavs();

document.querySelectorAll(".fav-star").forEach(star => {
    const key = star.dataset.key;
    const isFav = !!favs[key];

    star.dataset.fav = String(isFav);
    star.src = isFav ? "/public/img/star_yellow.png" : "/public/img/star_grey.png";
});

document.addEventListener("click", e => {
    const star = e.target.closest(".fav-star");
    if(!star) return;

    const key = star.dataset.key;
    const newValue = !(star.dataset.fav === "true");

    star.dataset.fav = String(newValue);
    star.src = newValue ? "/public/img/star_yellow.png" : "/public/img/star_grey.png";

    favs[key] = newValue;
    saveFavs(favs);
});