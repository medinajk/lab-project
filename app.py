import paho.mqtt.client as mqtt
import pandas as pd
from datetime import datetime
import json
import os

BROKER = "localhost"
TOPIC_ENTRADA = "laboratorio/entrada"
TOPIC_SAIDA = "laboratorio/saida"
CSV_PATH = "dados/registro.csv" # caminho do arquivo onde os dados serão salvos

insideLab = {} # Quando alguém entrar, adicionamos essa pessoa aqui. Quando sair, removemos.

pessoa = None, tipo = None, now = None, tempoEstadia = None

def salvaRegistro(pessoa, tipo, entrada=None): # tipo do evento: entrada ou saida
    now = datetime.now()

    if tipo == "entrada":
        insideLab[pessoa] = now # adiciona a pessoa a insideLab com o horário de entrada
        tempoEstadia = None # none porque a pessoa acabou de entrar
    else: 
        if pessoa in insideLab:
            tempoEstadia = (now - insideLab[pessoa]).total_seconds() / 60 # horário de saída - horário de entrada, convertido para minutos
            del insideLab[pessoa] # remove a pessoa de insideLab, porque ela saiu
        else:
            tempoEstadia = None  

novo = pd.DataFrame([{ # cria uma tabela com os dados
        "pessoa": pessoa,
        "tipo": tipo,
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "data": now.strftime("%Y-%m-%d"),
        "hora": now.strftime("%H:%M"),
        "tempo_estadia_min": tempoEstadia
    }])            

if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
    df = pd.concat([df, novo], ignore_index=True)
else:
    df = novo    

df.to_csv(CSV_PATH, index=False) # salva a tabela no arquivo CSV
print(f"Registro salvo: {pessoa} - {tipo} - {now.strftime('%Y-%m-%d %H:%M:%S')} - Tempo de estadia: {tempoEstadia} minutos")

def onMessage(client, userdata, msg):
    payload = json.loads(msg.payload.decode()) # a message chega como bytes, decodificamos e transformamos em json para acessar o id da pessoa
    pessoa = payload.get("id")

    if msg.topic == TOPIC_ENTRADA:
        salvaRegistro(pessoa, "entrada")
    elif msg.topic == TOPIC_SAIDA:
        salvaRegistro(pessoa, "saida")    

client = mqtt.Client()
client.on_message = onMessage
client.connect(BROKER, 1883)
# permite que o sistema receba apenas o que interessa pra ele (entrada e saída)
client.subscribe(TOPIC_ENTRADA)
client.subscribe(TOPIC_SAIDA)

print("escaneando QR codes...")
client.loop_forever()        