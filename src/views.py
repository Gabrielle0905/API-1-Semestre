from flask import Flask,render_template,url_for,request,flash,redirect, session, jsonify, make_response, send_from_directory, abort
from main import app, caminho_usuarios, caminho_equipes
from datetime import datetime
from xhtml2pdf import pisa
from werkzeug.security import generate_password_hash, check_password_hash
from utils import *
import io
import time
import json
import os

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

@app.route('/')
def homepage():
    return render_template('first_page.html')

@app.route('/login', methods=['GET','POST'])
def redirect_user():
    escolha = request.form.get('user-type')

    if escolha == 'Aluno':
        return redirect('/login/aluno')

    if escolha == 'Docente':
        return redirect('/login/docente')

    if escolha == 'Equipe':
        return redirect('/login/membro')
    
    else:
        flash('Por favor, selecione um tipo de usuário antes de continuar!!', 'error')
        return redirect('/')
    
@app.route('/login/aluno', methods=['GET', 'POST'])
def login_aluno():
    if request.method == 'POST':
        cpf = request.form['cpf']
        senha_digitada = request.form['senha']

        usuarios = load_user()

        if cpf in usuarios and check_password_hash(usuarios[cpf]['senha'], senha_digitada) and usuarios[cpf]['funcao'] == 'aluno':
            session['usuario_logado'] = cpf
            session['cpf'] = cpf
            session['funcao'] = 'aluno'
            return redirect('/home/aluno')
        else:
            flash('CPF ou senha inválidos!', 'error')
            return render_template('login_aluno.html')
    return render_template('login_aluno.html')

@app.route('/login/docente', methods=['GET', 'POST'])
def login_docente():
    if request.method == 'POST':
        cpf = request.form['cpf']
        senha_digitada = request.form['senha']
        usuarios = load_user()

        if cpf in usuarios and check_password_hash(usuarios[cpf]['senha'], senha_digitada) and usuarios[cpf]['funcao'] == 'docente':
            session['usuario_logado'] = cpf
            session['cpf'] = cpf
            session['funcao'] = 'docente'
            return redirect('/home/docente')
        else:
            flash('CPF ou senha inválidos!', 'error')
            return redirect('/login/docente')
    return render_template('login_docente.html')

