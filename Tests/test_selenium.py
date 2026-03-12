import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://localhost:5173"


@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=options)
    d.implicitly_wait(5)
    yield d
    d.quit()


class TestLoginPageLoads:
    """Vérifie que la page de connexion charge tous ses éléments."""

    def test_login_page_title(self, driver):
        driver.get(f"{BASE_URL}/login")
        wait = WebDriverWait(driver, 10)
        heading = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "h2")))
        assert "Connexion" in heading.text

    def test_login_email_field_present(self, driver):
        driver.get(f"{BASE_URL}/login")
        field = driver.find_element(By.ID, "email")
        assert field.is_displayed()
        assert field.get_attribute("type") == "email"

    def test_login_password_field_present(self, driver):
        driver.get(f"{BASE_URL}/login")
        field = driver.find_element(By.ID, "password")
        assert field.is_displayed()
        assert field.get_attribute("type") == "password"

    def test_login_submit_button_present(self, driver):
        driver.get(f"{BASE_URL}/login")
        button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        assert button.is_displayed()
        assert button.is_enabled()

    def test_login_register_link_present(self, driver):
        driver.get(f"{BASE_URL}/login")
        link = driver.find_element(By.LINK_TEXT, "S'inscrire")
        assert link.is_displayed()


class TestRegisterPageLoads:
    """Vérifie que la page d'inscription charge tous ses éléments."""

    def test_register_page_title(self, driver):
        driver.get(f"{BASE_URL}/register")
        wait = WebDriverWait(driver, 10)
        heading = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "h2")))
        assert "Inscription" in heading.text

    def test_register_name_field_present(self, driver):
        driver.get(f"{BASE_URL}/register")
        field = driver.find_element(By.ID, "name")
        assert field.is_displayed()
        assert field.get_attribute("type") == "text"

    def test_register_email_field_present(self, driver):
        driver.get(f"{BASE_URL}/register")
        field = driver.find_element(By.ID, "email")
        assert field.is_displayed()
        assert field.get_attribute("type") == "email"

    def test_register_password_field_present(self, driver):
        driver.get(f"{BASE_URL}/register")
        field = driver.find_element(By.ID, "password")
        assert field.is_displayed()
        assert field.get_attribute("type") == "password"

    def test_register_confirm_password_field_present(self, driver):
        driver.get(f"{BASE_URL}/register")
        field = driver.find_element(By.ID, "confirmPassword")
        assert field.is_displayed()
        assert field.get_attribute("type") == "password"

    def test_register_submit_button_present(self, driver):
        driver.get(f"{BASE_URL}/register")
        button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        assert button.is_displayed()
        assert button.is_enabled()


class TestRedirects:
    """Vérifie les redirections de l'application."""

    def test_root_redirects_to_login_when_unauthenticated(self, driver):
        driver.get(f"{BASE_URL}/")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.url_contains("/login"))
        assert "/login" in driver.current_url

    def test_dashboard_redirects_to_login_when_unauthenticated(self, driver):
        driver.get(f"{BASE_URL}/dashboard")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.url_contains("/login"))
        assert "/login" in driver.current_url


if __name__ == "__main__":
    pytest.main(["-v", "--html=report.html", "--self-contained-html"])