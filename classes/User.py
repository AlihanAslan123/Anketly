from flask_login import UserMixin


class User(UserMixin):
    '''
        tbl_user tablosunu temsil eden User sınıfı
    '''
    def __init__(self, id, email):
        self.id = id
        self.email = email