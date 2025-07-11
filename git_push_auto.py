import os
import datetime

# Mensagem de commit com data e hora
mensagem = f"Atualização em: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# Comandos Git
os.system("git add .")
os.system(f'git commit -m "{mensagem}"')
os.system("git push origin main")

# Verifica se o push foi bem-sucedido
if os.system("git push origin main") == 0:
    print("Push realizado com sucesso!")
else:
    print("Erro ao realizar o push. Verifique se há conflitos ou problemas de autenticação.")
# Verifica se o repositório remoto está atualizado
os.system("git fetch origin")
os.system("git status")
# Verifica o status do repositório
status = os.popen("git status").read()
if "nothing to commit, working tree clean" in status:
    print("O repositório está atualizado.")
else:
    print("Há alterações pendentes no repositório. Por favor, resolva antes de continuar.")
# Verifica se o repositório remoto está acessível
try:
    os.system("git ls-remote origin")
    print("O repositório remoto está acessível.")
except Exception as e:
    print(f"Erro ao acessar o repositório remoto: {e}")