from functools import wraps
from flask import session, redirect, url_for, flash
from main import caminho_usuarios, caminho_atestados, caminho_equipes
import json
import os

def load_user():
    with open(caminho_usuarios, 'r') as u:
        return json.load(u)
    
def save_user(usuarios):
    with open(caminho_usuarios, 'w') as u:
        json.dump(usuarios, u, indent=4)

def save_equipe(equipes):
    with open(caminho_equipes, 'w') as u:
        json.dump(equipes, u, indent=4)

def save_membro(equipes):
    with open(caminho_equipes, 'w', encoding='utf-8') as f:
        json.dump(equipes, f, ensure_ascii=False, indent=4)


def get_primeiro_nome():
    cpf = session.get('cpf')
    funcao = session.get('funcao')
    usuarios = load_user()

    if not cpf or cpf not in usuarios:
        return 'Usuário'

    usuario = usuarios[cpf]
    nome_completo=usuario.get("nome", 'Usuário')
    primeiro_nome=nome_completo.split()[0]
    return primeiro_nome

def get_equipe():
    cpf = session.get('cpf')
    funcao = session.get('funcao')
    usuarios = load_user()

    if not cpf or cpf not in usuarios:
        return 'Equipe não encontrada'

    usuario = usuarios[cpf]
    equipe = usuario.get("equipe", 'Equipe não encontrada')
    return equipe

def save_atestados(atestados):
    with open(caminho_atestados, 'w') as u:
        json.dump(atestados, u, indent=4)


def login_required(funcoes_permitidas, rota_login='login'):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'usuario_logado' not in session or session.get('funcao') not in funcoes_permitidas:
                flash('Você precisa estar logado para acessar essa página!', 'error')
                return redirect(url_for(rota_login))
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Funções para o funcionamento do Upload de Atestados e do Gerenciamento dos Json.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_ARQUIVO = os.path.join(BASE_DIR, 'uploads_atestados/dados_atestados.json')

def get_atestados():
    if not os.path.exists(CAMINHO_ARQUIVO):
        return[]
    with open(CAMINHO_ARQUIVO, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_atestados(dados):
    with open(CAMINHO_ARQUIVO, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
 
# Função de filtros com a barra de pesquisa de atestados.        
def filtrar_atestados(atestados, pesquisa):
    pesquisa = pesquisa.lower() 
    resultados = []

    for atestado in atestados:
        if (
            pesquisa in str(atestado.get("ID", "")).lower() or
            pesquisa in atestado.get("Nome", "").lower() or
            pesquisa in atestado.get("RA", "").lower() or
            pesquisa in atestado.get("Turma", "").lower() or
            pesquisa in atestado.get("Tipo", "").lower() or
            pesquisa in atestado.get("Data", "").lower() or
            pesquisa in atestado.get("Periodo", "").lower() or
            pesquisa in atestado.get("CRM", "").lower() or
            pesquisa in atestado.get("Nome do arquivo", "").lower() or
            pesquisa in str(atestado.get("Status", "")).lower() or
            pesquisa in atestado.get("Motivo", "").lower()
        ):
            resultados.append(atestado)

    return resultados

def atestados_usuario():
    todos_atestados = get_atestados()
    resultados = []
    
    for atestado in todos_atestados:
        if atestado['CPF'] == session['cpf']:
            resultados.append(atestado)
            
    return resultados
            
    

# Função que excluir um atestado do Json.
def excluir_atestados_porid(id_para_excluir):
    atestados = get_atestados()
    original_len = len(atestados)
    
    atestados = [a for a in atestados if a.get('ID') != id_para_excluir]
    
    if len(atestados) == original_len:
        return False
    
    save_atestados(atestados)
    return True

# Função para validar o ID de exclusão do Formulario
def validar_id_do_formulario(request):
    id_str = request.form.get('id')
    
    if not id_str or not id_str.isdigit():
        return None
    
    return int(id_str)