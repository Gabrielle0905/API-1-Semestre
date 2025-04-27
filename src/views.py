from flask import Flask,render_template,url_for,request,flash,redirect, session, jsonify
from main import app, UPLOAD_FOLDER, os, caminho_usuarios, caminho_atestados
from lista_atestados import atestados
import time
import json
import os

def load_user():
    with open(caminho_usuarios, 'r') as u:
        return json.load(u)
    
def save_user(usuarios):
    with open(caminho_usuarios, 'w') as u:
        json.dump(usuarios, u, indent=4)

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

def save_atestados(atestados):
    with open(caminho_atestados, 'w') as u:
        json.dump(atestados, u, indent=4)

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
        senha = request.form['senha']

        usuarios = load_user()

        if cpf in usuarios and usuarios[cpf]['senha'] == senha and usuarios[cpf]['funcao'] == 'aluno':
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
        senha = request.form['senha']
        usuarios = load_user()

        if cpf in usuarios and usuarios[cpf]['senha'] == senha and usuarios[cpf]['funcao'] == 'docente':
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
        senha = request.form['senha']

        usuarios = load_user()
        funcoes_permitidas = ['sm', 'po', 'dt']

        if cpf in usuarios and usuarios[cpf]['senha'] == senha and usuarios[cpf]['funcao'] in funcoes_permitidas:
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
        funcao = request.form['funcao']

        try:
            with open(caminho_usuarios,'r') as u:
                usuarios = json.load(u)
        except FileNotFoundError:
            usuarios = {}

        if cpf in usuarios:
            flash('CPF já cadastrado!', 'error')
            return redirect('/cadastro')
        
        usuarios[cpf] = {
            'nome': nome,
            'email': email,
            'senha': senha,
            'funcao': funcao
        }

        save_user(usuarios)
        return cadastroconcluido()



    return render_template('cadastro.html') 
   
@app.route('/autenticar')
def cadastroconcluido():
    return render_template('autenticar.html')
   

@app.route('/home/aluno')
def homestudent():
    if 'usuario_logado' not in session or session.get('funcao') != 'aluno':
        flash('Você precisa estar logado pra acessar essa página!', 'error')
        return redirect(url_for('login_aluno'))
    primeiro_nome = get_primeiro_nome()   
    return render_template('home_student.html', nome=primeiro_nome)

@app.route("/home/aluno/enviar")
def upload_form():
    return render_template('upload_certificates.html')

@app.route("/home/aluno/gerenciar_atestados/", methods=["GET"])
def listar_atestados_alunos():
    filtro = request.args.get('filtro')
    if filtro == 'nome':
        atestados.sort(key=lambda x: x['Nome'].lower())
    elif filtro == 'data':
        atestados.sort(key=lambda x: x['Inicio']) 
    elif filtro == 'status':
        atestados.sort(key=lambda x: 0 if x['Status'] == "Pendente" else 1 if x['Status'] == True else 2)
    pesquisa = request.args.get('pesquisa', '').lower()
    atestados_filtrados = []
    for atestado in atestados:
        if (pesquisa in str(atestado["Nome"]).lower() or
            pesquisa in str(atestado["Turma"]).lower() or
            pesquisa in str(atestado["RA"]).lower() or
            pesquisa in str(atestado["Tipo"]).lower() or
            pesquisa in str(atestado["Inicio"]).lower()):
            atestados_filtrados.append(atestado) 
    return render_template('gerenciamento_de_atestados_aluno.html', atestados = atestados_filtrados)

