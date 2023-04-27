# Audio P2P

Trabalho da disciplinas de Redes de Computadores 2 do Instituto de Computação da UFF.

## Setup

Necessário ter `pyenv` e `poetry` instalados.

Rodar `make init` a primeira vez que for configurar o projeto. Esse script vai tentar instalar a versão certa do Python e fazer o `poetry` usar essa versão no projeto.

Dando tudo certo, `make run-server` ou `make run-client` deve conseguir rodar o projeto.

`make inspect` vai rodar formatador, linter (e testes quando houver).

## TODO

- Definir ações entre cliente e servidor
- Definir protocolo para as mensagens trocadas
- Implementar classes para cada mensagem (com pydantic?)
- Implementar as ações para cada mensagem
- Implementar client
- Implementar server

## Ações

TODO listar ações

## Protocolo

TODO definir tipos de mensagens
