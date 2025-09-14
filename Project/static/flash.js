/*------------ Toggle profile  ------------*/

function toggleProfile() {
            var card = document.getElementById("profileCard");
            card.style.display = (card.style.display === "block") ? "none" : "block";
        }

/* ----------- Flash message effect ------------- */

document.addEventListener('DOMContentLoaded', function() {
    let flashmessage = document.getElementById('flash-message');
    if (flashmessage){

        setTimeout(() => {
            flashmessage.style.opacity = '0';;
            flashmessage.style.transition = 'opacity 1s ease';
            setTimeout(() => {
                flashmessage.style.display = 'none';
            },1000)
        }, 3000)
    }
});

/*--------------login page effects------------------*/
document.addEventListener('DOMContentLoaded', function() {
    let loginBox = document.querySelector('.login-box');
    if (loginBox) {
        setTimeout(() => {
            loginBox.classList.add('show');
        },300);
    }
});

