import scraper_utils


class CardapioScrapper(scraper_utils.Scraper):
    CAIXA_PROCURAR = '//input[@type="search"]'

    def __init__(self):
        url = 'https://whatsmenu.com.br/akisushibar'
        suffix = "aswm"
        super().__init__(url, CardapioScrapper.CAIXA_PROCURAR, suffix)
        texto = self.get_child_attribute_by_xpath(CardapioScrapper.CAIXA_PROCURAR, "placeholder", "erro", self.driver)
        if texto != "Buscar produtos por nome ou descrição":
            raise Exception("Não conseguiu obter input box...")
