import os
import scraper_utils


class WhatsWebScraper(scraper_utils.Scraper):
    url = 'https://web.whatsapp.com/'
    CHILD_PRE_TEXT = ".//div[@data-pre-plain-text]"
    CAIXA_DE_PESQUISA = "//div[@data-testid='chat-list-search' and @title='Caixa de texto de pesquisa']/p"
    CAIXA_DE_MENSAGEM = "//div[@data-testid='conversation-compose-box-input' and @title='Mensagem']/p"
    BOTAO_ENVIAR_MSG = "//button[@data-testid='compose-btn-send' and @aria-label='Enviar']/span"
    TODAS_MSGS_CONVERSA = "//div[@data-testid='msg-container']"
    TODOS_FRAMES_COM_MSG_NOVAS = '//div[@data-testid="cell-frame-container" and .//span[@data-testid=' \
                                 '"icon-unread-count"]]'
    CHILD_SPAN_QTD_MSG_NOVA = './/span[@data-testid="icon-unread-count"]'
    CHILD_HORA_ENVIADA = './/div[@data-testid="cell-frame-primary-detail"]'
    CHILD_NOME_CONTATO = './/div[@data-testid="cell-frame-title"]'
    CHILD_ULTIMA_MSG = './/span[@data-testid="last-msg-status"]'
    BOTAO_ANEXAR = '//div[@title="Anexar"]'
    CHILD_MSG_DOC = './/div[@data-testid="document-thumb"]'
    MSG_APAGADA = './/span[@data-testid="recalled"]'
    CHILD_MSG_IMG = './/div[@data-testid="image-thumb"]'
    MSG_CARREGANDO = '//div[@data-testid="msg-container" and .//*[@data-testid="media-state-pending"]]'
    TEXT_INPUT_IMGS = "//div[@data-testid='media-caption-input-container']"
    BOTAO_ENVIAR_IMGS = "//span[@data-testid='send']"
    CONVERSA_CONTATO = '//span[@title = "{}"]'

    # emoji_dict static attribute
    _emoji_dict = {"🍣": ":sushi\n", "🛵": ":scooter\n", "😉": ":winking face\n",
                   "😊": ":smiling face with smiling\n", "🙂": ":slightly smiling\n", "🙏": ":folded hand\n",
                   "🥰": ":smiling face with heart\n", "🔑": ":key\n", "😋": ":face savouring delicious\n"}

    def __init__(self, contato_bot):
        self.ultima_resposta_enviada = None
        self.ultima_texto_tupla_cache = ('', '', '', 0)
        self.contato_bot = contato_bot
        super().__init__(self.url, self.CAIXA_DE_PESQUISA, "wpp")

    @staticmethod
    def emoji_code(emoji):
        return WhatsWebScraper._emoji_dict[emoji]

    @staticmethod
    def parse_emoticons_texto(resposta, emoji_code=True):
        while resposta.find("\\") != -1:
            c = resposta.find("\\")
            antes = resposta[:c]
            # parse newline
            if resposta[c:c + 2] == "\\n":
                conv_str = "\n"
                depois = resposta[c + 2:]
            else:
                # parse utf8 escaped char
                utf8_bytes = bytes.fromhex(" ".join(map(lambda x: x[2:], resposta[c:c + 20].split('\\'))))
                depois = resposta[c + 20:]
                if emoji_code:
                    conv_str = WhatsWebScraper.emoji_code(utf8_bytes.decode('utf8'))
                else:
                    conv_str = utf8_bytes.decode('utf8')
            resposta = antes + conv_str + depois
        return resposta

    def get_tempo_autor_post(self, el=None):
        tempo, autor = self.get_child_attribute_by_xpath(WhatsWebScraper.CHILD_PRE_TEXT, "data-pre-plain-text",
                                                         "[data não disponível] nome do contato não disponível  ",
                                                         el).split("]")
        tempo, autor = tempo[1:], autor[1:-2]
        return tempo, autor

    def abre_conversa_contato(self, nome_contato):
        # Selecionamos o elemento da caixa de pesquisa do whats.
        caixa_de_pesquisa = self.espera_por_elemento_xpath_el(WhatsWebScraper.CAIXA_DE_PESQUISA)
        caixa_de_pesquisa.send_keys(nome_contato)
        contato = self.espera_por_elemento_xpath_el(WhatsWebScraper.CONVERSA_CONTATO.format(nome_contato),
                                                    clickable=True)
        contato.click()

    # Nosso método responde irá receber o parâmetro texto que seria o retorno do método escuta.
    def envia_msg_conversa(self, resposta):
        resposta = str(resposta)
        if resposta != self.ultima_resposta_enviada:
            self.ultima_resposta_enviada = resposta
            # Setamos caixa de mensagens preenchemos com a resposta e clicamos em enviar.
            caixa_de_mensagem = self.espera_por_elemento_xpath_el(WhatsWebScraper.CAIXA_DE_MENSAGEM)
            print(resposta)
            resposta = self.parse_emoticons_texto(resposta)
            print(resposta)
            caixa_de_mensagem.send_keys(resposta)
            botao_enviar = self.espera_por_elemento_xpath_el(WhatsWebScraper.BOTAO_ENVIAR_MSG, clickable=True)
            botao_enviar.click()
            if self.ultima_texto_tupla_cache != ('', '', '', 0):
                print("atualizando id cache...")
                self.ultima_texto_tupla_cache = (self.ultima_texto_tupla_cache[0], self.ultima_texto_tupla_cache[1],
                                                 self.ultima_texto_tupla_cache[2], self.ultima_texto_tupla_cache[3] + 1)
        else:
            print("nao envia msg pois a resposta é igual a ultima resposta enviada...")

    def saudacao_conversa(self, frases_iniciais):
        # Validamos se a frase inicial é uma lista.
        if type(frases_iniciais) == list:
            # Realizamos um for para enviar cada mensagem na lista.
            for frase in frases_iniciais:
                self.envia_msg_conversa(frase)

    def gen_todas_mensagens_conversa_texto_tupla(self, inv=False):
        posts = self.get_todas_msg_el_list()
        # gera lista de indexes na ordem correta
        if inv:
            lista = range(len(posts) - 1, -1, -1)
        else:
            lista = range(len(posts))
        # ignora posts que sejam um documento, imagem ou mensagem apagada pq estes nao tem pre-text e ou texto
        for index in lista:
            post = posts[index]
            xpath = './*[' + WhatsWebScraper.CHILD_MSG_DOC + ' or ' + \
                    WhatsWebScraper.MSG_APAGADA + ' or ' + WhatsWebScraper.CHILD_MSG_IMG + ']'
            # if len(self.get_list_elements_from_xpath(WhatsWebScraper.CHILD_MSG_DOC, post)) == 0 and \
            #         len(self.get_list_elements_from_xpath(WhatsWebScraper.MSG_APAGADA, post)) == 0 and \
            #         len(self.get_list_elements_from_xpath(WhatsWebScraper.CHILD_MSG_IMG, post)) == 0:
            if len(self.get_list_elements_from_xpath(xpath, post)) == 0:
                # se for um post com apenas texto
                texto = self.get_sel_text_from_post(post)
                tempo, autor = self.get_tempo_autor_post(post)
                yield tempo, autor, texto, index

    def get_sel_text_from_post(self, post):
        return self.get_child_text_by_css_selector(css_select='span.selectable-text',
                                                   default_texto="mensagem não disponível...", el=post)

    def get_todas_msg_el_list(self):
        return self.get_list_elements_from_xpath(WhatsWebScraper.TODAS_MSGS_CONVERSA)

    # def remover_msgs_contato_lista(self, texto_lista, contato):
    #     print("Filtrando", contato, "da conversa ...")
    #     lista = list(filter(lambda x: x[1] != contato, texto_lista))
    #     print("tam inicial", len(texto_lista), "tam final", len(lista))
    #     return lista

    def ultima_mensagem_conversa(self):
        def for_unpack_gen_todas_msg_tupla(r):
            qtd_msg_bot = 0
            # seta variavel fim de busca a partir da localizacao da ultima msg conhecida no cache
            if self.ultima_texto_tupla_cache != ('', '', '', 0):
                fim_busca = self.ultima_resposta_enviada[3]
            else:
                # -1 aqui significa ate o fim da lista
                fim_busca = -1
            for c, texto_tupla in enumerate(self.gen_todas_mensagens_conversa_texto_tupla(inv=True)):
                if texto_tupla[1] == self.contato_bot:
                    qtd_msg_bot += 1
                # atualiza variavel ultima_resposta da conversa
                if texto_tupla[1] == self.contato_bot and qtd_msg_bot == 1:
                    self.ultima_resposta_enviada = texto_tupla[2]
                # ignora mensagem do proprio bot e mensagens invalidas
                elif texto_tupla[1] != self.contato_bot and texto_tupla[1] != "nome do contato não disponível":
                    r = texto_tupla
                    # quebra o loop por ja ter a tupla com a ultima mensagem que nao foi do nosso bot
                    # ou nao estava indisponivel
                    break
                elif texto_tupla[1] == "nome do contato não disponível" and \
                        texto_tupla[2] == "mensagem não disponível...":
                    print("interrompendo prematuramente por ser nulo...")
                    break
                elif c == fim_busca:
                    # limita busca pelo tamanho maximo de iteracoes
                    print("busca chegou ao tamanho maximo:", fim_busca)
                    break
            return r

        # checa se a mensagem no cache é valida
        # print("func ->", msg_check, "split ->", self.ultima_texto_tupla_cache[:2])
        if self.ultima_texto_tupla_cache != ('', '', '', 0) and \
                self.get_tempo_autor_post(self.get_todas_msg_el_list()[self.ultima_texto_tupla_cache[3]]) == \
                self.ultima_texto_tupla_cache[:2]:
            print("retornando valor cacheado:", self.ultima_texto_tupla_cache)
            return self.ultima_texto_tupla_cache
        else:
            print("cache invalido", self.ultima_texto_tupla_cache)
            ret = for_unpack_gen_todas_msg_tupla(('', '', '', 0))
            self.ultima_texto_tupla_cache = ret
            print("atualizando cache:", ret)
            return ret

    def get_qtd_mensagens_nao_lidas(self):
        frame_container_els = self.get_list_elements_from_xpath(WhatsWebScraper.TODOS_FRAMES_COM_MSG_NOVAS)
        qtd = len(frame_container_els)
        total = 0
        for el in frame_container_els:
            span_text = self.get_child_text_by_xpath(WhatsWebScraper.CHILD_SPAN_QTD_MSG_NOVA, "erro", el)
            # contabiliza total de mensagens nao lidas
            if span_text != "" and span_text != "erro":
                total += int(span_text)
            elif span_text == "erro":
                print("qtd msg nao lidas", total, "qtd conversas nao respondidas", qtd)
                return total, qtd
            # total de conversas com msgs nao lidas
        print("qtd msg nao lidas", total, "qtd conversas nao respondidas", qtd)
        return total, qtd

    def gen_contatos_mensagens_nao_lidas(self):
        frame_cont_cells = self.get_list_elements_from_xpath(WhatsWebScraper.TODOS_FRAMES_COM_MSG_NOVAS)
        for frame_cont_cell in frame_cont_cells:
            qtd_msgs_nao_lidas_cell = self.get_child_text_by_xpath(WhatsWebScraper.CHILD_SPAN_QTD_MSG_NOVA, "0",
                                                                   frame_cont_cell)
            hora_msg_enviada_cell = self.get_child_text_by_xpath(WhatsWebScraper.CHILD_HORA_ENVIADA,
                                                                 "hora não pode ser obtida...", frame_cont_cell)
            nome_contato_cell = self.get_child_text_by_xpath(WhatsWebScraper.CHILD_NOME_CONTATO,
                                                             "nome não pode ser obtido...", frame_cont_cell)
            last_msg_cell = self.get_child_text_by_xpath(WhatsWebScraper.CHILD_ULTIMA_MSG,
                                                         "mensagem não pode ser obtida...", frame_cont_cell)
            yield qtd_msgs_nao_lidas_cell, hora_msg_enviada_cell, last_msg_cell, nome_contato_cell

    # def testes(self):
    # num_celulas_total = self.driver.find_element(By.XPATH, '//*[@id="pane-side"]/div/div/div'). \
    #     get_attribute("aria-rowcount")
    # celulas_paneside = self.driver.find_elements(By.XPATH, "//*[@id='pane-side']/div/div/div/div")
    # celulas_frame_container = self.driver.find_elements(By.XPATH, "//div[@data-testid='cell-frame-container']")
    # # celulas_com_msg_novas = self.driver.find_elements(By.XPATH, "//*[@id='pane-side' and "
    # #                                                             ".//div[@data-testid='icon-unread-count']"
    # #                                                             "]/div/div/div/div")
    # print("total celular paneside", num_celulas_total, "tam paneside", len(celulas_paneside),
    # "tam frame container",
    #       len(celulas_frame_container), "tam frame container msg novas", len(frame_cont_cells))
    # print("tam novas msg conversa", len(frame_cont_cells))/

    def envia_fotos(self, texto="", diretorio="fotos"):
        qtd = 0
        if texto != self.ultima_resposta_enviada:
            anexar = self.espera_por_elemento_xpath_el(WhatsWebScraper.BOTAO_ANEXAR, clickable=True)
            anexar.click()
            diretorio = os.path.join(self.cwd, diretorio)
            for arquivo in os.listdir(diretorio):
                if arquivo.lower().endswith(".jpg"):
                    qtd += 1
                    fp = os.path.join(diretorio, arquivo)
                    print("adicionando", fp)
                    input_box = self.espera_por_elemento_tagname_el("input")
                    input_box.send_keys(fp)
            if texto != "":
                self.espera_por_elemento_xpath_el(WhatsWebScraper.TEXT_INPUT_IMGS).send_keys(texto)
                # atualiza ultima resposta enviada
                self.ultima_resposta_enviada = texto
            self.espera_por_elemento_xpath_el(WhatsWebScraper.BOTAO_ENVIAR_IMGS, clickable=True).click()
            print("enviando imagens...")
            tam = 1
            # esperando todas as msg carregarem
            while tam > 0:
                tam = len(self.get_list_elements_from_xpath(WhatsWebScraper.MSG_CARREGANDO))
                print("Esperando carregar todas msg...", tam)
            if self.ultima_texto_tupla_cache != ('', '', '', 0):
                print("atualizando id cache...")
                self.ultima_texto_tupla_cache = (self.ultima_texto_tupla_cache[0],
                                                 self.ultima_texto_tupla_cache[1],
                                                 self.ultima_texto_tupla_cache[2],
                                                 self.ultima_texto_tupla_cache[3] + qtd)
        else:
            print("nao envia msg pois a resposta é igual a ultima resposta enviada")
