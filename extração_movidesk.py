from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import re

print("🚀 Iniciando o WebDriver...")
options = webdriver.ChromeOptions()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

print("🌐 Acessando a página do Movidesk...")
driver.get("https://grupocasamagalhaes.movidesk.com/kb/form/7426/#")

print("⏳ Esperando o campo 'Serviço' aparecer...")
espera = WebDriverWait(driver, 15)
dropdown_div = espera.until(
    EC.element_to_be_clickable((By.XPATH, "//div[contains(@id,'jqxWidget') and contains(@class,'jqx-widget')]"))
)

print("🖱️ Clicando no campo 'Serviço'...")
dropdown_div.click()
time.sleep(3)

print("\n🧠 AGORA É COM VOCÊ:")
print("➡️ Expanda todos os grupos no navegador (níveis 1, 2, 3 e 4).")
input("⏸️ Pressione ENTER aqui quando tudo estiver expandido...")

# Coletar os itens da árvore
print("🔍 Coletando itens visíveis...")
itens = driver.find_elements(By.CLASS_NAME, "jqx-tree-item-li")

caminho = ["", "", "", ""]
numeracao = ["", "", "", ""]
dados = []

# Contadores de cada nível
nivel1 = nivel2 = nivel3 = nivel4 = 0

for item in itens:
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", item)
        time.sleep(0.05)

        estilo = item.get_attribute("style")
        match = re.search(r"margin-left:\s*(\d+)px", estilo)
        if not match:
            continue

        margin = int(match.group(1))
        nivel = margin // 18

        div_texto = item.find_element(By.CLASS_NAME, "jqx-tree-item")
        texto = div_texto.get_attribute("innerText").strip()

        if not texto:
            continue

        # Atualiza caminho e reset de níveis abaixo
        caminho[nivel] = texto
        for i in range(nivel + 1, 4):
            caminho[i] = ""

        # Numeração
        if nivel == 0:
            nivel1 += 1
            nivel2 = nivel3 = nivel4 = 0
        elif nivel == 1:
            nivel2 += 1
            nivel3 = nivel4 = 0
        elif nivel == 2:
            nivel3 += 1
            nivel4 = 0
        elif nivel == 3:
            nivel4 += 1

        # Gerar código hierárquico
        if nivel == 0:
            cod = f"{nivel1}"
        elif nivel == 1:
            cod = f"{nivel1}.{nivel2}"
        elif nivel == 2:
            cod = f"{nivel1}.{nivel2}.{nivel3}"
        elif nivel == 3:
            cod = f"{nivel1}.{nivel2}.{nivel3}.{nivel4}"
        else:
            cod = ""

        print(f"{cod} -", " > ".join([c for c in caminho if c]))
        dados.append([cod] + caminho)

    except Exception as e:
        print(f"⚠️ Erro ao processar item: {e}")

# Salvar CSV
print("\n💾 Salvando em 'servicos_hierarquia.csv'...")
with open("servicos_hierarquia.csv", "w", newline="", encoding="utf-8") as arquivo:
    writer = csv.writer(arquivo)
    writer.writerow(["Código", "Nível 1", "Nível 2", "Nível 3", "Nível 4"])
    writer.writerows(dados)

print(f"\n✅ Finalizado! Total extraído: {len(dados)} registros")
driver.quit()
