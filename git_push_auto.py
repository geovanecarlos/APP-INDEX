import os
import shutil
import subprocess
import datetime

# 📁 Define o diretório raiz do projeto
projeto = "/home/nathan/DAS/APP-INDEX"
os.chdir(projeto)

# 📂 Caminhos de origem e destino
origem = "/home/nathan/DAS/Indices"
destino = os.path.join(projeto, "dataset")

# 🔧 Cria a pasta 'dataset' se ela não existir
if not os.path.exists(destino):
    os.makedirs(destino)

# 📦 Copia os arquivos da pasta 'Indices' para 'dataset'
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
    return result.stdout.strip(), result.stderr.strip(), result.returncode

# 📌 Verifica se há modificações no repositório
status, _, _ = run("git status")
if status:
    mensagem = f"commit realizado em: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    run("git add .")
    run(f'git commit -m "{mensagem}"')

    # 🔄 Faz pull antes do push para evitar conflitos com o repositório remoto
    print("🔄 Executando git pull --rebase...")
    _, pull_err, pull_code = run("git pull --rebase origin main")

    if pull_code != 0:
        print("❌ Erro ao realizar o git pull:")
        print(pull_err)
    else:
        print("✅ Pull realizado com sucesso.")

        # 🚀 Tenta realizar o push
        print("🚀 Executando git push...")
        _, push_err, push_code = run("git push origin main")
        if push_code == 0:
            print("✅ Push realizado com sucesso!")
        else:
            print("❌ Erro ao realizar o push:")
            print(push_err)
else:
    print("ℹ️ Nenhuma alteração detectada. Nada a fazer.")