from operator import or_
from pydoc import text
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from flasgger import Swagger


# Inicialização da aplicação
app = Flask(__name__)

app.config.from_object('config')

# Inicialização de extensões
db = SQLAlchemy(app)
jwt = JWTManager(app)
swagger = Swagger(app)

from flask import current_app

class Livros(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Titulo = db.Column(db.String , nullable=False)
    Preco = db.Column(db.String , nullable=False)
    Avaliacao = db.Column(db.String , nullable=False)
    Disponibilidade = db.Column(db.String , nullable=False)
    Categoria = db.Column(db.String , nullable=False)
    Imagem = db.Column(db.String , nullable=False)

class Usuario(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Nome_usuario = db.Column(db.String(80), unique=True, nullable=False)
    Senha = db.Column(db.String(120), nullable=False)


@app.route("/registro", methods=["POST"])
def registro_usuario():
    """
Registro de um novo usuário.
---
tags:
  - Usuários
security:
  - Bearer: []
summary: Cria um novo usuário no sistema
description: >
  Endpoint para registrar um novo usuário.  
  É necessário informar um nome de usuário único e uma senha.  
  Retorna 201 se o usuário for criado com sucesso.
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - Nome_usuario
        - Senha
      properties:
        Nome_usuario:
          type: string
          description: Nome de login único para o usuário.
          example: usuario1
        Senha:
          type: string
          description: Senha de acesso (mínimo 6 caracteres).
          example: senha123
responses:
  201:
    description: Usuário criado com sucesso
    schema:
      type: object
      properties:
        id:
          type: integer
          example: 42
        Nome_usuario:
          type: string
          example: usuario1
  400:
    description: Nome de usuário já existe
    schema:
      type: object
      properties:
        erro:
          type: string
          example: Usuário já existe
"""

    data = request.get_json()
    if Usuario.query.filter_by(Nome_usuario=data["Nome_usuario"]).first():
        return jsonify({"Erro": "Usuário já existe"}), 400

    novo_usuario = Usuario(Nome_usuario=data["Nome_usuario"], Senha=data["Senha"])
    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({"Sucesso": "Usuário criado com sucesso"}), 201

@app.route("/login", methods=["POST"])
def login():
    """
Gera um token JWT para autenticação.
---
tags:
  - Usuários
summary: Gera um token de autenticação JWT
description: >
  Endpoint para autenticação de usuários.  
  Recebe nome de usuário e senha válidos e retorna um token JWT para uso nas requisições autenticadas.  
  Retorna 400 se as credenciais forem inválidas.
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - Nome_usuario
        - Senha
      properties:
        Nome_usuario:
          type: string
          description: Nome de login do usuário.
          example: usuario1
        Senha:
          type: string
          description: Senha de acesso.
          example: senha123
responses:
  201:
    description: Token criado com sucesso
    schema:
      type: object
      properties:
        access_token:
          type: string
          example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        expires_in:
          type: integer
          example: 3600
  400:
    description: Usuário ou senha inválidos
    schema:
      type: object
      properties:
        erro:
          type: string
          example: Usuário ou senha inválidos
"""

    data = request.get_json()
    user = Usuario.query.filter_by(Nome_usuario=data["Nome_usuario"]).first()

    if user and user.Senha == data["Senha"]:
        token = create_access_token(identity=str(user.Id))
        return jsonify({"token": token}), 201

    return jsonify({"Erro": "Usuário ou senha inválidos"}), 400


@app.route("/api/v1/books", methods=["GET"])
@jwt_required()
def busca_livros():

    """
    Retorna todos os livros do catálogo.
    ---
    tags:
      - Livros
    security:
    - Bearer: []
    summary: Retorna todos os livros disponíveis no catálogo
    description: >
      Endpoint que retorna a lista completa de livros do catálogo.  
      Não requer parâmetros.
    responses:
      200:
        description: Lista de livros retornada com sucesso
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              titulo:
                type: string
                example: "It's Only the Himalayas"
              preco:
                type: string
                example: "£45.17"
              Avaliacao:
                type: string
                example: "Two"
              Categoria:
                type: string
                example: "Travel"
              Disponibilidade:
                type: string
                example: "In stock"
              Imagem:
                type: string
                format: uri
                example: "../../../../media/cache/27/a5/27a53d0bb95bdd88288eaf66c9230d7e.jpg"
    """
 
    consulta = Livros.query  
    livros = consulta.all()

    return jsonify(
        [
            {
                "id": l.Id,
                "titulo": l.Titulo,
                "Categoria": l.Categoria,
                "preco": l.Preco,
                "Avaliacao": l.Avaliacao,
                "Disponibilidade": l.Disponibilidade,
                "Imagem": l.Imagem
            }
            for l in  livros
        ]
    )

@app.route("/api/v1/books/<int:id_livro>", methods=["GET"])
@jwt_required()
def busca_livro_id(id_livro):
    """
    Retorna o livro do catálogo com base no ID.
    ---
    tags:
      - Livros
    security:
      - Bearer: []
    summary: Retorna um livro pelo seu ID
    description: >
      Busca um livro no catálogo pelo ID fornecido.  
      Retorna os detalhes do livro se encontrado.  
      Caso contrário, retorna erro 404.
    parameters:
      - name: id_livro
        in: path
        type: integer
        required: true
        description: ID do livro a ser buscado
        example: 1
    responses:
      200:
        description: Livro encontrado com sucesso
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            titulo:
              type: string
              example: "It's Only the Himalayas"
            Categoria:
              type: string
              example: "Travel"
            preco:
              type: string
              example: "£45.17"
            Avaliacao:
              type: string
              example: "Two"
            Disponibilidade:
              type: string
              example: "In stock"
            Imagem:
              type: string
              format: uri
              example: "../../../../media/cache/27/a5/27a53d0bb95bdd88288eaf66c9230d7e.jpg"
      404:
        description: Livro não encontrado
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Livro não encontrado
    """

    livro = Livros.query.get_or_404(id_livro)
    return jsonify({
        "id": livro.Id,
        "titulo": livro.Titulo,
        "Categoria": livro.Categoria,
        "preco": livro.Preco,
        "Avaliacao": livro.Avaliacao,
        "Disponibilidade": livro.Disponibilidade,
        "Imagem": livro.Imagem
    })


@app.route("/api/v1/books/search", methods=["GET"])
@jwt_required()
def busca_livro_categoria():
    """
    Retorna os livros de acordo com o título ou categoria.
    ---
    tags:
      - Livros
    security:
      - Bearer: []
    summary: Busca livros filtrando por título ou categoria
    description: >
      Retorna uma lista de livros que correspondem ao filtro informado via query string.  
      Os parâmetros são opcionais e podem ser usados juntos ou separadamente.
    parameters:
      - name: categoria
        in: query
        type: string
        required: false
        description: Categoria para filtrar os livros
        example: Travel
      - name: titulo
        in: query
        type: string
        required: false
        description: Título para filtrar os livros
        example: Himalayas
    responses:
      200:
        description: Lista de livros filtrada retornada com sucesso
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              titulo:
                type: string
                example: "It's Only the Himalayas"
              Categoria:
                type: string
                example: "Travel"
              preco:
                type: string
                example: "£45.17"
              Avaliacao:
                type: string
                example: "Two"
              Disponibilidade:
                type: string
                example: "In stock"
              Imagem:
                type: string
                format: uri
                example: "../../../../media/cache/27/a5/27a53d0bb95bdd88288eaf66c9230d7e.jpg"
    """
    categoria = request.args.get("categoria")
    titulo = request.args.get("titulo")

    query = Livros.query

    if categoria and titulo:
        query = query.filter(
            or_(
                Livros.Categoria.ilike(f"%{categoria}%"),
                Livros.Titulo.ilike(f"%{titulo}%")
            )
        )
    elif categoria:
        query = query.filter(Livros.Categoria.ilike(f"%{categoria}%"))
    elif titulo:
        query = query.filter(Livros.Titulo.ilike(f"%{titulo}%"))

    livros = query.all()

    return jsonify([
        {
            "id": l.Id,
            "titulo": l.Titulo,
            "Categoria": l.Categoria,
            "preco": l.Preco,
            "Avaliacao": l.Avaliacao,
            "Disponibilidade": l.Disponibilidade,
            "Imagem": l.Imagem
        }
        for l in livros
    ])

@app.route("/api/v1/categories", methods=["GET"])
@jwt_required()
def busca_categorias():
    """
    Retorna as categorias de livros disponíveis na base.
    ---
    tags:
      - Livros
    security:
    - Bearer: []
    summary: Retorna todas as categorias de livros distintas
    description: >
      Endpoint que retorna uma lista das categorias distintas disponíveis no catálogo de livros.  
      Não requer parâmetros.
    responses:
      200:
        description: Lista de categorias retornada com sucesso
        schema:
          type: array
          items:
            type: string
            example: Travel
    """
    #id_livro = request.args.get('id')
    categorias = db.session.query(Livros.Categoria).distinct().all()
    categorias_lista = [c[0] for c in categorias]
    return jsonify(categorias_lista)



@app.route('/health', methods=['GET'])
def check_servico():
    """
Verifica a saúde da aplicação.
---
tags:
  - Health
summary: Retorna o status da aplicação de API e conectividade com os dados.
description: >
  Endpoint que retorna uma mensagem para verificar se está tudo ok com o serviço de API (Flask) e conexão com os dados.  
  Não requer parâmetros.
responses:
  200:
    description: Tudo ok, a aplicação está funcionando e conexão com os dados ok.
    content:
      application/json:
        schema:
          type: object
          properties:
            Servidor de api:
              type: string
              example: "API: Tudo ok por aqui;"
            Banco de dados:
              type: string
              example: "Banco: Tudo ok por aqui."
  503:
    description: Problema, algum dos serviços não está funcionando.
    content:
      application/json:
        schema:
          type: object
          properties:
            Servidor de api:
              type: string
              example: "API: Tudo ok por aqui;"
            Banco de dados:
              type: string
              example: "Banco: Problema na conexão."
"""

    flask_status = 'API: Tudo ok por aqui;'
    banco_status = 'Banco: Tudo ok por aqui.'

    try:
        Livros.query.get_or_404(1)
        banco_ok = True
    except Exception:
        banco_ok = False

    resposta_final = {
        'Servidor de api': flask_status,
        'Banco de dados': banco_status if banco_ok else 'Banco: Problema na conexão.'
    }

    if banco_ok:
        return jsonify(resposta_final), 200
    else:
        return jsonify(resposta_final), 503
      

# ROTAS

# CRIAR BANCO
with app.app_context():
    db.create_all()
    print("Banco de dados criado com sucesso.")
    
# INICIAR APP
if __name__ == "__main__":
  app.run()