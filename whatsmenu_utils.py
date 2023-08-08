import scraper_utils


class WhatsMenuScrapper(scraper_utils.Scraper):
    MSG_AUDIO_DESABILITADO = '//span[@class="me-auto"]'
    QTD_PEDIDOS_NOVOS = '//span[@class=" position-absolute badge rounded-pill bg-danger"]'
    TODOS_PEDIDOS = "//tr[@title]"
    TODOS_PEDIDOS_CANCELADOS = '//tr[@title and .//span="Cancelado"]'
    COD_PEDIDO = '//tr[@title]//td[@data-title="Cód. Pedido: "]//span'
    NOME_PEDIDO = '//tr[@title]//td[@data-title="Nome: "]//span'
    TEL_PEDIDO = '//tr[@title]//td[@data-title="Telefone:"]//span'
    TOTAL_PEDIDO = '//tr[@title]//td[@data-title="Total:"]//span'
    FORMA_PGT_PEDIDO = '//tr[@title]//td[@data-title="Pagamento:"]//span'
    TROCO_PARA_PEDIDO = '//tr[@title]//td[@data-title="Troco Para:"]//span'
    TROCO_PEDIDO = '//tr[@title]//td[@data-title="Troco:"]//span'
    ROW = '//div[@class="row"]/div/div/div/div/div[./h3]'

    def __init__(self):
        url = 'https://adm.whatsmenu.com.br/dashboard/request'
        suffix = "wm"
        xpath = "//h1"
        super().__init__(url, xpath, suffix)
        texto = self.get_child_text_by_xpath(xpath, "erro", self.driver)
        if texto != "GESTÃO DE PEDIDOS":
            raise Exception("Não conseguiu obter elemento h1...")
        self.click_msg_audio_el()

    def click_msg_audio_el(self):
        banner = self.espera_por_elemento_xpath_el(WhatsMenuScrapper.MSG_AUDIO_DESABILITADO)
        print(self.get_xpath_from_element(banner))
        print(self.get_all_attributes_el(banner))
        banner.click()
