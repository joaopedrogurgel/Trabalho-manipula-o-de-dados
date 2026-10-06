# Pedro Luiz Pereira Zampar - RA: 145117
# Pedro Henrique Nishida Sarri - RA: 145121
# João Pedro Medeiros Gurgel - RA: 145118

INSTRUÇÕES DE EXECUÇÃO E DOCUMENTAÇÃO DO PROJETO

1. ARQUIVOS INCLUSOS

* trabalho_1.py: Código-fonte referente ao Trabalho 1 (Busca, Inserção e Remoção Lógica).
* trabalho_2.py: Código-fonte referente ao Trabalho 2 (Gerenciamento de LED com Best Fit e Estatísticas).
* filmes.dat: Arquivo binário manipulado pelos programas (gerado automaticamente se não existir).

---

2. COMANDO PARA EXECUÇÃO

Para iniciar o programa do Trabalho 1:
python trabalho_1.py

Para iniciar o programa do Trabalho 2:
python trabalho_2.py

---

3. DESCRIÇÃO DOS PARÂMETROS DE ENTRADA

Ambos os programas interagem com o usuário via terminal por meio de menus numéricos e solicitações de dados textuais.

* Menu Principal (Opções):
  - "1", "2", "3" ou "4": Seleção da funcionalidade desejada conforme o menu exibido.
  - "0": Finaliza e fecha o programa com segurança, garantindo a gravação do arquivo física no disco.

* Exemplo Prático de Parâmetros para Inserção (Filme Real):
  - ID: 101
  - Título: Interstellar
  - Diretor: Christopher Nolan
  - Ano: 2014
  - Gênero(s): Ficção Científica, Drama, Aventura
  - Duração: 169
  - Elenco: Matthew McConaughey, Anne Hathaway, Jessica Chastain

* Parâmetros para Busca ou Remoção:
  - ID do filme: Texto correspondente exatamente ao ID informado no momento do cadastro do filme (ex: 101).