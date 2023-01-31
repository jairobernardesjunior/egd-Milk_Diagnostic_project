# https://youtu.be/K21BSZPFIjQ
"""
Extraia e-mails selecionados da sua conta do Gmail
1. Certifique-se de ativar o IMAP nas configurações do Gmail
(Faça login na sua conta do Gmail e vá para Configurações, Ver todas as configurações e selecione
 Guia Encaminhamento e POP/IMAP. Na seção "Acesso IMAP", selecione Ativar IMAP.)
2. Se você tiver autenticação de dois fatores, o Gmail exige que você crie um aplicativo
senha específica que você precisa usar.
Vá para as configurações da sua conta do Google e clique em 'Segurança'.
Role para baixo até App Passwords em verificação em duas etapas.
Selecione Mail em Selecionar aplicativo. e Outro em Selecionar dispositivo. (Dê um nome, por exemplo, python)
O sistema fornece uma senha que você precisa usar para autenticar no python.
"""

import imaplib
import email
import yaml 
import strip
import datetime
import pandas as pd
from fc import fc_upload_s3 as ups3

def grava_sobes3_arquivo_json_lapidado(
        dirAux, nome_arquivo, df, s3_dados_processed, access_key, secret_key, regiao):

    nome_arquivo = nome_arquivo + '.json'
    pathJson = dirAux + '/' + nome_arquivo

    df.to_json(pathJson)

    # ******************** CARREGA ARQUIVO json NO BUCKET S3
    retorno = ups3.upload_s3(
            s3_dados_processed, nome_arquivo, pathJson, access_key, secret_key, regiao)

    if retorno != True:
        print(retorno)
        print('bucket s3 => ' + s3_dados_processed + ' arquivo => ' + nome_arquivo + 
                ' --- ' + retorno + ' ***** não foi carregado')    

    return retorno

def lambda_handler(event, context):
# ******************** INÍCIO

# parâmetros em arquivo de credenciais
    with open("credentials.yml") as f:
        content = f.read()
        
    my_credentials = yaml.load(content, Loader=yaml.FullLoader)

    # separa parâmetros em suas variáveis
    user, password = my_credentials["user"], my_credentials["password"]
    access_key, secret_key = my_credentials["access_key"], my_credentials["secret_key"]
    region, s3_dados_processed = my_credentials["region"], my_credentials["mk-s3-milk-json"]
    imap_url, dirAux = my_credentials["url_imap"], my_credentials["dirAux"]

    # conecta gmail
    my_mail = imaplib.IMAP4_SSL(imap_url)

    # loga usuário
    my_mail.login(user, password)

    # Seleciona as mensagens
    my_mail.select('Inbox')

    # filtra email com chave e valor
    key = 'FROM'
    value = 'jairobernardesjunior@gmail.com'
    _, data = my_mail.search(None, key, value)  #Search for emails with specific key and value
    status, search_data = my_mail.search(None, 'ALL')

    mail_id_list = data[0].split()
    msgs = []

    # carrega msgs
    for num in mail_id_list:
        typ, data = my_mail.fetch(num, '(RFC822)') #RFC822 returns whole message (BODY fetches just body)
        msgs.append(data)

    # Separa campos do email e monta documento json
    cod_produtor=[]
    data=[]
    tmax=[]
    tmin=[]
    var=[]

    i=0
    for msg in msgs[::-1]:
        for response_part in msg:
            if type(response_part) is tuple:
                my_msg=email.message_from_bytes((response_part[1]))
                #print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                #print ("subj:", my_msg['subject'])
                #print ("from:", my_msg['from'])   

                for part in my_msg.walk():  
                    if part.get_content_type() == 'text/plain':
                        body = part.get_payload()[0:160]
                        body = body.replace('\r\n', '')

                        if body[0:2] == '!@':
                            i=i+1
                            cod_produtor.append(body[2:8])
                            data.append(body[8:16])
                            pini=16

                            #print('...........................................')
                            #print(body[2:8])
                            #print(body[8:16])

                            tmax.append(body[pini:pini+3])
                            tmin.append(body[pini+3:pini+6])
                            var.append(body[pini+6:pini+9])

                if i>0:
                    df=pd.DataFrame({
                            "cod_produtor":cod_produtor,
                            "data":data,
                            "tmax":tmax,
                            "tmin":tmin,
                            "var":var,
                            })

                    nome_arquivo = 'milk_' + str(datetime.datetime.now())
                    nome_arquivo = nome_arquivo.replace(' ', '_')
                    nome_arquivo = nome_arquivo.replace(':', '')
                    nome_arquivo = nome_arquivo.replace('.', '_')
                    retorno = grava_sobes3_arquivo_json_lapidado(
                                dirAux, nome_arquivo, df, s3_dados_processed, 
                                access_key, secret_key, region)

                    if retorno == True:
                        mail_ids = []

                        for block in search_data:
                            mail_ids += block.split()

                        # definindo o range da operação
                        start = mail_ids[0].decode()
                        end = mail_ids[-1].decode()

                        # movendo os emails para a lixeira
                        # este passo é específico do gmail
                        # que não permite a exclusão direta
                        my_mail.store(f'{start}:{end}'.encode(), '+X-GM-LABELS', '\\Trash')                    

                else:
                    print("+++++ Email sem dados")
                    print (my_msg)                

lambda_handler(1, 1)                            