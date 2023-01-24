Milk Diagnostic é um projeto que vai receber os sms gerados a partir de um dispositivo físico que mede
a temperatura do leite no reservatório da fazenda, 24 horas por dia e 7 dias da semana, verifica se a variação da mesma está dentro dos padrões normais e envia o resultado, através de sms, para a caixa 
de mensagem do nro do supervisor, sendo o valor da temperatura, capturada por um aplicativo python,
rodando em AWS EC2, transformando os dados e armazenando em AWS BucketS3 como arquivo json.