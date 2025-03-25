from flask import Flask, render_template, request
app=Flask(__name__)
def salvar_membro(nome, cpf, email, senha, funcao):
    with open('membros.txt', 'a') as arquivo:
        arquivo.write(f'{nome}, {cpf}, {email}, {senha}, {funcao}\n')
@app.route('/', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome=request.form['nome']
        cpf=request.form['cpf']
        email=request.form['email']
        senha=request.form['senha']
        funcao=request.form['funcao']
        salvar_membro(nome, cpf, email, senha, funcao)
    return render_template('registrar_membroscrum.html')
if __name__ == '__main__':
    app.run(debug=True)
