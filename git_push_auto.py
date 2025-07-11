import os
import subprocess
import datetime

# ✅ Força a execução no diretório certo (garante que o Git use a URL correta)
os.chdir("/home/nathan/DAS/APP-INDEX")

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

# Verifica se há alterações
status, _ = run("git status --porcelain")
if status:
    mensagem = f"Atualização em: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    run("git add .")
    run(f'git commit -m \"{mensagem}\"')
    _, push_code = run("git push origin main")
    if push_code == 0:
        print("Push realizado com sucesso!")
    else:
        print("Erro ao realizar o push.")
else:
    print("Nenhuma alteração detectada. Nada a fazer.")