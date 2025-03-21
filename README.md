# Reserver - BACK-END

> Back-end do MVP para a disciplina **Desenvolvimento Full Stack Básico** da Pós-Graduação em Engenharia de Software – PUC-Rio.

## 📌 Proposta

O **Reserver** é um sistema de reservas de quadra de tênis que permite que alunos agendem horários de uso de forma simples e eficiente.

### 🎾 Funcionalidades principais

- Visualização dos horários já reservados, evitando conflitos de agendamento.
- Reserva de quadra por **1 hora**, com a opção de remarcar agendamentos futuros.
- API para gerenciamento de reservas e autenticação de usuários.

## 🚀 Instalação

### 1️⃣ Clonar o repositório

Certifique-se de que possui o `git` instalado e execute:

```sh
git clone https://github.com/LucasRosas/pos-pucrio-sprint-1-MVP-back-end.git
cd pos-pucrio-sprint-1-MVP-back-end
```

### 2️⃣ Criar um ambiente virtual

O uso de ambientes virtuais é altamente recomendado. Se ainda não possui o `virtualenv`, instale com:

```sh
pip install virtualenv
```

Depois, crie e ative um ambiente virtual:

```sh
python -m venv .venv
# No Windows:
.venv\Scripts\activate
# No macOS/Linux:
source .venv/bin/activate
```

### 3️⃣ Instalar dependências

Dentro do ambiente virtual, instale as bibliotecas necessárias:

```sh
pip install -r requirements.txt
```

### 4️⃣ Executar a API

Inicie o servidor Flask com:

```sh
flask run --host 0.0.0.0 --port 5000
```

Para desenvolvimento, utilize o modo **reload** para recarregar automaticamente após alterações no código:

```sh
flask run --host 0.0.0.0 --port 5000 --reload
```

### 5️⃣ Rodar os seeders

Após iniciar a API, execute o comando abaixo para popular o banco de dados com usuários de teste:

```sh
flask seed
```

Agora, acesse [http://localhost:5000/#/](http://localhost:5000/#/) no navegador para verificar o status da API.

## 📄 Documentação da API

A API **Reserver** possui documentação interativa disponível no **Swagger**, **Redoc** e **RapiDoc**.

- Acesse [http://localhost:5000/openapi/swagger](http://localhost:5000/openapi/swagger) para visualizar no **Swagger UI**.
- Para escolher outro formato de documentação, acesse: [http://localhost:5000/openapi](http://localhost:5000/openapi).

### 🔀 Rotas Disponíveis

| Método   | Rota         | Descrição                                                                        |
| -------- | ------------ | -------------------------------------------------------------------------------- |
| `GET`    | `/`          | Redireciona para `/openapi`, onde é possível escolher o formato da documentação. |
| `POST`   | `/login`     | Realiza a autenticação do usuário.                                               |
| `GET`    | `/schedules` | Retorna todas as reservas do mês e ano informados.                               |
| `POST`   | `/schedule`  | Adiciona uma nova reserva de quadra.                                             |
| `PATCH`  | `/schedule`  | Atualiza uma reserva existente.                                                  |
| `DELETE` | `/schedule`  | Remove uma reserva existente.                                                    |

## 🔑 Usuários de Teste

O sistema já vem com dois usuários cadastrados para fins de teste:

```sh
Usuário: joaofonseca
Senha: 654321
```

```sh
Usuário: biahaddad
Senha: 123456
```
