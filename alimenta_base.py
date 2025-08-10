# 'requests' para fazer requisições HTTP e obter o conteúdo HTML das páginas web.
import requests

# 'BeautifulSoup' para analisar (fazer o "parse") do conteúdo HTML e extrair dados de forma fácil.
from bs4 import BeautifulSoup

# 'urljoin' para construir URLs completas a partir de caminhos relativos (essencial para a paginação).
from urllib.parse import urljoin

# Componentes do SQLAlchemy, um ORM (Object-Relational Mapper) para interagir com o banco de dados usando objetos Python.
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base



SQLALCHEMY_DATABASE_URI = 'sqlite:///base.db'

# Cria uma classe Base declarativa da qual nossos modelos de tabela herdarão.
Base = declarative_base()

# Definição do modelo ORM para a tabela 'livros'.
class Livros(Base):
    # Nome da tabela no banco de dados.
    __tablename__ = 'livros'

    # Definição das colunas da tabela (seguindo a convenção 'snake_case').
    id = Column(Integer, primary_key=True)
    titulo = Column(String, unique=True)
    preco = Column(String)
    avaliacao = Column(String)
    disponibilidade = Column(String)
    categoria = Column(String)
    imagem = Column(String)

# Definição do modelo ORM para a tabela 'usuario'.
class Usuario(Base):
    # CORREÇÃO: Adicionando o nome da tabela.
    __tablename__ = 'usuario'

    # MELHORIA: Padronizando o nome da coluna da chave primária para 'id'.
    id = Column(Integer, primary_key=True)
    # MELHORIA: Usando 'snake_case' para os nomes das colunas.
    nome_usuario = Column(String(80), unique=True, nullable=False)
    senha = Column(String(120), nullable=False)


# Cria a "engine" (motor) que gerencia a conexão com o banco de dados.
engine = create_engine(SQLALCHEMY_DATABASE_URI)

# Cria TODAS as tabelas ('livros' e 'usuario') no banco de dados, caso ainda não existam.
Base.metadata.create_all(engine)

# Cria uma fábrica de sessões ('Session') que será usada para criar objetos de sessão individuais.
Session = sessionmaker(bind=engine)

# Cria uma instância de sessão, que é a nossa "ponte" para interagir com o banco de dados.
session = Session()

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

     
            
           # Verifica se um livro com o mesmo título já existe no banco de dados.
            # .first() retorna o objeto se encontrado, ou None caso contrário.
            existe = session.query(Livros).filter_by(titulo=titulo).first()
            
            # Se o livro não existir no banco de dados...
            if not existe:
                print(f"Salvando livro novo: {titulo}")
                # Cria uma nova instância do objeto 'Livros' com os dados extraídos.
                novo_livro = Livros(
                    titulo=titulo,
                    preco=preco,
                    avaliacao=avaliacao,
                    disponibilidade=estoque,
                    categoria=categoria_nome,
                    imagem=imagem
                )
                # Adiciona o novo objeto à sessão.
                session.add(novo_livro)
                # Comita (salva) a transação no banco de dados.
                session.commit()
            else:
                # Se o livro já existir, apenas informa no console.
                print(f"Livro já existente no banco de dados: {titulo}")


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