import os

from selenium import webdriver
from selenium.common import StaleElementReferenceException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WhatsWebScraper:
    def __init__(self, contato_bot):
        # Setamos o caminho de nossa aplicação.
        dir_path = os.getcwd()
        # Configuramos um profile no chrome para não precisar logar no whats toda vez que iniciar o bot.
        options = webdriver.ChromeOptions()
        options.add_argument(r"user-data-dir=" + dir_path + "/profile/wpp")
        # Iniciamos o driver.
        service = Service()
        # Setamos onde está nosso chromedriver.
        service.executable_path = dir_path + "/driver"
        self.driver = webdriver.Chrome(service=service, options=options)
        self.contato_bot = contato_bot
        self.timeout = 4
        self.exceptions_count = 0
        self.log_dir = "logs/"
        self.log_file = dir_path + "/" + self.log_dir + "wa_exceptions.log"
        self.abre_whatsapp_chrome()

    def get_exceptions_counter(self):
        return self.exceptions_count

    def set_exception_log_and_inc_count(self, e):
        self.exceptions_count += 1
        if not os.path.isdir("./" + self.log_dir):
            os.mkdir("logs")
        csv = open(self.log_file, "a")
        csv.write(str(e))
        csv.close()

    def espera_por_elemento_xpath_el(self, tempo, xpath):
        wait = WebDriverWait(self.driver, tempo)
        try:
            el = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException as e:
            self.set_exception_log_and_inc_count(e)
            print("Tratando TimeoutException, retornando None...")
            el = None
        return el

    def get_caixa_de_pesquisa_el(self):
        xpath = "//div[@data-testid='chat-list-search' and @title='Caixa de texto de pesquisa']/p"
        return self.espera_por_elemento_xpath_el(self.timeout, xpath)

    def get_contato_lista_el(self, nome_contato):
        xpath = '//span[@title = "{}"]'.format(nome_contato)
        return self.espera_por_elemento_xpath_el(self.timeout, xpath)

    def get_caixa_de_mensagem_el(self):
        xpath = "//div[@data-testid='conversation-compose-box-input' and @title='Mensagem']/p"
        return self.espera_por_elemento_xpath_el(self.timeout, xpath)

    def get_botao_enviar_el(self):
        xpath = "//button[@data-testid='compose-btn-send' and @aria-label='Enviar']/span"
        return self.espera_por_elemento_xpath_el(self.timeout, xpath)

    def get_all_posts_in_group_list(self):
        xpath = "//div[@data-testid='msg-container']"
        self.espera_por_elemento_xpath_el(10, xpath)
        lista = self.driver.find_elements(By.XPATH, xpath)
        # print(lista)
        return lista

    def get_selectable_text(self, el=None, el_index=0):
        texto = "mensagem não disponível..."
        if el is not None:
            try:
                texto = el.find_element(By.CSS_SELECTOR, 'span.selectable-text').text
            except StaleElementReferenceException as e:
                self.set_exception_log_and_inc_count(e)
                print("Stale element found!", el_index + 1, "retornando", texto, "...")
            except NoSuchElementException as e:
                self.set_exception_log_and_inc_count(e)
                print("No element found", el_index + 1, "retornando", texto, "...")
        return texto

    def get_pre_text(self, el=None, el_index=0):
        texto = "[data não disponível] nome do contato não disponível  "
        if el is not None:
            try:
                texto = el.find_element(By.XPATH, ".//div[@data-pre-plain-text]").get_attribute("data-pre-plain-text")
            except StaleElementReferenceException as e:
                self.set_exception_log_and_inc_count(e)
                print("Stale element found!", el_index + 1, "retornando", texto, "...")
            except NoSuchElementException as e:
                self.set_exception_log_and_inc_count(e)
                print("No element found", el_index + 1, "retornando", texto, "...")
        return texto

    def get_tempo_autor_post(self, el=None, el_index=0):
        tempo, autor = self.get_pre_text(el, el_index).split("]")
        tempo, autor = tempo[1:], autor[1:-2]
        return tempo, autor

    def abre_whatsapp_chrome(self):
        # Selenium irá entrar no whats e aguardar 120 segundos até o dom estiver pronto.
        self.driver.get('https://web.whatsapp.com/')
        xpath = "//div[@data-testid='chat-list-search' and @title='Caixa de texto de pesquisa']/p"
        self.espera_por_elemento_xpath_el(120, xpath)

    def abre_conversa_contato(self, nome_contato):
        # Selecionamos o elemento da caixa de pesquisa do whats.
        caixa_de_pesquisa = self.get_caixa_de_pesquisa_el()
        # Escreveremos o nome do contato na caixa de pesquisa e aguardaremos 2 segundos.
        caixa_de_pesquisa.send_keys(nome_contato)
        # Vamos procurar o contato/grupo que está em um span e possui o título igual que buscamos e vamos clicar.
        contato = self.get_contato_lista_el(nome_contato)
        contato.click()

    # Ao usar este método devemos enviar a mensagem de saudação em uma lista.
    def saudacao_conversa(self, frases_iniciais):
        # Validamos se a frase inicial é uma lista.
        if type(frases_iniciais) == list:
            # Realizamos um for para enviar cada mensagem na lista.
            for frase in frases_iniciais:
                # Setamos a caixa de mensagem como o elemento com a classe _2S1VP.
                caixa_de_mensagem = self.get_caixa_de_mensagem_el()
                # Escrevemos a frase na caixa de mensagem.
                caixa_de_mensagem.send_keys(frase)
                # Setamos o botão de enviar e clicamos para enviar.
                botao_enviar = self.get_botao_enviar_el()
                botao_enviar.click()

    def gen_todas_mensagens_conversa_texto_tupla(self, inv=False):
        posts = self.get_all_posts_in_group_list()
        if inv:
            lista = range(len(posts) - 1, -1, -1)
        else:
            lista = range(len(posts))
        for index in lista:
            post = posts[index]
            texto = self.get_selectable_text(post, index)
            tempo, autor = self.get_tempo_autor_post(post, index)
            yield tempo, autor, texto

    def remover_msgs_contato_lista(self, texto_lista, contato):
        print("Filtrando", contato, "da conversa ...")
        lista = list(filter(lambda x: x[1] != contato, texto_lista))
        print("tam inicial", len(texto_lista), "tam final", len(lista))
        return lista

    def ultima_mensagem_conversa(self):
        ret = ('', '', '')
        for texto_tupla in self.gen_todas_mensagens_conversa_texto_tupla(inv=True):
            # ignora mensagem do proprio bot e mensagens invalidas
            if texto_tupla[1] != self.contato_bot and texto_tupla[1] != "nome do contato não disponível":
                ret = texto_tupla
                break
        print(ret)
        return ret

    # Nosso método responde irá receber o parâmetro texto que seria o retorno do método escuta.
    def envia_msg_conversa(self, resposta):
        # Setamos a reposta do bot na variável response.
        # Transformas em string essa resposta.
        resposta = str(resposta)
        # Setamos caixa de mensagens preenchemos com a resposta e clicamos em enviar.
        caixa_de_mensagem = self.get_caixa_de_mensagem_el()
        caixa_de_mensagem.send_keys(resposta)
        botao_enviar = self.get_botao_enviar_el()
        botao_enviar.click()

    def get_qtd_mensagens_nao_lidas(self):
        total = 0
        qtd = 0
        try:
            span_elements = self.driver.find_elements(By.XPATH, '//div[@data-testid="cell-frame-container" and'
                                                                ' .//span[@data-testid="icon-unread-count"]]'
                                                                '//span[@data-testid="icon-unread-count"]')
            for span in span_elements:
                if span.text != "":
                    total += int(span.text)
            qtd = len(span_elements)
            print("qtd msg nao lidas", total, "qtd conversas nao respondidas", qtd)
        except StaleElementReferenceException as e:
            self.set_exception_log_and_inc_count(e)
            print("Stale element found! retornando total", total, "qtd", qtd, "...")
        return total, qtd

    def gen_contatos_mensagens_nao_lidas(self):
        # num_celulas_total = self.driver.find_element(By.XPATH, '//*[@id="pane-side"]/div/div/div'). \
        #     get_attribute("aria-rowcount")
        # celulas_paneside = self.driver.find_elements(By.XPATH, "//*[@id='pane-side']/div/div/div/div")
        # celulas_frame_container = self.driver.find_elements(By.XPATH, "//div[@data-testid='cell-frame-container']")
        # # celulas_com_msg_novas = self.driver.find_elements(By.XPATH, "//*[@id='pane-side' and "
        # #                                                             ".//div[@data-testid='icon-unread-count']"
        # #                                                             "]/div/div/div/div")

        # qtd_msgs_nao_lidas_cell = 0
        # hora_msg_enviada_cell = ""
        # last_msg_cell = ""
        # nome_contato_cell = ""
        try:
            frame_cont_cells = self.driver.find_elements(By.XPATH, '//div[@data-testid="cell-frame-container" and'
                                                                   ' .//span[@data-testid="icon-unread-count"]]')

            # print("total celular paneside", num_celulas_total, "tam paneside", len(celulas_paneside),
            # "tam frame container",
            #       len(celulas_frame_container), "tam frame container msg novas", len(frame_cont_cells))
            # print("tam novas msg conversa", len(frame_cont_cells))

            for frame_cont_cell in frame_cont_cells:
                qtd_msgs_nao_lidas_cell = frame_cont_cell.find_element(By.XPATH,
                                                                       './/span[@data-testid="icon-unread-count"]').text
                hora_msg_enviada_cell = frame_cont_cell.find_element(By.XPATH, './/div[@data-testid='
                                                                               '"cell-frame-primary-detail"]').text
                nome_contato_cell = frame_cont_cell.find_element(By.XPATH, './/div[@data-testid="cell-frame-title"]'). \
                    text
                last_msg_cell = frame_cont_cell.find_element(By.XPATH, './/span[@data-testid="last-msg-status"]').text
                yield qtd_msgs_nao_lidas_cell, hora_msg_enviada_cell, last_msg_cell, nome_contato_cell
        except NoSuchElementException as e:
            self.set_exception_log_and_inc_count(e)
            print("tratando NoSuchElementException nao retornando...")
            # yield qtd_msgs_nao_lidas_cell, hora_msg_enviada_cell, last_msg_cell, nome_contato_cell
        except StaleElementReferenceException as e:
            self.set_exception_log_and_inc_count(e)
            print("tratando StaleElementReferenceException nao retornando...")
            # yield qtd_msgs_nao_lidas_cell, hora_msg_enviada_cell, last_msg_cell, nome_contato_cell

    def fecha_conversa(self):
        caixa_de_mensagem = self.get_caixa_de_mensagem_el()
        # Escrevemos a frase na caixa de mensagem.
        esc = chr(27)
        caixa_de_mensagem.send_keys(esc)

    def get_all_attributes_el(self, el):
        attrs = self.driver.execute_script(
            'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) '
            '{ items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', el)
        return attrs
