import os
import shutil
import subprocess
import datetime

# 🏁 Define o diretório raiz do do projeto
os.chdir("/home/nathan/DAS/APP-INDEX")

# 📁 Caminhos de origem e destino dos dados
origem = "/home/nathan/DAS/Indices"
destino = "/home/nathan/DAS/APP-INDEX/dataset"

# 🔧 Cria a pasta 'dataset' se ela não existir
if not os.path.exists(destino):
    os.makedirs(destino)

# 📂 Copia os arquivos da pasta 'Indices' para 'dataset'
for item in os.listdir(origem):
    origem_item = os.path.join(origem, item)
    destino_item = os.path.join(destino, item)

    if os.path.isdir(origem_item):
        if os.path.exists(destino_item):
            shutil.rmtree(destino_item)
        shutil.copytree(origem_item, destino_item)
    else:
        shutil.copy2(origem_item, destino_item)

print("✅ Dados copiados de 'Indices' para 'dataset' com sucesso.")

# ⚙️ Função para executar comandos shell
def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

# 📌 Verifica se há modificações no repositório
status, _ = run("git status --porcelain")
if status:
    mensagem = f"commit realizado em: {datetime.datetime.now().strftime('%Y-%m-%d')}"
    run("git add .")
    run(f'git commit -m "{mensagem}"')
    _, push_code = run("git push origin main")
    if push_code == 0:
        print("✅ Push realizado com sucesso!")
    else:
        print("❌Erro ao realizar o push.")
else:
    print("ℹ️  Nenhuma alteração detectada. Nada a fazer.")
