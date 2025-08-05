from operator import or_
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# Inicialização da aplicação
app = Flask(__name__)

app.config.from_object('config')

# Inicialização de extensões
db = SQLAlchemy(app)
jwt = JWTManager(app)


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
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            Nome_usuario:
              type: string
              example: usuario1
            Senha:
              type: string
              example: senha123
    responses:
      201:
        description: Usuário criado com sucesso
      400:
        description: Usuário já existe
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
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            Nome_usuario:
              type: string
              example: usuario1
            Senha:
              type: string
              example: senha123
    responses:
      201:
        description: Token criado com sucesso
      400:
        description: Usuário ou senha inválidos
    """
    data = request.get_json()
    user = Usuario.query.filter_by(Nome_usuario=data["Nome_usuario"]).first()

    if user and user.Senha == data["Senha"]:
        token = create_access_token(identity=str(user.Id))
        return jsonify({"token": token}), 201

    return jsonify({"Erro": "Usuário ou senha inválidos"}), 400


@app.route("/api/v1/books", methods=["GET"])
def busca_livros():
    """
    Gera um token JWT para autenticação.
    ---
    tags:
      - Usuários
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            Nome_usuario:
              type: string
              example: usuario1
            Senha:
              type: string
              example: senha123
    responses:
      201:
        description: Token criado com sucesso
      400:
        description: Usuário ou senha inválidos
    """
    #id_livro = request.args.get('id')
    consulta = Livros.query

    #if id_livro:
    #    consulta = consulta.filter(Livros.Id == id_livro)
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
def busca_livro_id(id_livro):
    """
    Gera um token JWT para autenticação.
    ---
    tags:
      - Usuários
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            Nome_usuario:
              type: string
              example: usuario1
            Senha:
              type: string
              example: senha123
    responses:
      201:
        description: Token criado com sucesso
      400:
        description: Usuário ou senha inválidos
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
def busca_livro_categoria():
    """
    Gera um token JWT para autenticação.
    ---
    tags:
      - Usuários
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            Nome_usuario:
              type: string
              example: usuario1
            Senha:
              type: string
              example: senha123
    responses:
      201:
        description: Token criado com sucesso
      400:
        description: Usuário ou senha inválidos
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
def busca_categorias():
    """
    Gera um token JWT para autenticação.
    ---
    tags:
      - Usuários
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            Nome_usuario:
              type: string
              example: usuario1
            Senha:
              type: string
              example: senha123
    responses:
      201:
        description: Token criado com sucesso
      400:
        description: Usuário ou senha inválidos
    """
    #id_livro = request.args.get('id')
    categorias = db.session.query(Livros.Categoria).distinct().all()
    categorias_lista = [c[0] for c in categorias]
    return jsonify(categorias_lista)
# ROTAS

# INICIAR APP
if __name__ == "__main__":
  app.run()