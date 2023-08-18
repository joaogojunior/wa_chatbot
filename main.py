# implemantação em parte baseada em post de @jonathanferreiras
# https://medium.com/@jonathanferreiras/chatbot-python-whatsapp-e9c1079da5a

import time
import os
from chatbot_utils import ChatBotBr
from whatsweb_utils import WhatsWebScraper

# cria diretorio de profile caso nao exista
if not os.path.isdir("./profile"):
    os.mkdir("profile")

# inicializamos o bot passando o nome do mesmo e dados de treino opcionais.
nome_bot = 'Aki Sushi Bar'
train = not os.path.isfile("./db.sqlite3")
bot = ChatBotBr(nome_bot, train)
wa_driver = WhatsWebScraper(nome_bot)

# abre um conversa ou grupo para escutar e enviar mensagens
wa_driver.abre_conversa_contato('TESTE BOT')

# setamos a váriável último texto vazio
ultima_msg_respondida_tupla = ('', '', '', 0)


try:
    last_count = 0
    while True:
        inicio = time.time()
        print("------------------------------------")
        total_msgs = len(wa_driver.get_list_elements_from_xpath(WhatsWebScraper.TODAS_MSGS_CONVERSA))
        # if total_msgs > 0:
        #     print('total conversas:', total_msgs)
        # obtendo mensagens não lidas
        total_msgs_novas, qtd_conversas_novas = wa_driver.get_qtd_mensagens_nao_lidas()
        if total_msgs_novas > 0:
            print("qtd msg nao lidas", total_msgs_novas, "qtd conversas nao respondidas", qtd_conversas_novas)
            for n_msgs, hora_msg, ultima_msg, autor_msg in wa_driver.gen_tuplas_mensagens_nao_lidas():
                print(n_msgs, "-", hora_msg, "-", ultima_msg, "-", autor_msg)

        # obtendo ultima msg na conversa aberta
        # print("Pegando ultima mensangem conversa...")
        nova_mensagem_tupla = wa_driver.ultima_mensagem_conversa()
        tempo, autor, texto, index = nova_mensagem_tupla
        # garante que a ultima msg ainda nao foi respondida e evita processar msg vazias
        if nova_mensagem_tupla != ultima_msg_respondida_tupla and nova_mensagem_tupla != ('', '', '', 0):
            ultima_msg_respondida_tupla = nova_mensagem_tupla
            print("processando resposta:", texto)
            texto = texto.lower()
            if texto == "envia foto":
                wa_driver.envia_fotos("Nossas ofertas de hoje!")
                # pass
            else:
                # obtem resposta do modelo
                resposta = bot.responde(texto)
                # envia resposta na conversa aberta
                wa_driver.envia_msg_conversa(resposta)
        # else:
        #     print("nao entrou no if!", ultima_msg_respondida_tupla)
        # mostra quantidade de exceptions ja tratados
        cur_count = wa_driver.get_exceptions_counter()
        # if cur_count - last_count > 0:
        #     last_count = cur_count
        print("Num exceptions", cur_count)
        if wa_driver.ultima_resposta_enviada is not None:
            print("ultima resposta enviada", wa_driver.ultima_resposta_enviada)
        if nova_mensagem_tupla != ('', '', '', 0):
            print("ultima msg de contato", nova_mensagem_tupla)
        # calcula e mostra tempo trancorrido na iteração do loop
        print("tempo loop", time.time() - inicio)
except KeyboardInterrupt:
    print("Saindo...")
