const lbl_giris = document.getElementById('lbl-giris');
const lbl_kayit = document.getElementById('lbl-kayit');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');

const passwordFields = document.querySelectorAll('.password');
const toggleIcons = document.querySelectorAll('.sifre-degistirme-simgesi');

toggleIcons.forEach((iconSpan, index) => {
  const input = passwordFields[index];
  const icon = iconSpan.querySelector('i');

  iconSpan.addEventListener('click', () => {
    const isPassword = input.type === 'password';
    input.type = isPassword ? 'text' : 'password';

    icon.classList.toggle('fa-eye');
    icon.classList.toggle('fa-eye-slash');
  });
});


function showLogin() {
  lbl_kayit.classList.remove('lbller2');
  lbl_giris.classList.add('lbller2');
  registerForm.classList.remove('active');
  loginForm.classList.add('active');
}

function showRegister() {
  lbl_giris.classList.remove('lbller2');
  lbl_kayit.classList.add('lbller2');
  loginForm.classList.remove('active');
  registerForm.classList.add('active');
}


// uyarı mesajlarını belirli bir müddet sonra ekrandan siler.
document.addEventListener("DOMContentLoaded", function () {
    setTimeout(() => {
      const alerts = document.querySelectorAll('.alert');
      alerts.forEach(alert => {
        alert.remove();  // Mesajları DOM'dan kaldır
      });
    }, 5000); // 5 saniye sonra
  });