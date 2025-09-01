import os
import random
import time

from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait


class TicketAutomator:
    max_retries = 1

    def __init__(self):

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")  # for test
        options.add_argument("--headless")  # for production
        options.add_argument("--disable-gpu")  # Recommended for Windows
        self.driver = webdriver.Chrome(service=Service(), options=options)
        self.wait = WebDriverWait(self.driver, 20)

    def login(self, username, password):
        self.driver.get("https://ticket.xutil.net/login/")

        self.set_input_value(By.XPATH, "//input[@type='email']", username)
        pass_input = self.set_input_value(By.XPATH, "//input[@type='password']", password)
        pass_input.send_keys(Keys.ENTER)

        # Wait for login to complete
        time.sleep(3)

    def wait_room(self):
        self.driver.get("https://ticket.xutil.net/store/wait-room")
        customers = []
        first_name = None
        i = 1
        while True:
            time.sleep(1)
            try:
                nombre_servicio = self.get_node(By.XPATH,
                                                f"(//div[contains(@class, 'v-card__title') and contains(@class, 'fix-title')])[{i}]").text.lower()
            except Exception as e:
                if str(e).startswith('Failed to interact with element after'):
                    print(str(e))
                    break
            # print(nombre_servicio)
            # solo buscar por ticket de gasolina
            if 'combustible' in nombre_servicio:
                name = self.get_node(By.XPATH, f"(//div[contains(@class,'v-card__text')]//span)[{i}]").text
                position = int(
                    self.get_node(By.XPATH, f"(//div[contains(@class,'v-progress-linear__content')])[{i}]").text.split(
                        " ")[
                        1].strip())

                if first_name is None:
                    first_name = name
                elif first_name == name:
                    break
                # print(name)
                customers.append((name, position))
            # visit next page
            i += 1
            next_element = self.get_node(By.XPATH, "//i[@class='v-icon notranslate mdi mdi-chevron-right theme--dark']")
            next_element.click()

        return customers

    def has_ticket(self):
        self.driver.get("https://ticket.xutil.net/store/tickets")
        time.sleep(1)
        try:
            self.get_node(By.XPATH, "//div[contains(text(),'no tiene tickets')]")
            return False
        except Exception as e:
            return True

    def logout(self):
        arrow_down = self.get_node(By.XPATH,
                                   "//div[contains(@class, 'account-menu') and contains(@class, 'v-card--link')]")
        arrow_down.click()
        time.sleep(0.5)
        salir = self.get_node(By.XPATH,
                              "//div[@class='v-menu__content theme--light menuable__content__active']//div[@class='v-list-item__title' and normalize-space(text())='Salir']")
        salir.click()

    def quit(self):
        self.driver.quit()

    def get_select(self, selector_type, selector_value: str) -> Select:
        """
        Waits for a <select> element by its NAME and returns it as a Select object.

        :param selector_value: The NAME attribute of the select element
        :return: selenium.webdriver.support.ui.Select object
        """

        element = self.get_node(selector_type, selector_value)
        return Select(element)

    def set_input_value(self, selector_type, selector_value: str, input_value: str):
        """
        Locate an input, clear it, and set a new value.

        :param selector_type:
        :param selector_value: the locator value
        :param input_value: the text to input
        """
        element = self.get_node(selector_type, selector_value)
        element.clear()
        element.send_keys(input_value)
        return element  # return element in case you want to use it later

    def get_node(self, selector_type, selector_value: str):
        """
        Return a html node.

        :param selector_type:
        :param selector_value: the locator value
        """
        for attempt in range(TicketAutomator.max_retries):
            try:
                element = self.wait.until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                return element  # return element in case you want to use it later
            except StaleElementReferenceException:
                print(f"StaleElementReferenceException caught on attempt {attempt + 1}. Retrying...")
                time.sleep(1)  # Give the page a moment to settle
            except Exception as e:  # Catch other potential exceptions as well
                print(f"An unexpected error occurred: {attempt + 1}. Retrying...")
                time.sleep(1)  # Give the page a moment to settle

        raise Exception(f"Failed to interact with element after {TicketAutomator.max_retries} attempts.")


if __name__ == "__main__":
    automator = TicketAutomator()
    users = [
        # ("manologimenez322@gmail.com", "Ticket2++"),
        ("annielito590@gmail.com", "Ticket2++"),
        # ("annielmarrero@gmail.com", "Ticket2++"),
        # ("marientcorrales@gmail.com", "Ticket2++"),
        # ("carlosgarciasoko@gmail.com", "Ticket2++")
    ]
    customers = []
    tickets = []
    for username, password in users:
        # print(f"Username: {username}, Password: {password}")
        automator.login(username, password)
        customers += automator.wait_room()
        if automator.has_ticket():
            tickets.append(username)
        automator.logout()
        time.sleep(random.uniform(1, 3))

    automator.quit()

    customers.sort(key=lambda x: x[1])
    # print('--------------- Sala de espera ---------------')
    # i = 1
    # for name, position in customers:
    #     print(f"{i}. {position} - {name}")
    #     i += 1

    with open('ticket_info.txt', 'w', encoding="utf-8") as f:
        f.write('--------------- Sala de espera ---------------\n')
        i = 1
        for name, position in customers:
            f.write(f"{i}. {position} - {name}\n")
            i += 1

        i = 1
        f.write('\n\n')
        f.write('--------------- Tickets (Revisar cuentas) ---------------\n')
        for user in tickets:
            f.write(f"{i}. {user}\n")
            i += 1

        full_path = os.path.abspath(f.name)
        print(f'Archivo salvado en : {full_path}')
