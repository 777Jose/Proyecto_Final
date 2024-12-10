function App() {}
window.onload = function (event) {
    var app = new App();
    window.app = app;
};

App.prototype.processingButton = function (event) {
    const btn = event.currentTarget;
    const carruselList = event.currentTarget.parentNode;
    const track = event.currentTarget.parentNode.querySelector('#track');
    const carrusel = track.querySelectorAll('.carrusel');

    const carruselWidth = carrusel[0].offsetWidth;
    const trackWidth = track.offsetWidth;
    const listWidth = carruselList.offsetWidth;

    track.style.left == "" 
        ? (leftPosition = track.style.left = 0) 
        : (leftPosition = parseFloat(track.style.left.slice(0, -2) * -1));
        
    btn.dataset.button == "button-prev" 
        ? prevAction(leftPosition, carruselWidth, track) 
        : nextAction(leftPosition, trackWidth, listWidth, carruselWidth, track);
};

let prevAction = (leftPosition, carruselWidth, track) => {
    if (leftPosition > 0) {
        track.style.left = `${-1 * (leftPosition - carruselWidth)}px`;
    }
};

let nextAction = (leftPosition, trackWidth, listWidth, carruselWidth, track) => {
    if (leftPosition < trackWidth - listWidth) {
        track.style.left = `${-1 * (leftPosition + carruselWidth)}px`;
    }
};

document.addEventListener("DOMContentLoaded", () => {
    // Funcionalidad para mostrar PDFs
    const buttons = document.querySelectorAll(".ver-pdf");
    const pdfContainer = document.getElementById("pdf-container");
    const pdfViewer = document.getElementById("pdf-viewer");

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            const pdfUrl = button.getAttribute("data-pdf");
            pdfViewer.src = pdfUrl;
            pdfContainer.style.display = "block";
        });
    });

    // Funcionalidad para menús desplegables
    const dropdownToggles = document.querySelectorAll(".dropdown-toggle");

    dropdownToggles.forEach(toggle => {
        toggle.addEventListener("click", (e) => {
            e.preventDefault();
            const dropdownMenu = toggle.nextElementSibling;

            // Alternar el estado visible/oculto del menú desplegable
            dropdownMenu.style.display = dropdownMenu.style.display === "block" ? "none" : "block";
        });
    });

    // Cerrar el menú desplegable si se hace clic fuera
    document.addEventListener("click", (e) => {
        dropdownToggles.forEach(toggle => {
            const dropdownMenu = toggle.nextElementSibling;
            if (!toggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
                dropdownMenu.style.display = "none";
            }
        });
    });
});

