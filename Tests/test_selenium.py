import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://localhost:3000"

ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "password"


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


def logout(driver):
    driver.get(BASE_URL)
    driver.execute_script("window.localStorage.clear();")
    driver.delete_all_cookies()


def login(driver):
    # Clear any existing session first
    logout(driver)
    driver.get(f"{BASE_URL}/login")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.ID, "email")))
    driver.find_element(By.ID, "email").send_keys(ADMIN_EMAIL)
    driver.find_element(By.ID, "password").send_keys(ADMIN_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    wait.until(EC.url_contains("/dashboard"), message=(
        "Login timed out — is the backend running on localhost:3001?"
    ))


class TestAuthPages:

    def test_login_form_elements(self, driver):
        driver.get(f"{BASE_URL}/login")
        wait = WebDriverWait(driver, 10)
        heading = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "h2")))
        assert "Connexion" in heading.text
        assert driver.find_element(By.ID, "email").get_attribute("type") == "email"
        assert driver.find_element(By.ID, "password").get_attribute("type") == "password"
        assert driver.find_element(By.CSS_SELECTOR, "button[type='submit']").is_enabled()

    def test_login_has_register_link(self, driver):
        driver.get(f"{BASE_URL}/login")
        link = driver.find_element(By.LINK_TEXT, "S'inscrire")
        assert link.is_displayed()

    def test_register_form_elements(self, driver):
        driver.get(f"{BASE_URL}/register")
        wait = WebDriverWait(driver, 10)
        heading = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "h2")))
        assert "Inscription" in heading.text
        assert driver.find_element(By.ID, "name").is_displayed()
        assert driver.find_element(By.ID, "email").get_attribute("type") == "email"
        assert driver.find_element(By.ID, "password").get_attribute("type") == "password"
        assert driver.find_element(By.ID, "confirmPassword").get_attribute("type") == "password"
        assert driver.find_element(By.CSS_SELECTOR, "button[type='submit']").is_enabled()

class TestNavigation:

    def test_root_redirects_to_login_when_unauthenticated(self, driver):
        logout(driver)
        driver.get(f"{BASE_URL}/")
        WebDriverWait(driver, 10).until(EC.url_contains("/login"))
        assert "/login" in driver.current_url

    def test_dashboard_redirects_to_login_when_unauthenticated(self, driver):
        logout(driver)
        driver.get(f"{BASE_URL}/dashboard")
        WebDriverWait(driver, 10).until(EC.url_contains("/login"))
        assert "/login" in driver.current_url

    def test_login_page_link_goes_to_register(self, driver):
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.LINK_TEXT, "S'inscrire").click()
        WebDriverWait(driver, 10).until(EC.url_contains("/register"))
        assert "/register" in driver.current_url

class TestDashboard:

    def test_login_redirects_to_dashboard(self, driver):
        login(driver)
        assert "/dashboard" in driver.current_url

    def test_dashboard_header_visible(self, driver):
        login(driver)
        wait = WebDriverWait(driver, 10)
        header = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".dashboard-header h1")
        ))
        assert "Gestionnaire de Tâches" in header.text

    def test_dashboard_logout_button_present(self, driver):
        login(driver)
        btn = driver.find_element(By.CSS_SELECTOR, ".logout-btn")
        assert btn.is_displayed()

    def test_dashboard_new_task_button_present(self, driver):
        login(driver)
        wait = WebDriverWait(driver, 10)
        btn = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".btn.btn-primary")
        ))
        assert "Nouvelle Tâche" in btn.text

class TestTaskForm:

    def test_task_form_opens_on_button_click(self, driver):
        login(driver)
        wait = WebDriverWait(driver, 10)
        btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".btn.btn-primary")
        ))
        btn.click()
        modal = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".modal")
        ))
        assert modal.is_displayed()

    def test_task_form_title_field_present(self, driver):
        login(driver)
        driver.find_element(By.CSS_SELECTOR, ".btn.btn-primary").click()
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "title"))
        )
        assert driver.find_element(By.ID, "title").is_displayed()


    def test_task_form_close_button_works(self, driver):
        login(driver)
        driver.find_element(By.CSS_SELECTOR, ".btn.btn-primary").click()
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".close-btn"))
        )
        driver.find_element(By.CSS_SELECTOR, ".close-btn").click()
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal"))
        )
        assert len(driver.find_elements(By.CSS_SELECTOR, ".modal")) == 0

if __name__ == "__main__":
    pytest.main(["-v", "--html=report.html", "--self-contained-html"])