@app.route('/home/aluno/gerenciar_atestados/<int:atestado_id>', methods=["POST"])
def excluir_atestado_aluno(atestado_id):
    atestado_para_remover = None
    for atestado in atestados:
        if atestado["ID"] == atestado_id:
            atestado_para_remover = atestado
            break
    if atestado_para_remover:
        atestados.remove(atestado_para_remover)
    return render_template('gerenciamento_de_atestados_aluno.html', atestados=atestados)


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if "file" not in request.files:
            return"Nenhum arquivo selecionado",400
        
        file = request.files["file"]
        
        if file.filename == "":
            return "Nenhum arquivo selecionado", 400

        nome = request.form['nome']
        ra = request.form['ra']
        turma = request.form['turma']
        tipo = request.form['tipo']
        data = request.form['data']
        periodo = request.form['periodo']
        crm = request.form['crm']
        filename = file.filename
        
        if file and file.filename.lower().endswith(".pdf"):
            diaupload = time.strftime("%d%m%Y_%H%M%S")
            filename = (f'{ra}_{diaupload}.pdf')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            

            try:
                with open(caminho_atestados,'r') as u:
                    atestados = json.load(u)
            except FileNotFoundError:
                atestados = {}

            atestados[nome] = {
                'RA' : ra,
                'Turma' : turma,
                'Tipo de Atestado' : tipo,
                'Data' : data,
                'Periodo' : periodo,
                'CRM' : crm,
                'Nome do arquivo' : filename
            }
            save_atestados(atestados)

            return render_template("confirm_upload.html")     

        return "Formato de arquivo inválido.Apenas PDFs são permitidos",400
    
@app.route('/home/docente')
def homedocente():
    if 'usuario_logado' not in session or session.get('funcao') != 'docente':
        flash('Você precisa estar logado para acessar essa página!', 'error')
        return redirect(url_for('login_docente'))
    primeiro_nome = get_primeiro_nome()
    return render_template('home_docente.html', nome=primeiro_nome)

@app.route('/home/docente/gerenciar_atestados/', methods=["GET"])
def listar_atestados_docente():
    filtro = request.args.get('filtro')
    if filtro == 'nome':
        atestados.sort(key=lambda x: x['Nome'].lower())
    elif filtro == 'data':
        atestados.sort(key=lambda x: x['Inicio']) 
    elif filtro == 'status':
        atestados.sort(key=lambda x: 0 if x['Status'] == "Pendente" else 1 if x['Status'] == True else 2)
    pesquisa = request.args.get('pesquisa', '').lower()
    atestados_filtrados = []
    for atestado in atestados:
        if (pesquisa in str(atestado["Nome"]).lower() or
            pesquisa in str(atestado["Turma"]).lower() or
            pesquisa in str(atestado["RA"]).lower() or
            pesquisa in str(atestado["Tipo"]).lower() or
            pesquisa in str(atestado["Inicio"]).lower()):
            atestados_filtrados.append(atestado) 
    return render_template('gerenciamento_de_atestados_docente.html', atestados = atestados_filtrados)

@app.route('/home/docente/gerenciar_atestados/<int:atestado_id>', methods=["POST"])
def excluir_atestado_docente(atestado_id):
    atestado_para_remover = None
    for atestado in atestados:
        if atestado["ID"] == atestado_id:
            atestado_para_remover = atestado
            break
    if atestado_para_remover:
        atestados.remove(atestado_para_remover)
    return render_template('gerenciamento_de_atestados_docente.html', atestados=atestados)

@app.route('/home/docente/estatisticas')
def estatisticas_afastamento():
    return render_template('estatisticas_afastamento.html')

@app.route('/home/membro')
def homemembro():
    if 'usuario_logado' not in session or session.get('funcao') not in ['sm', 'po', 'dt']:
        flash('Você precisa estar logado para acessar essa página!', 'error')
        return redirect(url_for('login_membro'))
    primeiro_nome = get_primeiro_nome()
    user_type = session.get('funcao')
    return render_template('homeMaster.html', nome=primeiro_nome, user_type=user_type)

@app.route('/home/membro/avaliar')
def avaliarmembro():
    return render_template('avaliar_membro.html')

@app.route('/save_data', methods=['POST'])
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
def confirm_evaluation():
    return render_template('confirm_evaluation.html')


@app.route('/home/membro/burndown')
def burndown():
    return render_template('BurndownChart.html')

@app.route('/home/master/registroscrum', methods=['GET','POST'])
def registroscrum():
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
            return redirect(url_for('registroscrum'))

        usuarios[cpf] = {
            'nome': nome,
            'email': email,
            'senha' : senha,
            'funcao' : funcao
        }
        save_user(usuarios)
        return cadastroconcluido()
    
    return render_template('cadastro_membro.html')

@app.route('/home/membro/gerenciar')
def gerenciaravaliacoes():
    return render_template('comparacao_sprint.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso.', 'success')
    return redirect('/')

