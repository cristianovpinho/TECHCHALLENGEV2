import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config import SQLALCHEMY_DATABASE_URI


url = "https://books.toscrape.com/"
response = requests.get(url)
html = response.text
soup = BeautifulSoup(html , "html.parser")

with app.app_context():
  categories = soup.select('div.side_categories ul.nav-list ul li a')

  for cat in categories:
    url_categoria = url + cat['href']

    while True:
        response = requests.get(url_categoria)
        html = response.text
        soup = BeautifulSoup(html , "html.parser")

        categorias = soup.find_all('h1')
        for categoria in categorias:
            livros = soup.find_all('article' , class_="product_pod")
            for livro in livros:
                print (f"Categoria: {categoria.text.strip()}")
                print(f"Titulo: {livro.find('h3').text.strip()}")
                print(f"Imagem: {livro.find('img')['src']}")
                print(f"Preco: {livro.find('p', class_='price_color').text.strip()}")
                print(f"Estoque: {livro.select_one('p.instock.availability').get_text(strip=True)}")
                estrelas_tag = livro.find('p', class_='star-rating')
                classes = estrelas_tag.get("class", [])
                avaliacao = [c for c in classes if c != "star-rating"][0]
                print(f"Avaliacao: {avaliacao}")

                novo_livro = Livros(
                    Titulo=livro.find('h3').text.strip(),
                    Preco=livro.find('p', class_='price_color').text.strip(),
                    Avaliacao=avaliacao,
                    Disponibilidade=livro.select_one('p.instock.availability').get_text(strip=True),
                    Categoria=categoria.text.strip(),
                    Imagem=livro.find('img')['src']
                )
                db.session.add(novo_livro)
                db.session.commit()

        # Verifica se há próxima página
        next_button = soup.select_one('li.next > a')
        if next_button:
           
            url_categoria = urljoin(url_categoria, next_button['href'])
        else:
            break