import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# Configuração da URL do banco (pode trocar para PostgreSQL, MySQL etc.)
SQLALCHEMY_DATABASE_URI = 'sqlite:///livros.db'

# Setup do SQLAlchemy
Base = declarative_base()

class Livros(Base):
    __tablename__ = 'livros'

    id = Column(Integer, primary_key=True)
    Titulo = Column(String, unique=True)  # Evita duplicatas
    Preco = Column(String)
    Avaliacao = Column(String)
    Disponibilidade = Column(String)
    Categoria = Column(String)
    Imagem = Column(String)

# Criação do banco e da sessão
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# URL inicial
url = "https://books.toscrape.com/"
response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, "html.parser")

# Coleta categorias
categories = soup.select('div.side_categories ul.nav-list ul li a')

for cat in categories:
    url_categoria = url + cat['href']

    while True:
        response = requests.get(url_categoria)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        categoria_nome = soup.find('h1').text.strip()

        livros = soup.find_all('article', class_="product_pod")
        for livro in livros:
            titulo = livro.find('h3').text.strip()
            imagem = livro.find('img')['src']
            preco = livro.find('p', class_='price_color').text.strip()
            estoque = livro.select_one('p.instock.availability').get_text(strip=True)
            estrelas_tag = livro.find('p', class_='star-rating')
            classes = estrelas_tag.get("class", [])
            avaliacao = [c for c in classes if c != "star-rating"][0]

            print(f"Categoria: {categoria_nome}")
            print(f"Titulo: {titulo}")
            print(f"Imagem: {imagem}")
            print(f"Preco: {preco}")
            print(f"Estoque: {estoque}")
            print(f"Avaliacao: {avaliacao}")

            # Verifica se o livro já existe
            existe = session.query(Livros).filter_by(Titulo=titulo).first()
            if not existe:
                novo_livro = Livros(
                    Titulo=titulo,
                    Preco=preco,
                    Avaliacao=avaliacao,
                    Disponibilidade=estoque,
                    Categoria=categoria_nome,
                    Imagem=imagem
                )
                session.add(novo_livro)
                session.commit()
            else:
                print(f"Livro já existente: {titulo}")

        # Verifica se há próxima página
        next_button = soup.select_one('li.next > a')
        if next_button:
            url_categoria = urljoin(url_categoria, next_button['href'])
        else:
            break
