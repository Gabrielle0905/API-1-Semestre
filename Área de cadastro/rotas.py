from flask import Flask,render_template


#inicializacao
app = Flask(__name__)   
app.config['Secret_key'] = "minha-palavra-secreta"
#rotas
@app.route("/Aluno")
def Aluno():
    return  render_template("Aluno.html")

@app.route("/Autenticar")
def autenticar():
    return render_template("Autenticar.html")   

@app.route("/Docente")
def Docente():
    return render_template("Docente.html")

@app.route("/Autenticar2")
def autenticar2():
    return render_template("Autenticar_docente.html")

#execucao
app.run(debug=True)

    