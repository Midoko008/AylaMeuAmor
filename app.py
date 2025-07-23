from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Colecionador, Figure, Colecao, Obra
from datetime import datetime
import bcrypt

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://AylaUwU:StrongPassWord!@localhost/AylaActions'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def get_colecionador_logado():
    auth = request.headers.get('Authorization')
    if not auth:
        return None
    try:
        token_type, user_id = auth.split()
        if token_type.lower() != 'bearer':
            return None
        user_id_int = int(user_id)
        return Colecionador.query.get(user_id_int)
    except Exception:
        return None

# --- Rotas Colecionador ---

@app.route('/cadastro', methods=['POST'])
def cadastrar_colecionador():
    dados = request.json
    try:
        nascimento = datetime.strptime(dados['data_nascimento'], '%Y-%m-%d').date()
    except (ValueError, KeyError):
        return jsonify({'erro': 'Data de nascimento inválida ou não informada'}), 400

    idade = Colecionador.calcular_idade(nascimento)
    senha = dados.get('senha', '')
    if not senha:
        return jsonify({'erro': 'Senha não informada'}), 400

    senha_bytes = senha.encode('utf-8')
    senha_criptografada = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())

    novo_colecionador = Colecionador(
        nome=dados.get('nome'),
        email=dados.get('email'),
        cep=dados.get('cep'),
        cpf=dados.get('cpf'),
        data_nascimento=nascimento,
        idade=idade,
        senha_hash=senha_criptografada.decode('utf-8'),
        tipo='comum'
    )

    try:
        db.session.add(novo_colecionador)
        db.session.commit()
        return jsonify({'mensagem': 'Colecionador cadastrado com sucesso!'}), 201
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao cadastrar colecionador'}), 500

@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    colecionador = Colecionador.query.filter_by(email=dados.get('email')).first()

    if colecionador and bcrypt.checkpw(dados.get('senha', '').encode(), colecionador.senha_hash.encode()):
        return jsonify({
            'mensagem': 'Login bem-sucedido',
            'usuario': {
                'id': colecionador.id,
                'nome': colecionador.nome,
                'email': colecionador.email,
                'cep': colecionador.cep,
                'cpf': colecionador.cpf,
                'data_nascimento': colecionador.data_nascimento.strftime('%Y-%m-%d'),
                'idade': colecionador.idade,
                'tipo': colecionador.tipo
            }
        }), 200

    return jsonify({'erro': 'E-mail ou senha inválidos'}), 401

@app.route('/usuarios/<int:id>', methods=['GET'])
def obter_colecionador(id):
    colecionador = Colecionador.query.get_or_404(id)
    logado = get_colecionador_logado()
    if not logado:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    if logado.id == colecionador.id or logado.tipo == 'admin':
        return jsonify(colecionador.to_dict_completo())
    else:
        return jsonify(colecionador.to_dict_publico())

@app.route('/usuarios/me', methods=['GET'])
def obter_meu_perfil():
    logado = get_colecionador_logado()
    if not logado:
        return jsonify({'erro': 'Usuário não autenticado'}), 401
    return jsonify(logado.to_dict_completo())

@app.route('/usuarios/<int:id>', methods=['PUT'])
def atualizar_colecionador(id):
    logado = get_colecionador_logado()
    if not logado:
        return jsonify({'erro': 'Usuário não autenticado'}), 401
    if logado.id != id and logado.tipo != 'admin':
        return jsonify({'erro': 'Acesso negado'}), 403

    dados = request.json
    colecionador = Colecionador.query.get_or_404(id)
    if 'nome' in dados:
        colecionador.nome = dados['nome']
    if 'email' in dados:
        colecionador.email = dados['email']

    try:
        db.session.commit()
        return jsonify({'mensagem': 'Dados atualizados com sucesso'})
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao atualizar dados'}), 500

# --- Rotas Obra ---

@app.route('/obras', methods=['GET'])
def listar_obras():
    obras = Obra.query.all()
    return jsonify([{'id': o.id, 'nome': o.nome} for o in obras])

@app.route('/obras', methods=['POST'])
def criar_obra():
    dados = request.json
    nome = dados.get('nome')
    if not nome:
        return jsonify({'erro': 'Nome da obra é obrigatório'}), 400

    existente = Obra.query.filter_by(nome=nome).first()
    if existente:
        return jsonify({'erro': 'Obra já existe'}), 400

    nova_obra = Obra(nome=nome)
    try:
        db.session.add(nova_obra)
        db.session.commit()
        return jsonify({'mensagem': 'Obra criada', 'id': nova_obra.id}), 201
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao criar obra'}), 500

# --- Rotas Figures ---

@app.route('/figuras', methods=['GET'])
def listar_figures():
    figures = Figure.query.all()
    lista = []
    for f in figures:
        lista.append({
            'id': f.id,
            'nome': f.nome,
            'preco': f.preco,
            'imagem_url': f.imagem_url,
            'estoque': f.estoque,
            'categoria': {
                'id': f.obra.id if f.obra else None,
                'nome': f.obra.nome if f.obra else None
            }
        })
    return jsonify(lista)

