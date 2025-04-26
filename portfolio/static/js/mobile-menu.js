// portfolio/static/js/mobile-menu.js

document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const mobileMenu = document.querySelector('.mobile-menu');
    const overlay = document.querySelector('.overlay');
    // Optionnel: un bouton de fermeture dans le menu
    // const closeButton = document.querySelector('.mobile-menu .close-btn'); 

    if (hamburger && mobileMenu && overlay) {
        
        // Fonction pour basculer le menu
        function toggleMenu() {
            hamburger.classList.toggle('active');
            mobileMenu.classList.toggle('open');
            overlay.classList.toggle('active');
            // Empêcher le scroll du body quand le menu est ouvert (optionnel)
            document.body.classList.toggle('mobile-menu-open'); 
        }

        // Écouteur sur le bouton hamburger
        hamburger.addEventListener('click', toggleMenu);

        // Écouteur sur l'overlay pour fermer le menu
        overlay.addEventListener('click', toggleMenu);

        // Optionnel: Écouteur sur un bouton de fermeture explicite
        // if (closeButton) {
        //     closeButton.addEventListener('click', toggleMenu);
        // }

        // Optionnel: Fermer le menu si un lien du menu est cliqué
        const menuLinks = mobileMenu.querySelectorAll('nav a');
        menuLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (mobileMenu.classList.contains('open')) {
                    toggleMenu();
                }
            });
        });

    } else {
        console.warn('Mobile menu elements (hamburger, mobile-menu, overlay) not found.');
    }
});

// Optionnel: Ajouter une classe CSS au body pour empêcher le scroll
/* Dans votre CSS (par exemple style.css):
body.mobile-menu-open {
    overflow: hidden;
}
*/