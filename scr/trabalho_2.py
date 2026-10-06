# Pedro Luiz Pereira Zampar - RA: 145117
# Pedro Henrique Nishida Sarri - RA: 145121
# João Pedro Medeiros Gurgel - RA: 145118

import os

NOME_ARQUIVO = "filmes.dat"

def inicializar_arquivo() -> None:
    """Garante que o arquivo exista e tenha o cabeçalho inicial de 4 bytes."""
    if not os.path.exists(NOME_ARQUIVO):
        with open(NOME_ARQUIVO, "wb") as f:
            f.write((-1).to_bytes(4, byteorder='big', signed=True))

def ler_cabecalho(f) -> int:
    """Lê o offset de início da LED no cabeçalho (4 bytes com sinal)."""
    f.seek(0)
    return int.from_bytes(f.read(4), byteorder='big', signed=True)

def escrever_cabecalho(f, offset: int) -> None:
    """Atualiza o offset de início da LED no cabeçalho."""
    f.seek(0)
    f.write(offset.to_bytes(4, byteorder='big', signed=True))

def obter_led_lista() -> list[dict]:
    """Percorre a LED no arquivo e retorna uma lista de dicionários com os espaços mapeados."""
    inicializar_arquivo()
    led = []
    
    with open(NOME_ARQUIVO, "rb") as f:
        prox_offset = ler_cabecalho(f)
        
        while prox_offset != -1:
            # Vai até o registro deletado para ler o tamanho do espaço
            f.seek(prox_offset)
            tam_bytes = f.read(2)
            tam_espaco = int.from_bytes(tam_bytes, byteorder='big', signed=False)
            
            # Pula o tamanho (2 bytes) + o '*' (1 byte) para ler o offset do próximo da lista
            f.seek(prox_offset + 3)
            ponteiro_bytes = f.read(4)
            next_offset = int.from_bytes(ponteiro_bytes, byteorder='big', signed=True)
            
            # Adiciona o espaço à lista de LED
            led.append({"offset": prox_offset, "tam": tam_espaco, "proximo": next_offset})
            prox_offset = next_offset
            
    return led

def imprimir_e_estatisticas_led() -> None:
    """Exibe os elementos da LED e calcula suas estatísticas obrigatórias."""
    led = obter_led_lista()
    
    print("\nLED")
    for espaco in led:
        print(f"[offset: {espaco['offset']}, tam: {espaco['tam']}]")
    print("[offset: -1]")
    print(f"Total: {len(led)} espaços disponíveis")
    
    if len(led) > 0:
        # Obtém os tamanhos para calcular estatísticas
        tamanhos = [e["tam"] for e in led]
        total_bytes = sum(tamanhos)
        maior_espaco = max(tamanhos)
        menor_espaco = min(tamanhos)
        
        print(f"\nTotal de espaços: {len(led)}")
        print(f"Total de bytes livres: {total_bytes}")
        print(f"Maior espaço: {maior_espaco} bytes")
        print(f"Menor espaço: {menor_espaco} bytes")
    else:
        print("\nNenhum espaço disponível na LED.")

def buscar_filme(f, id_busca: str) -> tuple[int, int] | None:
    """Função que percorre o arquivo e retorna (byte_offset, tam_registro) do filme ativo."""
    byte_offset = 4
    f.seek(byte_offset)
    
    while True:
        tam_bytes = f.read(2)
        if not tam_bytes:
            break
            
        tam_registro = int.from_bytes(tam_bytes, byteorder='big', signed=False)
        registro_bytes = f.read(tam_registro)
        
        if registro_bytes[0] in b"*":
            byte_offset += 2 + tam_registro
            continue
            
        registro_texto = registro_bytes.decode('utf-8')
        campos = registro_texto.split("|")
        
        if campos[0] == id_busca:
            return byte_offset, tam_registro
            
        byte_offset += 2 + tam_registro
        
    return None

