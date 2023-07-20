import time
import os
from chatbot_utils import ChatBotBr
from whatsweb_utils import WhatsWebScraper

#cria diretorio de profile caso nao exista
if not os.path.isdir("./profile"):
    os.mkdir("profile")

#Setamos nosso bot passando o nome do mesmo.
nome_bot = 'Aki Sushi Bar'
bot = ChatBotBr(nome_bot, 'dados_treino')

wa_driver = WhatsWebScraper(nome_bot)
# Iniciamos o bot informando o grupo/pessoa que vamos conversar.
wa_driver.abre_conversa_contato('TESTE BOT')
# wa_driver.fecha_conversa()
#Setamos nossa saudação a entrar no grupo com duas frases em uma lista.
# wa_driver.saudacao_conversa(['Bot: Oi sou um bot e entrei no grupo!', 'Bot: Use :: no início para falar comigo!'])

#Setamos a váriável último texto sem nada.
ultima_msg_tupla = ('', '', '')


try:
    while True:
        inicio = time.time()
        # pass
        print("------------------------------------")
        wa_driver.get_qtd_mensagens_nao_lidas()
        for n_msgs, hora_msg, ultima_msg, autor_msg in wa_driver.gen_contatos_mensagens_nao_lidas():
            print(n_msgs, "-", hora_msg, "-", ultima_msg, "-", autor_msg)

        #Usamos o método de escuta que irá setar na variável texto.
        print("Pegando ultima mensangem conversa...")
        ultima_msg_conversa = wa_driver.ultima_mensagem_conversa()
        tempo, autor, texto = ultima_msg_conversa
        # print(texto, ultimo_texto)
        # print(texto != ultimo_texto, re.match(r'^::', texto))
        #Agora validamos se o texto enviado no grupo/pessoa é o mesmo que o último já lido.
        #Essa validação serve para que o bot não fique respondendo o mesmo texto sempre.
        #Validamos também se no texto possuí o comando :: no início para que ele responda.
        if ultima_msg_conversa != ultima_msg_tupla and ultima_msg_conversa != ('', '', ''):
        #Passando na validação setamos o texto como último texto.
            ultima_msg_tupla = ultima_msg_conversa
            print("entrou no if", texto)
        #Retiramos nosso comando de ativar do bot da string.
            # texto = texto.replace('::', '')
        #Tratamos para deixar o texto em caracteres minúsculos.
            texto = texto.lower()
            # print(texto)
        #Enviamos para o método responde que irá responder no grupo/pessoa.
            resposta = bot.responde(texto)
            wa_driver.envia_msg_conversa(resposta)
        else:
            print("nao entrou no if!", ultima_msg_tupla)
        print("Num exceptions", wa_driver.get_exceptions_counter())
        print("tempo loop", time.time() - inicio)
except KeyboardInterrupt:
    print("Saindo...")
