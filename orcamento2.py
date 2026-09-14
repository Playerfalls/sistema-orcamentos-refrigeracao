import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
import os, sys, textwrap

# ------------------ CAMINHO RECURSO ------------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

caminho_imagem = resource_path("logo_empresa.png")

# ------------------ DADOS ------------------
servicos = []

EMPRESA = {
    "nome": "Refriclima Refrigeração",
    "cnpj": "52.056.640/0001-17",
    "telefone": "(24) 974026386",
    "email": "Whatsapp:(24) 998324956",
    "endereco": "Av N S do Amparo, 4814 - Santa Rita do Zarur,RJ"
}

# ------------------ FUNÇÕES LISTA ------------------
def atualizar_lista():
    tree.delete(*tree.get_children())
    for i, s in enumerate(servicos):
        tree.insert("", "end", iid=i,
            values=(s["nome"], f"R$ {s['valor']:.2f}", s["data"].strftime("%d/%m/%Y")))

def cadastrar_servico():
    try:
        servicos.append({
            "nome": nome_entry.get(),
            "valor": float(valor_entry.get()),
            "data": datetime.strptime(data_entry.get(), "%d/%m/%Y")
        })
        atualizar_lista()
        nome_entry.delete(0, tk.END)
        valor_entry.delete(0, tk.END)
        data_entry.delete(0, tk.END)
    except:
        messagebox.showerror("Erro", "Dados inválidos")

def excluir_servico():
    item = tree.focus()
    if item:
        servicos.pop(int(item))
        atualizar_lista()

def editar_servico():
    item = tree.focus()
    if not item:
        return
    s = servicos[int(item)]
    nome_entry.insert(0, s["nome"])
    valor_entry.insert(0, s["valor"])
    data_entry.insert(0, s["data"].strftime("%d/%m/%Y"))
    excluir_servico()

# ------------------ PDF  ------------------
def gerar_pdf():

    arquivo = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not arquivo:
        return

    c = canvas.Canvas(arquivo, pagesize=A4)
    largura, altura = A4

    def desenhar_marca_dagua():
        if os.path.exists(caminho_imagem):
            largura_img = 500
            altura_img = 500
            x = (largura - largura_img) / 2
            y = (altura - altura_img) / 2
            c.saveState()
            c.setFillAlpha(0.1)
            c.drawImage(caminho_imagem, x, y,
                width=largura_img, height=altura_img, mask='auto')
            c.restoreState()

    desenhar_marca_dagua()

    if os.path.exists(caminho_imagem):
        c.drawImage(caminho_imagem, 0, altura - 244,
            width=380, height=380, preserveAspectRatio=True)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(370, altura - 40, EMPRESA["nome"])

    c.setFont("Helvetica", 10)
    c.drawString(370, altura - 55, f"CNPJ: {EMPRESA['cnpj']}")
    c.drawString(370, altura - 70, EMPRESA["telefone"] + " | " + EMPRESA["email"])
    c.drawString(370, altura - 85, EMPRESA["endereco"])

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(largura / 2, altura - 120,
        "Relatório de Análise de Valor de Serviços")

    c.setFont("Helvetica", 10)
    c.drawRightString(largura - 40, altura - 140,
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    y = altura - 170
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.whitesmoke)
    c.rect(40, y, largura - 80, 20, fill=True, stroke=False)
    c.setFillColor(colors.black)

    c.drawString(45, y + 5, "Data")
    c.drawString(120, y + 5, "Serviço")
    c.drawString(400, y + 5, "Valor (R$)")
    y -= 25

    c.setFont("Helvetica", 10)
    total = 0

    for s in servicos:
        linhas = textwrap.wrap(s["nome"], 45)
        altura_linha = 14
        bloco = len(linhas) * altura_linha

        if y - bloco < 80:
            c.showPage()
            desenhar_marca_dagua()
            y = altura - 80

        c.drawString(45, y, s["data"].strftime("%d/%m/%Y"))

        y_temp = y
        for linha in linhas:
            c.drawString(120, y_temp, linha)
            y_temp -= altura_linha

        c.drawString(400, y, f"{s['valor']:.2f}")
        y -= bloco + 6
        total += s["valor"]

    y -= 20
    c.setStrokeColor(colors.blue)
    c.line(40, y, largura - 40, y)

    y -= 30
    c.setFont("Helvetica-Bold", 11)
    c.drawString(45, y, f"Total de serviços: {len(servicos)}")
    c.drawString(400, y, f"Total em R$: {total:.2f}")

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(20, 40, EMPRESA["nome"])
    c.drawRightString(largura - 30, 40,
        "Assinatura: _______________________________________________")

    c.save()
    messagebox.showinfo("Sucesso", "PDF gerado com sucesso!")

# ------------------ INTERFACE ------------------
root = tk.Tk()
root.title("Sistema de Orçamentos")
root.geometry("1280x720")
root.configure(bg="#0d2b45")

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
style.configure("Treeview.Heading",
    background="#0d2b45", foreground="white",
    font=("Segoe UI", 10, "bold"))

container = tk.Frame(root, bg="white")
container.place(relx=0.03, rely=0.05, relwidth=0.94, relheight=0.9)

tk.Label(container, text="Cadastro de Serviços",
    font=("Segoe UI", 16, "bold"), bg="white").pack(anchor="w", padx=20, pady=10)

form = tk.Frame(container, bg="white")
form.pack(fill="x", padx=20)

tk.Label(form, text="Descrição", bg="white").grid(row=0, column=0)
nome_entry = tk.Entry(form, width=45)
nome_entry.grid(row=1, column=0, padx=5)

tk.Label(form, text="Valor (R$)", bg="white").grid(row=0, column=1)
valor_entry = tk.Entry(form, width=15)
valor_entry.grid(row=1, column=1, padx=5)

tk.Label(form, text="Data (DD/MM/AAAA)", bg="white").grid(row=0, column=2)
data_entry = tk.Entry(form, width=15)
data_entry.grid(row=1, column=2, padx=5)

tk.Button(form, text="Cadastrar",
    bg="#0d2b45", fg="white",
    command=cadastrar_servico).grid(row=1, column=3, padx=10)

lista_frame = tk.Frame(container)
lista_frame.pack(fill="both", expand=True, padx=20, pady=20)

scroll = ttk.Scrollbar(lista_frame)
scroll.pack(side="right", fill="y")

tree = ttk.Treeview(lista_frame,
    columns=("desc", "valor", "data"),
    show="headings", yscrollcommand=scroll.set)

scroll.config(command=tree.yview)

tree.heading("desc", text="Descrição")
tree.heading("valor", text="Valor")
tree.heading("data", text="Data")

tree.column("desc", width=700)
tree.column("valor", width=120, anchor="center")
tree.column("data", width=120, anchor="center")

tree.pack(fill="both", expand=True)

acoes = tk.Frame(container, bg="white")
acoes.pack(pady=10)

tk.Button(acoes, text="Editar", width=15, command=editar_servico).pack(side="left", padx=5)
tk.Button(acoes, text="Excluir", width=15, command=excluir_servico).pack(side="left", padx=5)
tk.Button(acoes, text="Gerar PDF", width=15,
    bg="#0d2b45", fg="white",
    command=gerar_pdf).pack(side="left", padx=5)

root.mainloop()
