from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Colecionador(db.Model):
    __tablename__ = 'colecionador'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    cep = db.Column(db.String(9))
    cpf = db.Column(db.String(14))
    data_nascimento = db.Column(db.Date)
    idade = db.Column(db.Integer)
    senha_hash = db.Column(db.Text)
    tipo = db.Column(db.String(20), default='comum')

    figures = db.relationship('Figure', backref='colecionador')

    @staticmethod
    def calcular_idade(data_nascimento):
        hoje = date.today()
        return hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))

    def to_dict_completo(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'cep': self.cep,
            'cpf': self.cpf,
            'data_nascimento': self.data_nascimento.strftime('%Y-%m-%d') if self.data_nascimento else None,
            'idade': self.idade,
            'tipo': self.tipo
        }

    def to_dict_publico(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'idade': self.idade
        }

class Obra(db.Model):
    __tablename__ = 'obra'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)

    figures = db.relationship('Figure', back_populates='obra', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Obra {self.nome}>'

class Figure(db.Model):
    __tablename__ = 'figures'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    imagem_url = db.Column(db.String(255))
    estoque = db.Column(db.Integer, nullable=False)

    colecionador_id = db.Column(db.Integer, db.ForeignKey('colecionador.id'), nullable=False)
    obra_id = db.Column(db.Integer, db.ForeignKey('obra.id'), nullable=True)

    obra = db.relationship('Obra', back_populates='figures')
    colecao_items = db.relationship('Colecao', back_populates='figure', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Figure {self.nome}>'

class Colecao(db.Model):
    __tablename__ = 'colecao'

    id = db.Column(db.Integer, primary_key=True)
    figure_id = db.Column(db.Integer, db.ForeignKey('figures.id'), nullable=False)

    figure = db.relationship('Figure', back_populates='colecao_items')

    def __repr__(self):
        return f'<Colecao figure_id={self.figure_id}>'