@app.route('/login/membro', methods=['GET', 'POST'])
def login_membro():
    if request.method == 'POST':
        cpf = request.form['cpf']
        senha_digitada = request.form['senha']

        usuarios = load_user()
        funcoes_permitidas = ['sm', 'po', 'dt']

        if cpf in usuarios and check_password_hash(usuarios[cpf]['senha'], senha_digitada) and usuarios[cpf]['funcao'] in funcoes_permitidas:
            session['usuario_logado'] = cpf
            session['cpf'] = cpf
            session['funcao'] = usuarios[cpf]['funcao'] 
            return redirect('/home/membro')
        else:
            flash('CPF ou senha inválidos!', 'error')
            return redirect('/login/membro')
    return render_template('login_membro.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['name']
        cpf = request.form['cpf']
        email = request.form['email']
        senha = request.form['senha']
        funcao = "aluno"

        try:
            with open(caminho_usuarios,'r') as u:
                usuarios = json.load(u)
        except FileNotFoundError:
            usuarios = {}

        if cpf in usuarios:
            flash('CPF já cadastrado!', 'error')
            return redirect('/cadastro')
        
        senha_hash = generate_password_hash(senha)
        
        usuarios[cpf] = {
            'nome': nome,
            'email': email,
            'senha': senha_hash,
            'funcao': funcao
        }

        save_user(usuarios)
        return cadastroconcluido()



    return render_template('cadastro.html') 
   
@app.route('/autenticar')
def cadastroconcluido():
    return render_template('autenticar.html')
   

@app.route('/home/aluno')
@login_required(['aluno'], rota_login='login_aluno')
def homestudent():
    primeiro_nome = get_primeiro_nome()   
    return render_template('home_student.html', nome=primeiro_nome)

@app.route("/home/aluno/enviar")
@login_required(['aluno'], rota_login='login_aluno')
def upload_form():
    return render_template('upload_certificates.html')

@app.route('/home/aluno/upload', methods=['POST'])
@login_required(['aluno'], rota_login='login_aluno')
def upload_file():
    if 'file' not in request.files:
        return "Nenhum arquivo selecionado", 400
    file = request.files['file']
    
    if file.filename == '':
        return "Nenhum arquivo selecionado", 400
    
    if not file.filename.lower().endswith('.pdf'):
        return "Formato invalido. Apenas PDF permitido", 400
    
    # Dados do Formulario
    nome = request.form.get("nome")
    ra = request.form.get("ra")
    turma = request.form.get("turma")
    tipo = request.form.get("tipo")
    data = request.form.get("data")
    periodo = request.form.get("periodo")
    crm = request.form.get("crm")
    
    # Gerar nome único para salvar o arquivo
    diaupload = time.strftime("%d%m%Y_%H%M%S")
    filename = f"{ra}_{diaupload}.pdf"
    
    file.save(os.path.join(app.config['uploads_atestados'], filename))
    
    # Carregar atestados existentes
    atestados = get_atestados()
    # Gerar novo ID — aqui, usa o maior ID atual + 1 ou começa no 1
    if atestados:
        novo_id = max(a['ID'] for a in atestados) + 1
    else:
        novo_id = 1
        
    # Novo Registro
      # Novo registro
    novo_atestado = {
        'ID': novo_id,
        'Nome': nome,
        'RA': ra,
        'Turma': turma,
        'Tipo': tipo,
        'Data': data,
        'Periodo': periodo,
        'CRM': crm,
        'Nome do arquivo': filename,
        'Status': "Pendente",
        'Motivo': "",
        'CPF': session['cpf']
    }
    
    # Adicionar novo atestado à lista
    atestados.append(novo_atestado)
    
    # Salvar JSON atualizado
    save_atestados(atestados)
    
    return render_template("confirm_upload.html")    

@app.route("/home/aluno/gerenciar_atestados/", methods=["GET"])
@login_required(['aluno'], rota_login='login_aluno')
def listar_atestados_alunos():
    pesquisa = request.args.get("pesquisa", "") 
    atestados = atestados_usuario()
    resultados = filtrar_atestados(atestados, pesquisa)
    return render_template('gerenciamento_de_atestados_aluno.html', atestados = resultados)

@app.route("/home/aluno/gerenciar_atestados/download/<int:atestado_id>")
def download_arquivo(atestado_id):
    # Busca o atestado pelo ID
    atestados = get_atestados()
    atestado = next((a for a in atestados if a["ID"] == atestado_id), None)

    if atestado:
        nome_arquivo = atestado["Nome do arquivo"]
        diretorio = app.config['uploads_atestados']
        caminho_arquivo = os.path.join(diretorio, nome_arquivo)

        if os.path.exists(caminho_arquivo):
            return send_from_directory(directory=diretorio, path=nome_arquivo, as_attachment=True)
        else:
            return abort(404, description="Arquivo não encontrado.")
    else:
        return abort(404, description="Atestado não encontrado.")
    
@app.route("/home/aluno/gerenciar_atestados/excluir", methods=['POST'])
def excluir_atestado_aluno():
    id_validado = validar_id_do_formulario(request)

    if id_validado is None:
        flash("ID inválido para exclusão.")
        return redirect(url_for('listar_atestados_alunos'))

    sucesso = excluir_atestados_porid(id_validado)

    if sucesso:
        flash("Atestado excluído com sucesso!")
    else:
        flash("Atestado não encontrado.")

    return redirect(url_for('listar_atestados_alunos'))

@app.route('/home/docente')
@login_required(['docente'], rota_login='login_docente')
def homedocente():
    primeiro_nome = get_primeiro_nome()
    return render_template('home_docente.html', nome=primeiro_nome)

@app.route('/home/docente/gerenciar_atestados/relatorios/gerarpdf')
@login_required(['docente'], rota_login='login_docente')
def gerar_pdf():
    atestados = get_atestados()
    data_hoje = datetime.today().strftime('%d/%m/%Y')
    atestados_filtrados = sorted(atestados, key=lambda x: x['Data'], reverse=True)
    html = render_template('relatorios.html', atestados = atestados_filtrados, data_hoje = data_hoje)
    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.StringIO(html), dest = result)
    if not pdf.err:
        response = make_response(result.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=relatorio.pdf'
        return response
    else:
        return "Erro ao gerar PDF", 500
    
@app.route('/home/docente/estatisticas')
@login_required(['docente'], rota_login='login_docente')
def estatisticas_afastamento():
    return render_template('estatisticas_afastamento.html')

@app.route('/home/membro')
@login_required(['sm', 'po', 'dt'], rota_login='login_membro')
def homemembro():
    primeiro_nome = get_primeiro_nome()
    user_type = session.get('funcao')
    return render_template('homeMaster.html', nome=primeiro_nome, user_type=user_type)

@app.route('/home/membro/avaliar')
@login_required(['sm', 'po', 'dt'], rota_login='login_membro')
def avaliarmembro():
    return render_template('avaliar_membro.html')

@app.route('/save_data', methods=['POST'])
@login_required(['sm', 'po', 'dt'], rota_login='login_membro')
def save_data():
    data = request.get_json()
    folder_path = 'src'
    file_path = os.path.join(folder_path, 'dados.json')

    os.makedirs(folder_path, exist_ok=True)

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                current_data = json.load(file)
            except json.JSONDecodeError:
                current_data = []
        current_data.append(data)
    else:
        current_data = [data]

    with open(file_path, 'w') as file:
        json.dump(current_data, file, indent=2)

    return jsonify({'message': 'Dados salvos com sucesso!'}), 200

@app.route('/home/membro/confirm_evaluation')
@login_required(['sm', 'po', 'dt'], rota_login='login_membro')
def confirm_evaluation():
    return render_template('confirm_evaluation.html')


@app.route('/home/membro/burndown')
@login_required(['sm', 'po', 'dt'], rota_login='login_membro')
def burndown():
    return render_template('BurndownChart.html')

@app.route('/home/master/registroscrum', methods=['GET','POST'])
@login_required(['sm'], rota_login='login_membro')
def registroscrum():
    with open(caminho_equipes, 'r', encoding='utf-8') as f:
        equipes = json.load(f)
    
    if request.method == 'POST':
        nome = request.form['name']
        cpf = request.form['cpf']
        email = request.form['email']
        senha = request.form['senha']
        funcao = request.form['funcao']
        equipe = get_equipe()

        try:
            with open(caminho_usuarios,'r') as u:
                usuarios = json.load(u)
        except FileNotFoundError:
            usuarios = {}
        if cpf in usuarios:
            flash('CPF já cadastrado!','error') 
            return redirect(url_for('registroscrum'))
        
        senha_hash = generate_password_hash(senha)

        if equipe in equipes:
            nome_com_funcao = f"{nome} (Scrum Master)"
            if nome_com_funcao not in equipes[equipe]['Membros']:
                equipes[equipe]['Membros'].append(nome_com_funcao)
        save_membro(equipes)

        usuarios[cpf] = {
            'nome': nome,
            'email': email,
            'senha' : senha_hash,
            'funcao' : funcao,
            'equipe' : equipe
        }
        save_user(usuarios)
        return cadastroconcluido()
    
    return render_template('cadastro_membro.html')

@app.route('/home/membro/gerenciar')
@login_required(['sm', 'po', 'dt'], rota_login='login_membro')
def gerenciaravaliacoes():
    return render_template('comparacao_sprint.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso.', 'success')
    return redirect('/')


@app.route('/login/adm', methods=['GET', 'POST'])
def login_adm():
    if request.method == 'POST':
        cpf = "ADM"
        senha_digitada = request.form['senha']

        usuarios = load_user()

        if cpf in usuarios and check_password_hash(usuarios[cpf]['senha'], senha_digitada) and usuarios[cpf]['funcao'] == 'adm':
            session['usuario_logado'] = cpf
            session['cpf'] = cpf
            session['funcao'] = 'adm'
            return redirect('/adm')
        else:
            flash('CPF ou senha inválidos!', 'error')
            return render_template('login_adm.html')
    return render_template('login_adm.html')

@app.route('/adm')
@login_required(['adm'], rota_login='login_adm')
def administracao():
    primeiro_nome = get_primeiro_nome()
    return render_template('home_adm.html', nome=primeiro_nome)

@app.route('/adm/acessos', methods=['GET', 'POST'])
@login_required(['adm'], rota_login='login_adm')
def criar_acesso():
    with open(caminho_equipes, 'r', encoding='utf-8') as f:
        equipes = json.load(f)

        if request.method == 'POST':
            nome = request.form['name']
            cpf = request.form['cpf']
            email = request.form['email']
            senha = request.form['senha']
            funcao = request.form['funcao']

            try:
                with open(caminho_usuarios,'r') as u:
                    usuarios = json.load(u)
            except FileNotFoundError:
                usuarios = {}
            if cpf in usuarios:
                flash('CPF já cadastrado!','error') 
                return redirect(url_for('criar_acesso'))
            
            senha_hash = generate_password_hash(senha)

            if funcao == "sm":
                equipe = request.form['equipe']
                
                usuarios[cpf] = {
                    'nome': nome,
                    'email': email,
                    'senha' : senha_hash,
                    'funcao' : funcao,
                    'equipe' : equipe
                }

                if equipe in equipes:
                    nome_com_funcao = f"{nome} (Scrum Master)"
                    if nome_com_funcao not in equipes[equipe]['Membros']:
                        equipes[equipe]['Membros'].append(nome_com_funcao)

                    save_membro(equipes)

                save_user(usuarios)
                return redirect(url_for('administracao'))
            
            usuarios[cpf] = {
                'nome': nome,
                'email': email,
                'senha' : senha_hash,
                'funcao' : funcao
            }
            save_user(usuarios)
            return redirect(url_for('administracao'))    

    return render_template('criar_acesso.html', equipes=equipes)

@app.route('/adm/equipes')
@login_required(['adm'], rota_login='login_adm')
def gerenciar_equipes():
    with open(caminho_equipes, 'r', encoding='utf-8') as f:
        equipes = json.load(f)
    return render_template('gerenciar_equipes.html', equipes=equipes)

@app.route('/adm/equipes/adicionar', methods=['GET', 'POST'])
@login_required(['adm'], rota_login='login_adm')
def adicionar_equipe():
    if request.method == 'POST':
        nome_equipe = request.form['name']
        membros = []

        try:
            with open(caminho_equipes,'r') as u:
                equipes = json.load(u)
        except FileNotFoundError:
            equipes = {}
        if nome_equipe in equipes:
            flash('Equipe já cadastrado!','error') 
            return redirect(url_for('adicionar_equipe'))

        equipes[nome_equipe] = {
            'Membros' : membros,
        }
        save_equipe(equipes)
        return redirect(url_for('gerenciar_equipes')) 
    
    return render_template('add_equipes.html')