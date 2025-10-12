/*---------------------------------- Toggle profile  -------------------------*/

function toggleProfile() {
            var card = document.getElementById("profileCard");
            card.style.display = (card.style.display === "block") ? "none" : "block";
        }

/*----------------------------- Organizer Type ----------------------------*/
document.addEventListener('DOMContentLoaded', function() {
    const roleSelect = document.getElementById('role');
    const organizerTypeDiv = document.getElementById('organizerType');

    roleSelect.addEventListener('change', function() {
        if (this.value === 'organizer') {
            organizerTypeDiv.style.display = 'block';
        } else {
            organizerTypeDiv.style.display = 'none';
        }
    });
});
/*----------------------------- Calendar ----------------------------*/



