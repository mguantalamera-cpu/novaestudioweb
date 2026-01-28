// ✅ MENÚ MÓVIL (antes faltaba toggleMenu y rompía el hamburger)
const menu = document.getElementById("menu");
const hamburger = document.querySelector(".hamburger");

function toggleMenu(forceClose = false) {
  if (!menu) return;

  const isOpen = menu.classList.contains("open");
  const nextState = forceClose ? false : !isOpen;

  menu.classList.toggle("open", nextState);

  if (hamburger) {
    hamburger.setAttribute("aria-expanded", String(nextState));
    hamburger.setAttribute("aria-label", nextState ? "Cerrar menú" : "Abrir menú");
  }
}

// Cerrar menú al clickar un enlace
if (menu) {
  menu.addEventListener("click", (e) => {
    const link = e.target.closest("a");
    if (link && menu.classList.contains("open")) toggleMenu(true);
  });
}

// Cerrar menú al clickar fuera (solo si está abierto)
document.addEventListener("click", (e) => {
  if (!menu || !hamburger) return;
  if (!menu.classList.contains("open")) return;

  const clickedInsideNav = e.target.closest("nav");
  if (!clickedInsideNav) toggleMenu(true);
});

// FORMULARIO DE CONTACTO
document.getElementById("formulario").addEventListener("submit", function (e) {
  e.preventDefault();

  const nombre = document.getElementById("nombre").value.trim();
  const email = document.getElementById("email").value.trim();
  const mensaje = document.getElementById("mensaje").value.trim();

  if (!nombre || !email || !mensaje) {
    alert("Por favor completa todos los campos.");
    return;
  }

  alert(`¡Gracias ${nombre}! Tu mensaje ha sido enviado.`);
  this.reset();
});

// BOTÓN WHATSAPP (si existe audio con id="pop-sound")
const whatsappBtn = document.querySelector(".whatsapp");
const popSound = document.getElementById("pop-sound");

if (whatsappBtn && popSound) {
  whatsappBtn.addEventListener("click", () => {
    popSound.currentTime = 0;
    popSound.play();
  });
}
