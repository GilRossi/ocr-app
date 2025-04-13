import re

# Termos irrelevantes que devem ser removidos do nome do produto
IGNORAR_TERMS = [
    "cada", "g", "kg", "ml", "l", "un", "tp", "pet", "frasco", "garrafa",
    "r$", "leve", "pague", "pague menos", "mais", "promo", "oferta", "com"
]

def limpar_nome_produto(nome: str) -> str:
    """
    Remove preços, termos irrelevantes e caracteres especiais do nome.
    """
    nome = re.sub(r'R\$ ?\d+[,\.]?\d*', '', nome, flags=re.IGNORECASE)  # Remove valores
    nome = re.sub(r'\b(?:' + '|'.join(IGNORAR_TERMS) + r')\b', '', nome, flags=re.IGNORECASE)  # Remove termos
    nome = re.sub(r'[^\w\sÀ-ÿ]', '', nome)  # Remove pontuação e símbolos
    nome = re.sub(r'\s+', ' ', nome).strip()  # Remove espaços repetidos
    return nome.title()


def extrair_promocoes(texto: str) -> list:
    """
    Extrai promoções do texto OCR.
    Cada promoção inclui nome, preço original (se houver), preço promocional e condição.
    """
    promocoes = []
    linhas = texto.splitlines()

    for i, linha in enumerate(linhas):
        # Busca por preços na linha atual
        precos = re.findall(r'R\$ ?\d{1,3}(?:[.,]\d{2})', linha)
        if not precos:
            continue

        preco_promocional = precos[-1]
        preco_original = precos[0] if len(precos) > 1 and precos[0] != preco_promocional else None

        # Tenta capturar até 3 linhas acima como parte do nome
        nome_linhas = []
        for j in range(1, 4):
            if i - j >= 0:
                linha_acima = linhas[i - j].strip()
                if not re.search(r'R\$ ?\d', linha_acima, flags=re.IGNORECASE):
                    nome_linhas.insert(0, linha_acima)

        nome_completo = limpar_nome_produto(" ".join(nome_linhas))

        # Tenta detectar condição (ex: "A PARTIR DE 3 UN.")
        condicao = ""
        for j in range(1, 3):
            if i + j < len(linhas) and "A PARTIR DE" in linhas[i + j].upper():
                condicao = linhas[i + j].strip()
                break

        if nome_completo and len(nome_completo.split()) >= 2:
            promocoes.append({
                "produto": nome_completo,
                "preco_original": preco_original,
                "preco_promocional": preco_promocional,
                "condicao": condicao
            })

    return promocoes