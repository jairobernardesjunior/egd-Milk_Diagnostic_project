Milk Diagnostic é um projeto que vai receber os sms gerados a partir de um dispositivo físico que mede
a temperatura do leite no reservatório da fazenda, 24 horas por dia e 7 dias da semana, verifica se a variação da mesma está dentro dos padrões normais e envia o resultado, através de sms, para a caixa 
de mensagem e para o gmail receptor, sendo o valor dos índices, capturados por uma aplicação python,
rodando em AWS Lambda, transformando os dados e armazenando em AWS BucketS3 como arquivo json.