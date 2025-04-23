from flask import Flask,render_template,url_for,request,flash,redirect
from main import app, UPLOAD_FOLDER, os
from lista_atestados import atestados
import time
import json
import os

@app.route('/')
def homepage():
    return render_template('first_page.html')

@app.route('/login', methods=['POST'])
def redirect_user():
    escolha = request.form.get('user-type')

    if escolha == 'Aluno':
        return render_template('login_aluno.html')

    if escolha == 'Docente':
        return render_template('login_docente.html')

    if escolha == 'Equipe':
        return render_template('login_membro.html')
    
    else:
        flash('Por favor, selecione um tipo de usuário antes de continuar!!', 'error')
        return redirect('/')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        print(request.form)
        nome = request.form.get('Name')
        cpf = request.form.get('CPF')
        email = request.form.get('Email')
        senha = request.form.get('password')
        tipo = request.form.get('funcao')
        
        if not all([nome, cpf, email, senha, tipo]) :
            flash("Por favor, preencha todos os campos.")
            return redirect('/cadastro')
        
        novo_usuario = {
            "nome": nome,
            "cpf": cpf,
            "email": email,
            "senha": senha,
            "tipo": tipo
        }

        try:
            with open('usuarios.json') as usuariosTemp:
                usuarios = json.load(usuariosTemp)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            usuarios = []

        usuarios.append(novo_usuario)

        with open('usuarios.json', 'w', encoding='utf-8') as gravarTemp:
            json.dump(usuarios, gravarTemp, indent=4, ensure_ascii=False)

        print("Usuário salvo:", novo_usuario)

        flash("Usuário cadastrado com sucesso!")
        return render_template('autenticar.html')

    return render_template('cadastro.html')

   
@app.route('/autenticar', methods=['POST'])
def confirm_upload():
   return render_template("autenticar.html")
   

@app.route('/home/aluno', methods=['POST'])
def homestudent():
    return render_template('home_student.html')

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
            

            with open(os.path.join(UPLOAD_FOLDER, 'dados.txt'), 'a') as f:
                f.write(f'Nome: {nome}\nRA: {ra}\nTurma: {turma}\nTipo de Atestado: {tipo}\nData: {data}\nPeríodo de afastamento:{periodo}\nCrum/CFO: {crm}\nArquivo: {filename} \n\n')

            return render_template("confirm_upload.html")     

        return "Formato de arquivo inválido.Apenas PDFs são permitidos",400
    
@app.route('/home/docente')
def homedocente():
    return render_template('home_docente.html')

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


@app.route('/home/membro')
def homemembro():
    return render_template('homePODevteam.html')

@app.route('/home/master')
def homemaster():
    return render_template('homeMaster.html')

@app.route('/home/membro/avaliar')
def avaliarmembro():
    return render_template('avaliar_membro.html')

@app.route('/home/master/burndown')
def burndown():
    return render_template('BurndownChart.html')

@app.route('/home/master/registroscrum')
def registroscrum():
    return render_template('cadastro_membro.html')

@app.route('/home/master/gerenciar')
def gerenciaravaliacoes():
    return render_template('gerenciar_avaliacoes.html')

@app.route('/login_membro', methods = ['POST'])
def login():
    cpf = request.form.get('cpf')
    password = request.form.get('password')

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(BASE_DIR, 'users.json')

    with open(json_path, 'r', encoding='utf-8') as f:
        users = json.load(f)

        cont = 0
        for user in users:
            cont = cont + 1

            if user['cpf'] == cpf and user['password'] == password:
                if user['type'] in ['dev', 'master']:
                    return render_template('homeMaster.html', cpf=cpf, user_type=user['type'])
            
            if cont >= len(users):
                flash('usuario invalido')
                return redirect('/')
