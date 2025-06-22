from flask import Flask,render_template,request, Blueprint, flash ,redirect, url_for, abort
from utils import resim_yukle,insert_anket,get_db_engine,get_logger
from flask_login import login_required,current_user
from sqlalchemy import text

process = Blueprint(
    'process',
    __name__,
    template_folder='templates',
    static_folder='static'
)

engine = get_db_engine()
logger = get_logger()

@process.route('/anketOlustur/olustur',methods=['POST'])
@login_required
def post_anket():
    anket_adi = request.form.get('anket-adi')
    anket_aciklamasi = request.form.get('description')
    kategori_id = request.form.get('kategori')
    if kategori_id and kategori_id.isdigit():
        kategori_id = int(kategori_id)
    resim = request.files.get('image')
    if resim and resim_yukle(resim) == False:
        flash('Hatalı resim yüklemesi','error')
        return redirect(url_for('account.create_anket'))
    yayin_tipi = request.form.get('sekil')
    
    sorular = sorulari_getir()
    # [{'soru': 'xx', 'secenekler': ['q', 'a']}, {'soru': 'dsadad', 'secenekler': None}]
    insert_anket(anket_adi,anket_aciklamasi,kategori_id,resim,yayin_tipi,sorular)
    flash('Anketiniz başarıyla oluşturuldu.','success')
    return render_template('dashboard.html')
    
    
    
@process.route('/anketCoz/<uniqid>')
@login_required
def gizli_anket_getir(uniqid):
    
    with engine.connect() as conn:
        
        anket_id = conn.execute(text('SELECT anket_id FROM [dbo].[private_anket] where anket_link = :anket_link'),{'anket_link':uniqid}).fetchone()[0]
        
        if anket_id is None:
            logger.error('hatalı link')
            abort(404)
        logger.info('doğru link')
        
        id_check = conn.execute(text('select id from tbl_anket where id= :id'),{'id':anket_id}).fetchone()
        if id_check is None:
            logger.error('anket_id si bulunamadı')
            abort(404)
        
        result_tbl_anket = conn.execute(text('''
            SELECT kategori_id, title, picture, description 
            FROM tbl_anket 
            WHERE id = :id and is_private = 1
        '''), {'id': anket_id}).fetchone()
        
        if result_tbl_anket is None:
            logger.error('anket_bulunamadı')
            abort(404)
        
        result_tbl_sorular = conn.execute(text('''
            SELECT id,soru_text,cevap_tipi,soru_numarasi FROM tbl_sorular WHERE anket_id = :anket_id order by soru_numarasi
        '''), {'anket_id': anket_id}).fetchall()
        
        sorular_liste = []
        for soru in result_tbl_sorular:
            secenekler = conn.execute(text('''
                select id,secenek_text from tbl_secenekler where soru_id = :soru_id
            '''),{'soru_id':soru.id}).fetchall()
            
            sorular_liste.append({
                'id': soru.id,
                'soru_text': soru.soru_text,
                'cevap_tipi': soru.cevap_tipi,
                'soru_numarasi':soru.soru_numarasi,
                'secenekler': secenekler
            })
    
    return render_template('anket.html',anket=result_tbl_anket, sorular = sorular_liste)
        
        
        
        


@process.route('/ankets/<id>')
@login_required
def anket_getir(id):
    
    '''
        public oluşturulan anketleri id sine göre getirir.
    '''
        
    with engine.connect() as conn:
        
        id_check = conn.execute(text('select id from tbl_anket where id= :id'),{'id':id}).fetchone()
        if id_check is None:
            logger.error('anket_id si bulunamadı')
            abort(404)
        
        result_tbl_anket = conn.execute(text('''
            SELECT id,kategori_id, title, picture, description 
            FROM tbl_anket 
            WHERE id = :id and is_private = 0
        '''), {'id': id}).fetchone()
        
        if result_tbl_anket is None:
            logger.error('anket_bulunamadı')
            abort(404)
        
        result_tbl_sorular = conn.execute(text('''
            SELECT id,soru_text,cevap_tipi,soru_numarasi FROM tbl_sorular WHERE anket_id = :anket_id order by soru_numarasi
        '''), {'anket_id': id}).fetchall()
        
        sorular_liste = []
        for soru in result_tbl_sorular:
            secenekler = conn.execute(text('''
                select id,secenek_text from tbl_secenekler where soru_id = :soru_id
            '''),{'soru_id':soru.id}).fetchall()
            
            sorular_liste.append({
                'id': soru.id,
                'soru_text': soru.soru_text,
                'cevap_tipi': soru.cevap_tipi,
                'soru_numarasi':soru.soru_numarasi,
                'secenekler': secenekler
            })
    
    return render_template('anket.html',anket=result_tbl_anket, sorular = sorular_liste, cozulmusmu=anket_cozulmusmu(id))

    
        
    
