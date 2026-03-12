import src.qrcode as qrcode
import os

pessoas = ["aluno01", "aluno02", "professor01", "aluno03", "aluno04"]

os.makedirs("qrcodes", exist_ok=True)

for pessoa in pessoas:
    img = qrcode.make(pessoa)
    img.save(f"qrcodes/{pessoa}.png") # salva a imagem em qrcode
    print(f"QR code gerado com sucesso: {pessoa}.png")