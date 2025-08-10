# -*- coding: utf-8 -*-

# =============================================================================
# Importação das bibliotecas necessárias
# =============================================================================

# 'requests' para fazer requisições HTTP e obter o conteúdo HTML das páginas web.
import requests

# 'BeautifulSoup' para analisar (fazer o "parse") do conteúdo HTML e extrair dados de forma fácil.
from bs4 import BeautifulSoup

# 'urljoin' para construir URLs completas a partir de caminhos relativos (essencial para a paginação).
from urllib.parse import urljoin

# Componentes do SQLAlchemy, um ORM (Object-Relational Mapper) para interagir com o banco de dados usando objetos Python.
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# =============================================================================
# Configuração do Banco de Dados com SQLAlchemy
# =============================================================================

# Define a string de conexão para o banco de dados.
# 'sqlite:///livros.db' cria um arquivo de banco de dados SQLite chamado 'livros.db' no mesmo diretório do script.
SQLALCHEMY_DATABASE_URI = 'sqlite:///livros.db'

# Cria uma classe Base declarativa da qual nossos modelos de tabela herdarão.
Base = declarative_base()

# Definição do modelo ORM para a tabela 'livros'.
# Esta classe mapeia os objetos Python para as linhas da tabela no banco de dados.
class Livros(Base):
    # Nome da tabela no banco de dados.
    __tablename__ = 'livros'

    # Definição das colunas da tabela.
    id = Column(Integer, primary_key=True)  # Chave primária autoincrementável.
    Titulo = Column(String, unique=True)    # Coluna para o título, com restrição de valor único para evitar duplicatas.
    Preco = Column(String)                  # Coluna para o preço.
    Avaliacao = Column(String)              # Coluna para a avaliação (ex: "One", "Two", etc.).
    Disponibilidade = Column(String)        # Coluna para o status do estoque.
    Categoria = Column(String)              # Coluna para a categoria do livro.
    Imagem = Column(String)                 # Coluna para a URL da imagem de capa.

# Cria a "engine" (motor) que gerencia a conexão com o banco de dados.
engine = create_engine(SQLALCHEMY_DATABASE_URI)

# Cria a tabela 'livros' no banco de dados, caso ela ainda não exista.
Base.metadata.create_all(engine)

# Cria uma fábrica de sessões ('Session') que será usada para criar objetos de sessão individuais.
Session = sessionmaker(bind=engine)

# Cria uma instância de sessão, que é a nossa "ponte" para interagir com o banco de dados.
session = Session()

# =============================================================================
# Início do processo de Web Scraping
# =============================================================================

# URL da página inicial do site a ser "raspado".
url = "https://books.toscrape.com/"

print("Iniciando o scraping do site 'books.toscrape.com'...")

# Faz uma requisição GET para a URL inicial.
response = requests.get(url)

# Obtém o conteúdo HTML da resposta.
html = response.text

# Cria um objeto BeautifulSoup para analisar o HTML.
soup = BeautifulSoup(html, "html.parser")

# Seleciona todos os links de categorias na barra lateral usando um seletor CSS.
categories = soup.select('div.side_categories ul.nav-list ul li a')
print(f"Encontradas {len(categories)} categorias.")

# Itera sobre cada tag de link (<a>) encontrada para as categorias.
for cat in categories:
    # Constrói a URL completa para a página da categoria.
    url_categoria = url + cat['href']

    # Loop 'while True' para lidar com a paginação dentro de cada categoria.
    # O loop continuará até que não haja mais um botão "próxima página".
    while True:
        print(f"Acessando a URL da categoria: {url_categoria}")
        response = requests.get(url_categoria)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # Extrai o nome da categoria do cabeçalho <h1> da página.
        categoria_nome = soup.find('h1').text.strip()

        # Encontra todos os contêineres de livros na página atual.
        livros = soup.find_all('article', class_="product_pod")
        print(f"Encontrados {len(livros)} livros na categoria '{categoria_nome}'...")

        # Itera sobre cada livro encontrado na página.
        for livro in livros:
            # Extrai o título do livro.
            titulo = livro.find('h3').text.strip()
            
            # Extrai a URL relativa da imagem e a torna completa (embora já seja relativa à raiz, o site a resolve).
            imagem = livro.find('img')['src']
            
            # Extrai o preço do livro.
            preco = livro.find('p', class_='price_color').text.strip()
            
            # Extrai o status de disponibilidade em estoque.
            estoque = livro.select_one('p.instock.availability').get_text(strip=True)
            
            # Extrai a avaliação em estrelas.
            estrelas_tag = livro.find('p', class_='star-rating')
            classes = estrelas_tag.get("class", [])  # Pega a lista de classes, ex: ["star-rating", "Three"]
            avaliacao = [c for c in classes if c != "star-rating"][0] # Remove "star-rating" e pega a classe de avaliação.

            # === Bloco de impressão no console (para feedback visual) ===
            # print(f"Categoria: {categoria_nome}")
            # print(f"Titulo: {titulo}")
            # print(f"Imagem: {imagem}")
            # print(f"Preco: {preco}")
            # print(f"Estoque: {estoque}")
            # print(f"Avaliacao: {avaliacao}")
            
            # =================================================================
            # Persistência de Dados no Banco
            # =================================================================

            # Verifica se um livro com o mesmo título já existe no banco de dados.
            # .first() retorna o objeto se encontrado, ou None caso contrário.
            existe = session.query(Livros).filter_by(Titulo=titulo).first()
            
            # Se o livro não existir no banco de dados...
            if not existe:
                print(f"Salvando livro novo: {titulo}")
                # Cria uma nova instância do objeto 'Livros' com os dados extraídos.
                novo_livro = Livros(
                    Titulo=titulo,
                    Preco=preco,
                    Avaliacao=avaliacao,
                    Disponibilidade=estoque,
                    Categoria=categoria_nome,
                    Imagem=imagem
                )
                # Adiciona o novo objeto à sessão.
                session.add(novo_livro)
                # Comita (salva) a transação no banco de dados.
                session.commit()
            else:
                # Se o livro já existir, apenas informa no console.
                print(f"Livro já existente no banco de dados: {titulo}")

        # =================================================================
        # Lógica de Paginação
        # =================================================================
        
        # Procura pelo link do botão "next" (próxima página).
        next_button = soup.select_one('li.next > a')
        
        # Se um botão "next" for encontrado...
        if next_button:
            # Pega o link relativo (ex: 'page-2.html') do botão.
            next_page_url_relativa = next_button['href']
            # Usa urljoin para construir a URL completa da próxima página de forma segura.
            url_categoria = urljoin(url_categoria, next_page_url_relativa)
        else:
            # Se não houver botão "next", significa que estamos na última página da categoria.
            # O 'break' encerra o loop 'while' e o script passa para a próxima categoria.
            print(f"Fim da categoria '{categoria_nome}'. Passando para a próxima.")
            break

print("\nProcesso de scraping concluído com sucesso!")
print("Os dados foram salvos no arquivo 'livros.db'.")

# Fecha a sessão com o banco de dados.
session.close()