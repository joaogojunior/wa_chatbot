import os

from selenium import webdriver
from selenium.common import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import StaleElementReferenceException, NoSuchElementException


class Scraper:
    _default_timeout = 4
    _init_timeout = 120

    def __init__(self, url, xpath, profile_sufix):
        # Setamos o caminho de nossa aplicação.
        self.cwd = os.getcwd()
        # Configuramos um profile no chrome para não precisar logar no whats toda vez que iniciar o bot.
        options = webdriver.ChromeOptions()
        options.add_argument(r"user-data-dir=" + self.cwd + "/profile/" + profile_sufix)
        # Iniciamos o driver.
        service = Service()
        # Setamos onde está nosso chromedriver.
        service.executable_path = self.cwd + "/driver"
        self.driver = webdriver.Chrome(service=service, options=options)
        self.exceptions_count = 0
        self.log_dir = "logs/"
        self.log_file = self.cwd + "/" + self.log_dir + profile_sufix + "_exceptions.log"
        self.abre_url_chrome(url)
        if self.espera_por_elemento_xpath_el(xpath, self._init_timeout) is None:
            # print("Não foi possivel carregar o conteúdo da pagina solicitada... (sem internet?)")
            # exit(1)
            raise Exception("Não foi possivel encontrar o elemento na url solicitada... "
                            "(xpath invalido ou sem internet) " + url + "el: " + xpath)

    def abre_url_chrome(self, url):
        self.driver.get(url)

    def espera_por_elemento_xpath_el(self, xpath, tempo=None, clickable=False):
        if tempo is None:
            tempo = Scraper._default_timeout
        wait = WebDriverWait(self.driver, tempo)
        try:
            if clickable:
                el = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            else:
                el = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException as e:
            self.set_exception_log_and_inc_count(e)
            print("Tratando TimeoutException, retornando None...")
            el = None
        return el

    def espera_por_elemento_tagname_el(self, tagname, tempo=None):
        if tempo is None:
            tempo = Scraper._default_timeout
        wait = WebDriverWait(self.driver, tempo)
        try:
            el = wait.until(EC.presence_of_element_located((By.TAG_NAME, tagname)))
        except TimeoutException as e:
            self.set_exception_log_and_inc_count(e)
            print("Tratando TimeoutException, retornando None...")
            el = None
        return el

    def get_exceptions_counter(self):
        return self.exceptions_count

    def set_exception_log_and_inc_count(self, e):
        self.exceptions_count += 1
        if not os.path.isdir("./" + self.log_dir):
            os.mkdir("logs")
        csv = open(self.log_file, "a")
        csv.write(str(e))
        csv.close()

    def get_all_attributes_el(self, el):
        attrs = self.driver.execute_script(
            'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) '
            '{ items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value };'
            'return items;', el)
        return attrs

    def get_list_elements_from_xpath(self, xpath, el=None):
        if el is None:
            el = self.driver
        try:
            lista = el.find_elements(By.XPATH, xpath)
        except StaleElementReferenceException as e:
            self.set_exception_log_and_inc_count(e)
            print("Tratando Stale Element Exception, retornando lista vazia...")
            lista = []
        except WebDriverException as e:
            self.set_exception_log_and_inc_count(e)
            print("Tratando WebDriver Exception, retornando lista vazia...")
            lista = []
        return lista

    def get_child_text_by_css_selector(self, css_select, default_texto, el=None):
        texto = default_texto
        if el is not None:
            try:
                texto = el.find_element(By.CSS_SELECTOR, css_select).text
            except StaleElementReferenceException as e:
                self.set_exception_log_and_inc_count(e)
                print("Tratando stale element exception! retornando", texto, "...")
            except NoSuchElementException as e:
                self.set_exception_log_and_inc_count(e)
                print("Tratando no element exception! retornando", texto, "...")
            except WebDriverException as e:
                self.set_exception_log_and_inc_count(e)
                print("Tratando WebDriver exception! retornando", texto, "...")
        return texto

    def get_child_text_by_xpath(self, xpath, default_texto, el=None):
        texto = default_texto
        if el is not None:
            try:
                texto = el.find_element(By.XPATH, xpath).text
            except StaleElementReferenceException as e:
                self.set_exception_log_and_inc_count(e)
                print("Stale element found! retornando", texto, "...")
            except NoSuchElementException as e:
                self.set_exception_log_and_inc_count(e)
                print("No element found retornando", texto, "...")
            except WebDriverException as e:
                self.set_exception_log_and_inc_count(e)
                print("Tratando no WebDriver exception retornando", texto, "...")
        return texto

    def get_child_attribute_by_xpath(self, xpath, atributo, default_texto, el=None):
        texto = default_texto
        if el is not None:
            try:
                texto = el.find_element(By.XPATH, xpath).get_attribute(atributo)
            except StaleElementReferenceException as e:
                self.set_exception_log_and_inc_count(e)
                print("Stale element found! retornando", texto, "...")
            except NoSuchElementException as e:
                self.set_exception_log_and_inc_count(e)
                print("No element found retornando", texto, "...")
            except WebDriverException as e:
                self.set_exception_log_and_inc_count(e)
                print("WebDriver Exception retornando", texto, "...")
        return texto

    #
    # def get_element_xpath_js(self, xpath, el):
    #     _xpath = self.get_xpath_from_element(el)
    #     script = \
    #         "function getXPath(parent_selector, selector) {\
    #             const context = document.evaluate(parent_selector, document, null, XPathResult.\
    #                                             ORDERED_NODE_SNAPSHOT_TYPE, null);\
    #             const found = document.evaluate(selector, context, null, XPathResult.\
    #                                             ORDERED_NODE_SNAPSHOT_TYPE, null);\
    #             return found\
    #             }\
    #         return getXPath(arguments[0], arguments[1])"
    #     print(_xpath, xpath)
    #     return self.driver.execute_script(script, _xpath, xpath)

    def get_xpath_from_element(self, el):
        # casos bases - se há um node com id para iniciar xpath ou se chegamos na raiz (document.body)
        if el.get_attribute("id") != "":  # and el.get_attribute("id") is not None:
            return 'id(\"' + el.get_attribute("id") + '\")'
        elif el == self.get_list_elements_from_xpath("/html/body")[0]:
            return "/html/body"
        ix = 1
        pai = self.get_list_elements_from_xpath('./..', el)[0]
        filhos = self.get_list_elements_from_xpath('./*', pai)
        for irmao in filhos:
            if irmao == el:
                # print("encontrou o elemento no meio dos filhos")
                return self.get_xpath_from_element(pai) + "/" + el.tag_name + "[" + str(ix) + "]"
            elif irmao.tag_name == el.tag_name:
                # print("acrescentou ix pois irmao tem o mesmo tagname")
                ix += 1
            # else:
            #     print("entrou no else...")