def inserir_filme_best_fit() -> None:
    """Insere um novo filme utilizando a estratégia Best Fit consultando a LED."""
    inicializar_arquivo()
    
    print("\nDigite os dados para o novo filme (Best Fit):")
    id_filme = input("ID: ")
    titulo = input("Título: ")
    diretor = input("Diretor: ")
    ano = input("Ano: ")
    genero = input("Gênero(s): ")
    duracao = input("Duração: ")
    elenco = input("Elenco: ")
    
    registro_texto = f"{id_filme}|{titulo}|{diretor}|{ano}|{genero}|{duracao}|{elenco}"
    registro_bytes = registro_texto.encode('utf-8')
    tam_necessario = len(registro_bytes)
    
    led = obter_led_lista()
    espaco_escolhido = None
    
    # Como a LED é mantida estritamente em ordem crescente por tamanho,
    # o primeiro espaço que couber o registro já é o Best Fit perfeito.
    for espaco in led:
        if espaco["tam"] >= tam_necessario:
            espaco_escolhido = espaco
            break
            
    with open(NOME_ARQUIVO, "r+b") as f:
        if espaco_escolhido:
            offset_uso = espaco_escolhido["offset"]
            print(f"\nReutilizando espaço no offset {offset_uso} ({espaco_escolhido['tam']} bytes).")
            
            # Desencadeia o espaço em disco atualizando a cadeia de ponteiros
            remover_espaco_da_led_em_disco(f, offset_uso, espaco_escolhido["proximo"])
            
            # Grava os novos dados (pula os 2 bytes de tamanho originais que continuam válidos)
            f.seek(offset_uso + 2)
            f.write(registro_bytes)
            
            # Limpa o restante do espaço que sobrou com fragmentação interna (\x00)
            sobra = espaco_escolhido["tam"] - tam_necessario
            if sobra > 0:
                f.write(b'\x00' * sobra) # Preenche com bytes nulos para evitar lixo de memória
        else:
            print("\nSem espaço adequado na LED. Gravando ao final do arquivo.")
            f.seek(0, 2)
            f.write(tam_necessario.to_bytes(2, byteorder='big', signed=False))
            f.write(registro_bytes)
            
        print(f"Filme '{titulo}' inserido com sucesso!")

def remover_espaco_da_led_em_disco(f, offset_remover: int, proximo_do_removido: int) -> None:
    """Corrige as referências em disco retirando o espaço reutilizado da LED."""
    atual_led = ler_cabecalho(f)
    
    if atual_led == offset_remover:
        escrever_cabecalho(f, proximo_do_removido)
    else:
        while atual_led != -1:
            f.seek(atual_led + 3) # Campo do ponteiro do elemento atual
            ponteiro = int.from_bytes(f.read(4), byteorder='big', signed=True)
            if ponteiro == offset_remover:
                f.seek(atual_led + 3)
                f.write(proximo_do_removido.to_bytes(4, byteorder='big', signed=True))
                break
            atual_led = ponteiro

def remover_filme_com_led(id_busca: str) -> None:
    """Remove logicamente o filme e insere o espaço ordenadamente por tamanho na LED."""
    inicializar_arquivo()
    
    with open(NOME_ARQUIVO, "r+b") as f:
        resultado = buscar_filme(f, id_busca)
        if not resultado:
            print(f"\nErro: Filme com ID '{id_busca}' não foi encontrado.")
            return
            
        offset_removido, tam_registro = resultado
        
        confirmar = input(f"\nDeseja realmente remover o filme de ID {id_busca}? (S/N): ").upper()
        if confirmar != 'S':
            print("Operação cancelada.")
            return
            
        # Carrega os estados da LED para buscar a posição correta de inserção
        led = obter_led_lista()
        
        idx_insercao = 0

        # Avança enquanto o espaço atual for menor que o registro
        # para ao encontrar o primeiro espaço com tamanho >= tam_registro
        while idx_insercao < len(led) and led[idx_insercao]["tam"] < tam_registro:
            idx_insercao += 1
                
        if idx_insercao == len(led):
            prox_ponteiro = -1  # Fim da lista ordenada
        else:
            prox_ponteiro = led[idx_insercao]["offset"]
            
        # Ajusta as conexões de quem vem antes
        if idx_insercao == 0:
            escrever_cabecalho(f, offset_removido)
        else:
            offset_anterior = led[idx_insercao - 1]["offset"]
            f.seek(offset_anterior + 3)
            f.write(offset_removido.to_bytes(4, byteorder='big', signed=True))
            
        # Grava a marcação física em disco no registro desativado
        f.seek(offset_removido + 2)
        f.write(b"*")
        f.write(prox_ponteiro.to_bytes(4, byteorder='big', signed=True))
        
        print(f"Filme com ID {id_busca} removido e indexado na LED com sucesso!")

def menu() -> None:
    while True:
        print("\n================ MENU  ================")
        print("1. Inserir Filme (Best Fit)")
        print("2. Remover Filme (Integrar à LED)")
        print("3. Exibir LED e Estatísticas")
        print("0. Sair")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            inserir_filme_best_fit()
        elif opcao == "2":
            id_busca = input("Digite o ID do filme a ser removido: ")
            remover_filme_com_led(id_busca)
        elif opcao == "3":
            imprimir_e_estatisticas_led()
        elif opcao == "0":
            print("Saindo do programa...")
            break
        else:
            print("Opção inválida! Tente novamente.")

if __name__ == "__main__":
    menu()