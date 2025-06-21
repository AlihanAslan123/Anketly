const navbar = document.getElementById('navbar');
let hamburger_button = document.querySelector('#open-sidebar-button');
let carpi_button = document.querySelector('#close-sidebar-button');
const dropdownmenu = document.querySelector(".dropdown-menu");
const dropdown = document.querySelector(".dropdown");
const kategoriler = dropdown.firstElementChild
const okIMG = kategoriler.firstElementChild

// hamburget butonunu görünmez yap. ve show klasıını ekle
function openSidebar(){
    navbar.classList.add('show');
    hamburger_button.style.display = "none";
}
function closeSidebar(){
    navbar.classList.remove('show');
    hamburger_button.style.display = "block";
}

// ekran büyüdüğünde hamburger butonu gözükmesin.
function checkScreenSize() {
    if (window.innerWidth >= 769) {
        hamburger_button.style.display = 'none'; 
    }else{
        hamburger_button.style.display = 'block'; 
    }

    
}


function kategori_listele(){

    const isVisible = dropdownmenu.style.display === "block";

    if (isVisible) {
        dropdownmenu.style.display = "none";
    } else {
        dropdownmenu.style.display = "block";
    }
}



window.addEventListener('resize',checkScreenSize);

kategoriler.addEventListener('click', () => {
    // Eğer okIMG elemanında 'cevir' sınıfı varsa, çıkar
    if (okIMG.classList.contains('cevir')) {
        okIMG.classList.remove('cevir');
    } else {
        // Eğer 'cevir' sınıfı yoksa, ekle
        okIMG.classList.add('cevir');
    }
});






// slideShow javascript 

let slideIndex = 0;
let slides = document.getElementsByClassName("mySlides");
let timer = null;

// Slideshow başlat
function showSlides() {
  for (let i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";  
  }
  
  slideIndex++;
  if (slideIndex > slides.length) {slideIndex = 1}    

  slides[slideIndex-1].style.display = "block";  

  timer = setTimeout(showSlides, 7000); // 7 saniyede bir değiş
}

// Manuel kontrol için
function plusSlides(n) {
  clearTimeout(timer); // Manuel müdahale olduğunda zamanı sıfırla
  slideIndex += n;

  if (slideIndex > slides.length) {slideIndex = 1}
  if (slideIndex < 1) {slideIndex = slides.length}

  for (let i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";  
  }

  slides[slideIndex-1].style.display = "block";

  timer = setTimeout(showSlides, 4000); // Sonra yine otomatik devam etsin
}

// Sayfa yüklenince başlasın
window.onload = function() {
  showSlides();
};











