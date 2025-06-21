const sayilar = document.querySelectorAll('.sayi');

sayilar.forEach(element => {
    hareket(element);
});

function hareket(sayi){
    let a = Number(sayi.textContent);
    for (let index = 0; index <= a; index++) {
        setTimeout(() => {
            sayi.textContent = index;    
        }, index * 100);
    }
}

function cevap_tipini_goster(select) {
    const soruBlok = select.closest('.soru-blok');
    const wrapper = soruBlok.querySelector('.secenek-wrapper');
    wrapper.innerHTML = '';

    const soruIndeks = soruBlok.querySelector('.soru-indeks').value;

    if (select.value === '1') {
        const input = document.createElement('input');
        input.type = 'text';
        input.placeholder = 'Şık yazınız';
        input.name = `secenekler_${soruIndeks}[]`;

        const ekleBtn = document.createElement('button');
        ekleBtn.type = 'button';
        ekleBtn.textContent = 'Şık Ekle';
        ekleBtn.style = "margin-top:10px; margin-right: 5px;";

        const geriAlBtn = document.createElement('button');
        geriAlBtn.type = 'button';
        geriAlBtn.textContent = 'Geri Al';
        geriAlBtn.style = "margin-top:10px;";

        ekleBtn.onclick = function () {
            const inputs = wrapper.querySelectorAll(`input[name="secenekler_${soruIndeks}[]"]`);
            if (inputs.length < 6) {
                const yeniInput = document.createElement('input');
                yeniInput.type = 'text';
                yeniInput.placeholder = 'Şık yazınız';
                yeniInput.name = `secenekler_${soruIndeks}[]`;
                wrapper.insertBefore(document.createElement('br'), ekleBtn);
                wrapper.insertBefore(yeniInput, ekleBtn);

                if (inputs.length + 1 === 6) {
                    ekleBtn.disabled = true;
                }
            }
        };

        geriAlBtn.onclick = function () {
            const inputs = wrapper.querySelectorAll(`input[name="secenekler_${soruIndeks}[]"]`);
            if (inputs.length > 1) {
                const sonInput = inputs[inputs.length - 1];
                const br = sonInput.previousSibling;
                wrapper.removeChild(sonInput);
                if (br && br.tagName === "BR") wrapper.removeChild(br);
                ekleBtn.disabled = false;
            }
        };

        wrapper.appendChild(input);
        wrapper.appendChild(document.createElement('br'));
        wrapper.appendChild(ekleBtn);
        wrapper.appendChild(geriAlBtn);
    }
}

function yeniSoruEkle() {
    const wrapper = document.getElementById('soru-wrapper');

    const soruDiv = document.createElement('div');
    soruDiv.className = 'soru-blok';
    soruDiv.style = "margin-top: 20px; margin-bottom: 20px; padding:10px; border:1px solid #ccc; border-radius:10px";

    soruDiv.innerHTML = `
        <label class="soru-etiket"></label><br/><br/>
        <input class='soru-indeks' type='hidden'>
        <input type="text" name="soru" placeholder="Soruyu Yazınız"> <br/><br/>
        <select class="cevap_type" onchange="cevap_tipini_goster(this)">
            <option>Cevap Tipini Seçiniz</option>
            <option value="1">Şıklar</option>
            <option value="2">Metin</option>
        </select> <br/>
        <div class="secenek-wrapper" style="margin-top: 10px;"></div>
        <button name='btnSoruIptal' type="button" onclick="soruyuSil(this)" style="margin-top:10px; color: red;">❌ Soruyu Geri Al</button>
    `;

    wrapper.appendChild(soruDiv);
    sorulariNumaralandir();
}

function soruyuSil(btn) {
    const soruDiv = btn.closest('.soru-blok');
    const soru_indeks = soruDiv.querySelector('.soru-indeks');
    if (soru_indeks.value == 1){
        return;
    }

    soruDiv.remove();
    sorulariNumaralandir(); // Silmeden sonra yeniden numaralandır
}

function sorulariNumaralandir() {
    const sorular = document.querySelectorAll('.soru-blok');
    sorular.forEach((soru, index) => {
        const etiket = soru.querySelector('.soru-etiket');
        const soru_indeks = soru.querySelector('.soru-indeks');
        const input = soru.querySelector('input[type="text"]');
        const soruNo = index + 1;
        etiket.textContent = `${soruNo}. Soruyu Yazınız`;
        input.placeholder = `${soruNo}. Soruyu Yazınız`;
        soru_indeks.value = soruNo;
        input.name = `soru_${soruNo}`;
    });
}

window.onload = yeniSoruEkle;
