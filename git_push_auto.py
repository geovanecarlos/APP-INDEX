import os
import shutil
import subprocess
import datetime

# Caminho do projeto
projeto = "/home/nathan/DAS/APP-INDEX"
os.chdir(projeto)

# Caminhos
origem = "/home/nathan/DAS/Indices"
destino = os.path.join(projeto, "dataset")

# Cria pasta destino se não existir
if not os.path.exists(destino):
    os.makedirs(destino)

# Copia conteúdo da pasta
for item in os.listdir(origem):
    origem_item = os.path.join(origem, item)
    destino_item = os.path.join(destino, item)

    if os.path.isdir(origem_item):
        if os.path.exists(destino_item):
            shutil.rmtree(destino_item)
        shutil.copytree(origem_item, destino_item)
    else:
        shutil.copy2(origem_item, destino_item)

print("✅ Dados copiados de 'Indices' para 'dataset'.")

# Executa comandos shell
def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

# Verifica alterações no repositório
status, _, _ = run("git status --porcelain")
if status:
    msg = f"commit realizado em: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    run("git add .")
    run(f'git commit -m "{msg}"')
    _, stderr, code = run("git push origin main")
    if code == 0:
        print("✅ Push realizado com sucesso!")
    else:
        print("❌ Erro ao realizar o push:")
        print(stderr)
else:
    print("ℹ️ Nenhuma alteração detectada.")
