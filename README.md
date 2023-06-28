# Audio P2P

Trabalho da disciplinas de Redes de Computadores 2 do Instituto de Computação da UFF.

## Setup

Necessário ter `pyenv` e `poetry` instalados.

Rodar `make init` a primeira vez que for configurar o projeto. Esse script vai tentar instalar a versão certa do Python e fazer o `poetry` usar essa versão no projeto.

Dando tudo certo, `make run-server` ou `make run-client` deve conseguir rodar o projeto.

`make inspect` vai rodar formatador, linter (e testes quando houver).

## Ações

Cada ação pode ser um json com um campo `action` que define qual a ação a ser executada. Esse campo também definiria qual deve ser o resto do payload.

### Cadastro de cliente

- Recusar cadastro caso cliente já esteja cadastrado.

Requisição:

```json
{
  "action": "register",
  "port": 12345,
  "songs": [
    "song1"
    // ...
  ]
}
```

Resposta:

```json
{
  "message": "user registered succesfully"
}
```

Em caso de usuário já existente:

```json
{
  "message": "user already exists"
}
```

### Descadastro de cliente

- Descadastrar o cliente que mandou a mensagem
- Ou em caso de conexão fechada

Requisição:

```json
{
  "action": "unregister"
}
```

Resposta:

```json
{
  "message": "OK"
}
```

### Listagem de clientes

- Retornar todos os clientes cadastrados com suas respectivas músicas

```json
{
  "action": "list"
}
```

Resposta:

```json
{
  "peers": [
    {"ip": "127.0.0.1", "port": 12345, "songs": ["song1.mp4", "song2.mp4"]}
    {"ip": "128.0.0.1", "port": 12346, "songs": ["song4.mp4", "song5.mp4"]}
  ]
}
```
### Outro cliente quer música

- Avisar um cliente que outro quer uma música

```json
{
  "action": "notify-request",
  "client": {"ip": "127.0.0.1", "port": 12345},
  "song": "song.wav"
}
```

Resposta:

```json
{
  "message": "OK"
}
```
```json
{
  "message": "Not OK"
}
```

