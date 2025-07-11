import os
import datetime

# Mensagem de commit com data e hora
mensagem = f"Atualização automática em {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# Comandos Git
os.system("git add .")
os.system(f'git commit -m "{mensagem}"')
os.system("git push origin main")