"""
HP Smart App Onboarding Flow
Handles the complete onboarding process including privacy acceptance and sign-in
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from appium.webdriver.common.appiumby import AppiumBy

logger = logging.getLogger(__name__)


class HPSmartOnboardingFlow:
    """Handles HP Smart app onboarding flow including privacy and sign-in"""
    
    def __init__(self, driver, wait_utils=None, common_utils=None):
        self.driver = driver
        self.wait_utils = wait_utils
        self.common_utils = common_utils
        self.wait = WebDriverWait(driver, 30)
        
        # If common_utils is provided and has the required methods, use it
        if common_utils and hasattr(common_utils, 'take_screenshot'):
            self.take_screenshot = common_utils.take_screenshot
        else:
            # Fallback to basic screenshot method
            self.take_screenshot = self._basic_screenshot
    
    def complete_onboarding_flow(self, platform="android"):
        """
        Complete HP Smart app onboarding flow
        
        Args:
            platform (str): Platform type ("android" or "ios")
            
        Returns:
            dict: Onboarding results
        """
        logger.info("Starting HP Smart app onboarding flow")
        results = {
            "privacy_accepted": False,
            "sign_in_clicked": False,
            "onboarding_completed": False,
            "steps_completed": []
        }
        
        try:
            # Step 1: Wait for app to launch and verify it's actually loaded
            logger.info("Step 1: Waiting for HP Smart app to launch...")
            if self.wait_utils:
                app_launched = self.wait_utils.wait_for_app_launch(timeout=180)
                if not app_launched:
                    logger.error("App failed to launch properly")
                    results["steps_completed"].append("App launch failed")
                    results["onboarding_completed"] = False
                    return results
            else:
                time.sleep(5)  # Basic wait
            
            # Verify app is actually loaded and functional
            logger.info("Step 1.1: Verifying app is loaded and functional...")
            if self.wait_utils and hasattr(self.wait_utils, '_verify_app_loaded'):
                app_loaded = self.wait_utils._verify_app_loaded()
                if not app_loaded:
                    logger.error("App is not properly loaded - still in loading state")
                    results["steps_completed"].append("App not loaded properly")
                    results["onboarding_completed"] = False
                    return results
            
            self.take_screenshot("app_launched")
            results["steps_completed"].append("App launched and verified")
            
            # Step 2: Handle privacy acceptance
            logger.info("Step 2: Handling privacy acceptance...")
            privacy_result = self._handle_privacy_acceptance(platform)
            results["privacy_accepted"] = privacy_result
            if privacy_result:
                results["steps_completed"].append("Privacy accepted")
            else:
                results["steps_completed"].append("Privacy screen not found")
            
            # Step 3: Handle sign-in
            logger.info("Step 3: Handling sign-in...")
            signin_result = self._handle_sign_in(platform)
            results["sign_in_clicked"] = signin_result
            if signin_result:
                results["steps_completed"].append("Sign-in clicked")
            else:
                results["steps_completed"].append("Sign-in not found")
            
            # Step 4: Continue with onboarding
            logger.info("Step 4: Continuing with onboarding...")
            onboarding_result = self._continue_onboarding(platform)
            results["onboarding_completed"] = onboarding_result
            if onboarding_result:
                results["steps_completed"].append("Onboarding completed")
            else:
                results["steps_completed"].append("Onboarding failed - no elements found")
            
            # Only log success if onboarding actually completed
            if results["onboarding_completed"]:
                logger.info("HP Smart app onboarding flow completed successfully")
            else:
                logger.warning("HP Smart app onboarding flow failed - no onboarding elements found")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in onboarding flow: {e}")
            results["error"] = str(e)
            return results
    
    def _handle_privacy_acceptance(self, platform):
        """
        Handle privacy acceptance screen
        
        Args:
            platform (str): Platform type
            
        Returns:
            bool: True if privacy was handled, False if screen not found
        """
        logger.info("Looking for privacy acceptance screen...")
        
        # Wait for privacy screen to appear (max 10 seconds)
        privacy_selectors = [
            "//*[contains(@text, 'We value your data and privacy')]",
            "//*[contains(@text, 'privacy')]",
            "//*[contains(@text, 'data')]",
            "//*[contains(@text, 'Accept all')]",
            "//*[contains(@text, 'Accept')]",
            "//*[contains(@text, 'Agree')]",
            "//*[contains(@text, 'Continue')]"
        ]
        
        try:
            # Check if privacy screen is present
            privacy_screen_found = False
            for selector in privacy_selectors:
                try:
                    elements = self.driver.find_elements(AppiumBy.XPATH, selector)
                    if elements and any(elem.is_displayed() for elem in elements):
                        logger.info(f"Found privacy screen with selector: {selector}")
                        privacy_screen_found = True
                        break
                except:
                    continue
            
            if not privacy_screen_found:
                logger.info("Privacy screen not found - continuing to next step")
                return False
            
            # Look for Accept button
            accept_selectors = [
                "//*[@text='Accept all']",
                "//*[@text='Accept']",
                "//*[@text='Agree']",
                "//*[@text='Continue']",
                "//*[contains(@text, 'Accept')]",
                "//*[contains(@text, 'Agree')]",
                "//*[contains(@text, 'Continue')]",
                "//android.widget.Button[contains(@text, 'Accept')]",
                "//XCUIElementTypeButton[contains(@text, 'Accept')]"
            ]
            
            for selector in accept_selectors:
                try:
                    element = self.driver.find_element(AppiumBy.XPATH, selector)
                    if element.is_displayed():
                        logger.info(f"Found Accept button: {selector}")
                        element.click()
                        logger.info("Clicked Accept button")
                        time.sleep(2)  # Wait for screen to transition
                        self.common_utils.take_screenshot("privacy_accepted")
                        return True
                except:
                    continue
            
            logger.warning("Accept button not found on privacy screen")
            return False
            
        except Exception as e:
            logger.error(f"Error handling privacy acceptance: {e}")
            return False
    
    def _handle_sign_in(self, platform):
        """
        Handle sign-in screen
        
        Args:
            platform (str): Platform type
            
        Returns:
            bool: True if sign-in was clicked, False if not found
        """
        logger.info("Looking for sign-in screen...")
        
        # Wait for sign-in screen to appear
        signin_selectors = [
            "//*[contains(@text, 'Sign in')]",
            "//*[contains(@text, 'Sign In')]",
            "//*[contains(@text, 'Sign in &')]",
            "//*[contains(@text, 'Continue as guest')]",
            "//*[contains(@text, 'HP')]",
            "//*[contains(@text, 'Smart')]"
        ]
        
        try:
            # Check if sign-in screen is present
            signin_screen_found = False
            for selector in signin_selectors:
                try:
                    elements = self.driver.find_elements(AppiumBy.XPATH, selector)
                    if elements and any(elem.is_displayed() for elem in elements):
                        logger.info(f"Found sign-in screen with selector: {selector}")
                        signin_screen_found = True
                        break
                except:
                    continue
            
            if not signin_screen_found:
                logger.info("Sign-in screen not found - continuing to next step")
                return False
            
            # Look for Sign in button
            signin_button_selectors = [
                "//*[@text='Sign in']",
                "//*[@text='Sign In']",
                "//*[contains(@text, 'Sign in')]",
                "//*[contains(@text, 'Sign In')]",
                "//android.widget.Button[contains(@text, 'Sign in')]",
                "//XCUIElementTypeButton[contains(@text, 'Sign in')]"
            ]
            
            for selector in signin_button_selectors:
                try:
                    element = self.driver.find_element(AppiumBy.XPATH, selector)
                    if element.is_displayed():
                        logger.info(f"Found Sign in button: {selector}")
                        element.click()
                        logger.info("Clicked Sign in button")
                        time.sleep(3)  # Wait for screen to transition
                        self.common_utils.take_screenshot("sign_in_clicked")
                        return True
                except:
                    continue
            
            logger.warning("Sign in button not found on sign-in screen")
            return False
            
        except Exception as e:
            logger.error(f"Error handling sign-in: {e}")
            return False
    
    def _continue_onboarding(self, platform):
        """
        Continue with the rest of the onboarding process
        
        Args:
            platform (str): Platform type
            
        Returns:
            bool: True if onboarding completed successfully
        """
        logger.info("Continuing with onboarding process...")
        
        try:
            # Wait for next screen to load
            self.wait_utils.smart_wait("onboarding_continuation")
            
            # Look for common onboarding elements
            onboarding_elements = [
                "//*[contains(@text, 'Email')]",
                "//*[contains(@text, 'Password')]",
                "//*[contains(@text, 'Create account')]",
                "//*[contains(@text, 'Login')]",
                "//*[contains(@text, 'Welcome')]",
                "//*[contains(@text, 'Get started')]",
                "//*[contains(@text, 'Add device')]",
                "//*[contains(@text, 'Printer')]"
            ]
            
            found_elements = []
            for selector in onboarding_elements:
                try:
                    elements = self.driver.find_elements(AppiumBy.XPATH, selector)
                    if elements and any(elem.is_displayed() for elem in elements):
                        found_elements.append(selector)
                        logger.info(f"Found onboarding element: {selector}")
                except:
                    continue
            
            if found_elements:
                logger.info(f"Found {len(found_elements)} onboarding elements")
                self.common_utils.take_screenshot("onboarding_elements_found")
                return True
            else:
                logger.warning("No onboarding elements found")
                self.common_utils.take_screenshot("onboarding_no_elements_found")
                return False
                
        except Exception as e:
            logger.error(f"Error continuing onboarding: {e}")
            return False
    
    def handle_permissions(self, platform):
        """
        Handle app permissions
        
        Args:
            platform (str): Platform type
            
        Returns:
            bool: True if permissions handled successfully
        """
        logger.info("Handling app permissions...")
        
        try:
            if platform.lower() == "android":
                self.common_utils.handle_android_permissions()
            else:
                # iOS permission handling
                permission_texts = ["Allow", "OK", "Continue", "Yes"]
                for text in permission_texts:
                    try:
                        element = self.driver.find_element(
                            AppiumBy.XPATH, 
                            f"//*[@name='{text}' or @label='{text}']"
                        )
                        if element.is_displayed():
                            element.click()
                            logger.info(f"Clicked permission button: {text}")
                            time.sleep(2)
                    except NoSuchElementException:
                        continue
            
            self.common_utils.take_screenshot("permissions_handled")
            return True
            
        except Exception as e:
            logger.error(f"Error handling permissions: {e}")
            return False
    
    def _basic_screenshot(self, filename):
        """Basic screenshot method as fallback"""
        try:
            screenshot_path = f"Screenshots/{filename}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.warning(f"Could not take screenshot: {e}")
