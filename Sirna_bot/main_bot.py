#!/usr/bin/python3

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait



class SIRNA:

    document_value = {
            'CC': 'Cédula de ciudadanía',
            'CE': 'Cedula de extranjería'
            }
    invalid_info_msg = 'La información suministrada no corresponde con ningún inscrito al URNA'
    success_msg = ''
    invalid_card = 'La tarjeta de {} {} se encuentra {} por {}'
    sirna_page = 'https://sirna.ramajudicial.gov.co/Paginas/Inscritos.aspx'

    @classmethod
    def check(cls, document_type, document_number, card_number):
        # Driver configuration
        options = FirefoxOptions()
        # The next line allows to selenium work without graphical interface
        # options.add_argument('--headless')
        driver = webdriver.Firefox(options=options) # create the driver
        driver.get(cls.sirna_page) # open the page
        # Select all the inputs and the search button
        num_busqueda = driver.find_element_by_css_selector('#ctl00_ctl34_g_eb7be7dc_0096_49f5_b95c_e2ef7df94440_txtNumeroBusqueda')
        num_documento = driver.find_element_by_css_selector('#ctl00_ctl34_g_eb7be7dc_0096_49f5_b95c_e2ef7df94440_txtNumDocumento')
        doc_type = driver.find_element_by_css_selector('#ctl00_ctl34_g_eb7be7dc_0096_49f5_b95c_e2ef7df94440_ddlTipoDocumentosBusqueda')
        search_button = driver.find_element_by_css_selector('#btnEnviar')
        # select document type
        doc_type.send_keys(cls.document_value[document_type])
        # field the information
        num_busqueda.send_keys(card_number)
        num_documento.send_keys(document_number)
        # Hit that button
        search_button.send_keys(Keys.RETURN)
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            driver.switch_to.alert.accept()
            driver.quit()
            return cls.invalid_info_msg, False
        except TimeoutException:
            estado = driver.find_element_by_xpath('/html/body/form/div[4]/div/div/section/div/span/div[1]/div[3]/div[2]/div/div[1]/div/div/div/div[1]/div[2]/div/div/div[1]/table/tbody/tr/td[6]').text
            if estado == 'VIGENTE':
                driver.quit()
                return cls.success_msg, True
            names = driver.find_element_by_css_selector('tbody.ui-widget-content > tr:nth-child(1) > td:nth-child(2)').text
            last_names = driver.find_element_by_css_selector('tbody.ui-widget-content > tr:nth-child(1) > td:nth-child(1)').text
            motive = driver.find_element_by_css_selector('tbody.ui-widget-content > tr:nth-child(1) > td:nth-child(7)')
            driver.quit()
            return cls.invalid_card.format(names, last_names, estado, motive), False
