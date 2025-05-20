import datetime
import json

# Lista principal onde os atestados serão armazenados
atestados = []

# Função para formatar data de "YYYY-MM-DD" para "dd.mm.yyyy"
def formatar_data(data_iso):
    try:
        data = datetime.datetime.strptime(data_iso, "%Y-%m-%d")
        return data.strftime("%d.%m.%Y")
    except Exception:
        return "xx.xx.xxxx"

# Função para extrair quantidade de dias do período, se possível
def extrair_dias(periodo_str):
    try:
        return int(''.join(filter(str.isdigit, periodo_str)))
    except:
        return None

# Função para calcular a data final (Fim) a partir da data inicial e período
def calcular_fim(data_inicio_str, periodo_str):
    try:
        dias = extrair_dias(periodo_str)
        if dias is None:
            return "xx.xx.xxxx"
        data_inicio = datetime.datetime.strptime(data_inicio_str, "%d.%m.%Y")
        data_fim = data_inicio + datetime.timedelta(days=dias)
        return data_fim.strftime("%d.%m.%Y")
    except Exception:
        return "xx.xx.xxxx"

# Função principal que converte um JSON para o formato da lista de atestados
def adicionar_atestados_de_json(json_data, lista_atestados):
    for nome, dados in json_data.items():
        novo_id = max([a.get("ID", 0) for a in lista_atestados], default=0) + 1

        data_inicio = formatar_data(dados.get("Data", ""))
        periodo = dados.get("Periodo", "")

        novo_atestado = {
            "Nome": nome,
            "Turma": dados.get("Turma", ""),
            "RA": int(dados.get("RA", 0)),
            "Tipo": dados.get("Tipo de Atestado", ""),
            "Inicio": data_inicio,
            "Fim": calcular_fim(data_inicio, periodo),
            "Horas": "xx:xx - xx:xx",
            "Status": "Pendente",
            "Motivo": "-",
            "Comprovante": dados.get("Nome do arquivo", ""),
            "ID": novo_id
        }

        lista_atestados.append(novo_atestado)

# Chamada
with open("src/uploads_atestados/dados_atestados.json", "r", encoding="utf-8") as arquivo:
    dados_json = json.load(arquivo)

adicionar_atestados_de_json(dados_json, atestados)