def sorulari_getir():
    '''
    form ekranındaki soruları getirir.
    '''
    sorular = []
    index = 1
    while True:
        soru_key = f'soru_{index}'
        soru = request.form.get(soru_key)
        if not soru:
            break
        secenek_key =  f'secenekler_{index}[]'
        secenekler = request.form.getlist(secenek_key)
        
        sorular.append({
            'soru':soru,
            'secenekler':secenekler if secenekler else None
        })
        index += 1
    return sorular
        
        
def anket_cozulmusmu(anket_id):
    '''
    ilgili kullanicinin anketi çözüp çözmediğine bakar.
    '''
    with engine.begin() as conn:
        result = conn.execute(text(
            '''
            select tamamlandi_mi from tbl_kullanici_anketleri where kullanici_id = :kullanici_id and anket_id = :anket_id 
            '''
        ),{'kullanici_id':current_user.id, 'anket_id':anket_id}).fetchone()
    if result and int(result[0]) == 1:
        return True
    return False
    

@process.route('/submitAnketCevap',methods=['POST'])
def submit_anket():
    
    '''
    kullanıcının çözdüğü anketi veritabanına ekler.
    '''
    
    anket_id = request.form.get('anket-id')
    if not anket_id:
        logger.error('anket_id bulunamadı')
        return abort(404)        
    
    cevaplar = {}
    for key in request.form:
        if key.startswith('soru_'):
            cevaplar[key] = request.form.get(key)
    
    try:
        
        with engine.begin() as conn:
            for soru_key, cevap in cevaplar.items():
                soru_id = int(soru_key.replace('soru_', ''))
                
                if cevap.isdigit():  # Şıklı sorular için
                    conn.execute(text('''
                        INSERT INTO tbl_kullanici_cevaplari (kullanici_id, anket_id, soru_id, secenek_id, cevap_text)
                        VALUES (:kullanici_id, :anket_id, :soru_id, :secenek_id, NULL)
                    '''), {
                        'kullanici_id': current_user.id,
                        'anket_id': anket_id,
                        'soru_id': soru_id,
                        'secenek_id': int(cevap)
                    })
                    
                else:  # Açık uçlu sorular için
                    conn.execute(text('''
                        INSERT INTO tbl_kullanici_cevaplari (kullanici_id, anket_id, soru_id, secenek_id, cevap_text)
                        VALUES (:kullanici_id, :anket_id, :soru_id, NULL, :cevap_text)
                    '''), {
                        'kullanici_id': current_user.id,
                        'anket_id': anket_id,
                        'soru_id': soru_id,
                        'cevap_text': cevap
                    })
            conn.execute(text(''' insert into tbl_kullanici_anketleri (kullanici_id, anket_id, tamamlandi_mi)
                values (:kullanici_id, :anket_id , 1) '''),{'kullanici_id':current_user.id, 'anket_id':anket_id})
            logger.info('anket çözümü tamamlandı.')
            
        flash('Anket çözüldü')
        return redirect(url_for('account.get_dashboard'))
        
        
    except Exception as e:
        logger.error(e)
        
    



@process.route('/myAnkets')
def get_myAnkets():
    '''
        anketlerim butonuna basınca oluşturduğum anketleri getirir.
    '''
    with engine.begin() as conn:
        query = text('''
        SELECT 
            a.id,
            a.title,
            a.picture,
            a.description,
            a.is_private,
            pa.anket_link
        FROM tbl_anket a
        LEFT JOIN private_anket pa ON a.id = pa.anket_id
        where a.kullanici_id= :kullanici_id;
        ''')
        result = conn.execute(query,{'kullanici_id':current_user.id}).fetchall()
        
    return render_template('anketlerim.html',anketlerim=result)


@process.route('/myAnkets/remove',methods=['POST'])
@login_required
def remove_myanket():
    id = int(request.form.get('myanket_id'))
    with engine.begin() as conn:
        result = conn.execute(text('delete from tbl_anket where kullanici_id = :kullanici_id and id = :id'),
        {'kullanici_id':current_user.id, 'id':id})
    if result.rowcount != 0:
        flash('Başarı ile silindi')
        return redirect(url_for('process.get_myAnkets'))