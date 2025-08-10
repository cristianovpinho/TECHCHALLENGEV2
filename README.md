# PROJETO DE INGESTÃO E DISPONIBILIZAÇÃO DE DADOS VIA API

## 🔶 Descrição do Projeto e Arquitetura

O projeto consiste em uma **API REST**, desenvolvida em **Flask**, para gerenciamento de um catálogo de livros. A API inclui:

- **Autenticação de usuários** via **JWT**.
- **Documentação interativa** fornecida pelo **Swagger**.

A aplicação permite registrar e autenticar usuários, consultar livros por diferentes critérios, listar categorias e obter detalhes individuais.

A arquitetura segue um padrão **MVC simplificado**:

- **Model:** Implementado com **SQLAlchemy**, define as tabelas `Livros` e `Usuario`.
- **View/Controller:** As rotas do **Flask** atuam como controladores, processando requisições e retornando respostas em formato **JSON**.
- **Camada de segurança:** Gerenciada pelo **`flask_jwt_extended`**, restringindo o acesso a rotas protegidas.
- **Documentação:** Integrada com **Flasgger**, permitindo testes diretos via interface **Swagger UI**.

O banco de dados é criado automaticamente na inicialização do aplicativo e armazenado localmente.

---

## 🔶 Instruções de Instalação e Configuração

#### Pré-requisitos
- **Python 3.8** ou superior instalado
- **pip** atualizado

#### Clonar o repositório
```bash
git clone [https://github.com/cristianovpinho/TECHCHALLENGEV2](https://github.com/cristianovpinho/TECHCHALLENGEV2)
cd TECHCHALLENGEV2
```

### Criar e ativar o ambiente virtual
```bash
python -m venv venv
# No Windows
.\venv\Scripts\activate
# No macOS/Linux
source venv/bin/activate
```

### Instalar dependências
```bash
pip install -r requirements.txt
```
### Configurar variáveis de ambiente
Crie um arquivo chamado config.py na raiz do projeto com as seguintes variáveis:
```
SECRET_KEY=sua_chave_secreta
SQLALCHEMY_DATABASE_URI=sqlite:///livros.db
JWT_SECRET_KEY=sua_chave_jwt
```

### Criar e alimentar o banco de dados
Execute o script de raspagem para popular a base de dados:
```bash
python alimentar_base.py
```
Esse script fará a raspagem do site Books to Scrape e gravará os livros no banco livros.db.


## Executar a aplicação
A API estará disponível em: http://127.0.0.1:5000
A documentação Swagger estará em: http://127.0.0.1:5000/apidocs

## 🔶 Documentação das rotas da API.

Esta API utiliza **JSON Web Tokens (JWT)** para autenticação, garantindo a segurança da maioria dos endpoints. Para acessar as rotas protegidas, você deve incluir o token no cabeçalho da requisição.

**Formato do cabeçalho de autenticação:**

#### 🧑‍💻 Endpoints de Usuários

| Método | Rota | Autenticação | Descrição |
| :--- | :--- | :--- | :--- |
| `POST` | `/registro` | Sim | Registra um novo usuário. |
| `POST` | `/login` | Não | Autentica um usuário e retorna um token JWT para acesso. |

#### 📚 Endpoints de Livros

| Método | Rota | Autenticação | Descrição |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/books` | Sim | Retorna todos os livros do catálogo. |
| `GET` | `/api/v1/books/<id_livro>` | Sim | Retorna os detalhes de um livro específico, usando seu ID. |
| `GET` | `/api/v1/books/search?categoria=...&titulo=...` | Sim | Permite buscar livros, filtrando por `categoria` e/ou `título`. |
| `GET` | `/api/v1/categories` | Sim | Retorna uma lista de todas as categorias distintas disponíveis no catálogo. |

### Observações Adicionais

* **Formato de Resposta:** Todas as respostas da API são retornadas no formato **JSON**.
* **Documentação Interativa:** Para explorar e testar os endpoints diretamente, acesse a documentação interativa do **Swagger UI** no seguinte endereço:
    [http://127.0.0.1:5000/apidocs](http://127.0.0.1:5000/apidocs)

## 🔶 Exemplos de Chamadas (Requests/Responses)

### 📞 Registro de Usuário
Requisição:
```HTTP
POST /registro
Content-Type: application/json

{
    "Nome_usuario": "usuario1",
    "Senha": "senha123"
}
```
Resposta 201 (Sucesso):
```JSON
{
    "Sucesso": "Usuário criado com sucesso"
}
```
Resposta 400 (Erro):
```JSON
{
    "Erro": "Usuário já existe"
}
```

### 📞 Login e Obtenção de Token
Requisição:
```HTTP
POST /login
Content-Type: application/json

{
    "Nome_usuario": "usuario1",
    "Senha": "senha123"
}
```
Resposta 201 (Sucesso):
```JSON
{
    "token": "eyJhbGciOiJIUzI1NiIs..."
}
```
Resposta 400 (Erro):
```JSON
{
    "Erro": "Usuário ou senha inválidos"
}
```

### 📞 Listar Todos os Livros
Requisição:
```HTTP
GET /api/v1/books
Authorization: Bearer <seu_token>
```

Resposta 200 (Sucesso):
```JSON
[
    {
        "id": 1,
        "titulo": "It's Only the Himalayas",
        "Categoria": "Travel",
        "preco": "£45.17",
        "Avaliacao": "Two",
        "Disponibilidade": "In stock",
        "Imagem": "../../../../media/cache/27/a5/27a53d0bb95bdd88288eaf66c9230d7e.jpg"
    }
]
```

### 📞 Buscar Livro por ID
Requisição:
```HTTP
GET /api/v1/books/1
Authorization: Bearer <seu_token>
```
Resposta 200 (Sucesso):
```JSON
[
    {
        "id": 1,
        "titulo": "It's Only the Himalayas",
        "Categoria": "Travel",
        "preco": "£45.17",
        "Avaliacao": "Two",
        "Disponibilidade": "In stock",
        "Imagem": "../../../../media/cache/27/a5/27a53d0bb95bdd88288eaf66c9230d7e.jpg"
    }
]
```
Resposta 404 (Erro):
```JSON
{
    "erro": "Livro não encontrado"
}
```

### 📞 Buscar Livros por Categoria e/ou Título
Requisição:
```HTTP
GET /api/v1/books/search?categoria=Travel&titulo=Himalayas
Authorization: Bearer <seu_token>
```
Resposta 200 (Sucesso):
```JSON
[
    {
        "id": 1,
        "titulo": "It's Only the Himalayas",
        "Categoria": "Travel",
        "preco": "£45.17",
        "Avaliacao": "Two",
        "Disponibilidade": "In stock",
        "Imagem": "../../../../media/cache/27/a5/27a53d0bb95bdd88288eaf66c9230d7e.jpg"
    }
]
```

### 📞 Listar Categorias
```HTTP
GET /api/v1/categories
Authorization: Bearer <seu_token>
```
Resposta 200 (Sucesso):
```JSON
[
    "Travel",
    "Mystery",
    "Historical Fiction"
]
```







