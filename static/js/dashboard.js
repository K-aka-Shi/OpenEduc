// Script pour afficher/cacher le formulaire
console.log("tst")
const toggleButton = document.getElementById('toggleForm');
const formContainer = document.getElementById('formContainer');

toggleButton.addEventListener('click', () => {
    formContainer.classList.toggle('hidden');
});