@app.route('/figuras/<int:id>', methods=['GET'])
def obter_figure(id):
    f = Figure.query.get(id)
    if not f:
        return jsonify({'erro': 'Figure não encontrada'}), 404
    return jsonify({
        'id': f.id,
        'nome': f.nome,
        'preco': f.preco,
        'imagem_url': f.imagem_url,
        'estoque': f.estoque,
        'categoria': {
            'id': f.obra.id if f.obra else None,
            'nome': f.obra.nome if f.obra else None
        },
        'usuario': {
            'id': f.colecionador.id,
            'nome': f.colecionador.nome
        }
    })

@app.route('/figuras', methods=['POST'])
def criar_figure():
    logado = get_colecionador_logado()
    if not logado:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    dados = request.json
    nome = dados.get('nome')
    preco = dados.get('preco')
    imagem_url = dados.get('imagem_url')
    estoque = dados.get('estoque')
    obra_id = dados.get('categoria_id')

    if not nome or preco is None or not imagem_url or estoque is None or not obra_id:
        return jsonify({'erro': 'Dados incompletos'}), 400

    try:
        preco = float(preco)
        estoque = int(estoque)
        obra_id = int(obra_id)
        if estoque <= 0:
            return jsonify({'erro': 'Estoque deve ser maior que zero'}), 400
    except (ValueError, TypeError):
        return jsonify({'erro': 'Preço, estoque ou obra inválidos'}), 400

    obra = Obra.query.get(obra_id)
    if not obra:
        return jsonify({'erro': 'Obra não encontrada'}), 404

    nova_figure = Figure(
        nome=nome,
        preco=preco,
        imagem_url=imagem_url,
        estoque=estoque,
        obra_id=obra_id,
        colecionador_id=logado.id
    )

    try:
        db.session.add(nova_figure)
        db.session.commit()
        return jsonify({'mensagem': 'Figure criada com sucesso!'}), 201
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao salvar figure'}), 500

@app.route('/figuras/<int:id>', methods=['DELETE'])
def deletar_figure(id):
    logado = get_colecionador_logado()
    if not logado:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    figure = Figure.query.get(id)
    if not figure:
        return jsonify({'erro': 'Figure não encontrada'}), 404

    if logado.id != figure.colecionador_id and logado.tipo != 'admin':
        return jsonify({'erro': 'Acesso negado'}), 403

    try:
        Colecao.query.filter_by(figure_id=id).delete()
        db.session.delete(figure)
        db.session.commit()
        return jsonify({'mensagem': 'Figure deletada com sucesso'}), 200
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao deletar figure'}), 500

# --- Colecao (Carrinho) ---

@app.route('/carrinho', methods=['POST'])
def adicionar_ao_carrinho():
    dados = request.json
    figure_id = dados.get('produto_id')  # ou 'figure_id', se preferir
    figure = db.session.get(Figure, figure_id)

    if not figure:
        return jsonify({'erro': 'Figure não encontrada'}), 404
    if figure.estoque <= 0:
        return jsonify({'erro': 'Sem estoque'}), 400

    try:
        novo_item = Colecao(figure_id=figure.id)
        figure.estoque -= 1
        db.session.add(novo_item)
        db.session.commit()
        return jsonify({'mensagem': 'Adicionada ao carrinho!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao adicionar ao carrinho', 'detalhe': str(e)}), 500



@app.route('/carrinho', methods=['GET'])
def listar_colecao():
    itens = Colecao.query.all()
    figures = []
    valor_total = 0.0

    for item in itens:
        f = Figure.query.get(item.figure_id)
        if f:
            valor_total += f.preco
            figures.append({
                'id': f.id,
                'nome': f.nome,
                'preco': f.preco,
                'imagem_url': f.imagem_url,
                'estoque': f.estoque,
                'categoria': {
                    'id': f.obra.id if f.obra else None,
                    'nome': f.obra.nome if f.obra else None
                }
            })

    return jsonify({'produtos': figures, 'valor_total': f"{valor_total:.2f}"})

@app.route('/carrinho/<int:produto_id>', methods=['DELETE'])
def remover_da_colecao(produto_id):
    item = Colecao.query.filter_by(figure_id=produto_id).first()
    if not item:
        return jsonify({'erro': 'Figure não está na coleção'}), 404

    try:
        figure = Figure.query.get(produto_id)
        if figure:
            figure.estoque += 1
        db.session.delete(item)
        db.session.commit()
        return jsonify({'mensagem': 'Figure removida da coleção!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao remover da coleção', 'detalhe': str(e)}), 500

@app.route('/produtos/usuario/<int:usuario_id>', methods=['GET'])
def figures_por_colecionador(usuario_id):
    figures = Figure.query.filter_by(colecionador_id=usuario_id).all()
    lista = []
    for f in figures:
        lista.append({
            'id': f.id,
            'nome': f.nome,
            'preco': f.preco,
            'imagem_url': f.imagem_url,
            'estoque': f.estoque,
            'categoria': {
                'id': f.obra.id if f.obra else None,
                'nome': f.obra.nome if f.obra else None
            }
        })
    return jsonify(lista)

@app.route('/figuras/obras/<int:obra_id>', methods=['GET'])
def figures_por_obra(obra_id):
    figures = Figure.query.filter_by(obra_id=obra_id).all()
    lista = []
    for f in figures:
        lista.append({
            'id': f.id,
            'nome': f.nome,
            'preco': f.preco,
            'imagem_url': f.imagem_url,
            'estoque': f.estoque,
            'categoria': {
                'id': f.obra.id if f.obra else None,
                'nome': f.obra.nome if f.obra else None
            }
        })
    return jsonify(lista)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
