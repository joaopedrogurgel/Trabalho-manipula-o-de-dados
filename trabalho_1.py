# Pedro Luiz Pereira Zampar - RA: 145117
# Pedro Henrique Nishida Sarri - RA: 145121
# João Pedro Medeiros Gurgel - RA: 145118

import os

NOME_ARQUIVO = "filmes.dat"

def inicializar_arquivo() -> None:
    """Garante que o arquivo exista e tenha o cabeçalho inicial de 4 bytes."""
    if not os.path.exists(NOME_ARQUIVO):
        with open(NOME_ARQUIVO, "wb") as f:
            # Inicializa o cabeçalho com -1 (representando int com sinal de 4 bytes)
            # Usamos signed=True porque a LED usará offsets com sinal (-1)
            f.write((-1).to_bytes(4, byteorder='big', signed=True))

def buscar_filme(id_busca: str) -> int | None:
    """Busca um filme pelo ID e exibe suas informações."""
    inicializar_arquivo()
    
    with open(NOME_ARQUIVO, "rb") as f:
        # Define o offset inicial e pula os 4 bytes do cabeçalho
        byte_offset = 4
        f.seek(byte_offset)
        
        while True:
            tam_bytes = f.read(2)
            
            if not tam_bytes:
                break  # Fim do arquivo
                
            # Converte os 2 bytes do tamanho do registro (inteiro sem sinal)
            tam_registro = int.from_bytes(tam_bytes, byteorder='big', signed=False)
            
            # Lê o registro de tamanho variável baseado no tamanho obtido
            registro_bytes = f.read(tam_registro)
            registro_texto = registro_bytes.decode('utf-8')
            
            # Verifica se o registro foi removido logicamente
            if registro_bytes[0] in b"*":
                byte_offset += 2 + tam_registro # Atualiza o offset para o próximo registro
                continue
                
            # Divide o registro em campos usando o delimitador '|'    
            campos = registro_texto.split("|")
            
            # O primeiro campo é o ID único do filme
            if campos[0] == id_busca:
                print(f"\nFilme Encontrado (Offset: {byte_offset}):")
                print(f"    ID: {campos[0]}")
                print(f"    Título: {campos[1]}")
                print(f"    Diretor: {campos[2]}")
                print(f"    Ano: {campos[3]}")
                print(f"    Gênero(s): {campos[4]}")
                print(f"    Duração: {campos[5]}")
                print(f"    Elenco: {campos[6]}")
                return byte_offset
            
            byte_offset += 2 + tam_registro # Atualiza o offset para o próximo registro
                
        print(f"\nErro: Filme com ID '{id_busca}' não foi encontrado.")
        return None

def inserir_filme() -> None:
    """Insere um novo filme ao final do arquivo."""
    inicializar_arquivo()
    
    print("\nDigite os dados para o novo filme:")
    id_filme = input("ID: ")
    titulo = input("Título: ")
    diretor = input("Diretor: ")
    ano = input("Ano: ")
    genero = input("Gênero(s): ")
    duracao = input("Duração: ")
    elenco = input("Elenco: ")
    
    # Junta os campos usando o delimitador '|'
    registro_texto = f"{id_filme}|{titulo}|{diretor}|{ano}|{genero}|{duracao}|{elenco}"
    registro_bytes = registro_texto.encode('utf-8')
    tam_registro = len(registro_bytes)
    
    # Abre no modo de leitura e escrita binária sem apagar o arquivo
    with open(NOME_ARQUIVO, "r+b") as f:
        # Move o ponteiro para o final do arquivo para realizar a inserção
        f.seek(0, 2)
        
        # Grava o tamanho do registro em 2 bytes
        f.write(tam_registro.to_bytes(2, byteorder='big', signed=False))
        # Grava os dados do filme
        f.write(registro_bytes)
        
        print(f"Filme '{titulo}' inserido com sucesso!")

def remover_filme(id_busca: str) -> None:
    """Realiza a remoção lógica marcando o primeiro caractere com '*'."""
    inicializar_arquivo()
    
    # Reutiliza a busca para encontrar o offset e tamanho do registro
    resultado = buscar_filme(id_busca)
    if not resultado:
        return
        
    offset = resultado
    
    confirmar = input("\nDeseja realmente remover este filme? (S/N): ").upper()
    if confirmar != 'S':
        print("Operação cancelada.")
        return
        
    with open(NOME_ARQUIVO, "r+b") as f:
        # Reposiciona o ponteiro exatamente no início do texto (pula os 2 bytes de tamanho)
        f.seek(offset + 2)
        
        # Grava um * para indicar que o registro foi removido logicamente
        f.write(b"*")
        
        print(f"Filme com ID {id_busca} removido logicamente com sucesso!")

def menu() -> None:
    while True:
        print("\n================ MENU ================")
        print("1. Buscar Filme")
        print("2. Inserir Filme")
        print("3. Remover Filme")
        print("0. Sair")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            id_busca = input("Digite o ID do filme: ")
            buscar_filme(id_busca)
        elif opcao == "2":
            inserir_filme()
        elif opcao == "3":
            id_busca = input("Digite o ID do filme a ser removido: ")
            remover_filme(id_busca)
        elif opcao == "0":
            print("Saindo do programa...")
            break
        else:
            print("Opção inválida! Tente novamente.")

# Inicia o programa
if __name__ == "__main__":
    menu()