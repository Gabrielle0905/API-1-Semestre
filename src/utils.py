from functools import wraps
from flask import session, redirect, url_for, flash
from main import caminho_usuarios, caminho_atestados, caminho_equipes
import json

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