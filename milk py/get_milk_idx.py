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

# Importing libraries
import imaplib
import email

import yaml  #To load saved login credentials from a yaml file

with open("credentials.yml") as f:
    content = f.read()
    
# from credentials.yml import user name and password
my_credentials = yaml.load(content, Loader=yaml.FullLoader)

#Load the user name and passwd from yaml file
user, password = my_credentials["user"], my_credentials["password"]

#URL for IMAP connection
imap_url = 'imap.gmail.com'

# Connection with GMAIL using SSL
my_mail = imaplib.IMAP4_SSL(imap_url)

# Log in using your credentials
my_mail.login(user, password)

# Select the Inbox to fetch messages
my_mail.select('Inbox')

#Define Key and Value for email search
#For other keys (criteria): https://gist.github.com/martinrusev/6121028#file-imap-search
key = 'FROM'
value = 'jairobernardesjunior@gmail.com'
_, data = my_mail.search(None, key, value)  #Search for emails with specific key and value

mail_id_list = data[0].split()  #IDs of all emails that we want to fetch 

msgs = [] # empty list to capture all messages
#Iterate through messages and extract data into the msgs list
for num in mail_id_list:
    typ, data = my_mail.fetch(num, '(RFC822)') #RFC822 returns whole message (BODY fetches just body)
    msgs.append(data)

#Agora temos todas as mensagens, mas com muitos detalhes
#Vamos extrair o texto certo e imprimir na tela

#Em um e-mail com várias partes, email.message.Message.get_payload() retorna um
# lista com um item para cada peça. A maneira mais fácil é passar a mensagem
# e obtenha o payload de cada parte:
# https://stackoverflow.com/questions/1463074/how-can-i-get-an-email-messages-text-content-using-python

# OBSERVE que um objeto Message consiste em cabeçalhos e cargas úteis.

for msg in msgs[::-1]:
    for response_part in msg:
        if type(response_part) is tuple:
            my_msg=email.message_from_bytes((response_part[1]))
            print("_________________________________________")
            print ("subj:", my_msg['subject'])
            print ("from:", my_msg['from'])
            print ("body:")
            for part in my_msg.walk():  
                #print(part.get_content_type())
                if part.get_content_type() == 'text/plain':
                    print (part.get_payload())