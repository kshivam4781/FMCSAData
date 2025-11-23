"""
Test script for headless browser automation login
Tests the automated login and credential extraction functionality
"""

import json
import time
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Note: Proxy environment variables are checked in the function to avoid import-time output

# Configuration
LOGIN_URL = "https://bizfileonline.sos.ca.gov/"
SEARCH_URL = "https://bizfileonline.sos.ca.gov/search/business"
API_URL = "https://bizfileonline.sos.ca.gov/api/Records/businesssearch"

# Login credentials
LOGIN_USERNAME = "shivamssing96@gmail.com"
LOGIN_PASSWORD = "Solutions@121"

def type_slowly(element, text, min_delay=0.05, max_delay=0.3, make_mistakes=True):
    """
    Type text character by character with random delays and occasional mistakes to simulate human typing
    
    Args:
        element: Selenium WebElement to type into
        text: Text to type
        min_delay: Minimum delay between characters (seconds)
        max_delay: Maximum delay between characters (seconds)
        make_mistakes: Whether to simulate typing mistakes and corrections
    """
    element.clear()
    i = 0
    while i < len(text):
        char = text[i]
        
        # Occasionally make a mistake (10-15% chance, but not at the end)
        if make_mistakes and i < len(text) - 2 and random.random() < 0.12:
            # Type a wrong character (common adjacent key mistakes)
            wrong_chars = {
                'a': ['s', 'q', 'w'],
                'e': ['r', 'w', 'd'],
                'i': ['o', 'u', 'k'],
                'o': ['i', 'p', 'l'],
                's': ['a', 'd', 'w'],
                'n': ['m', 'b', 'h'],
                'g': ['h', 'f', 't'],
                'h': ['g', 'j', 'y'],
                'm': ['n', 'j', 'k'],
                '6': ['5', '7'],
                '9': ['8', '0'],
                '@': ['.', '#'],
                '.': ['@', ','],
            }
            
            # Get wrong character options or use a random adjacent one
            if char.lower() in wrong_chars:
                wrong_char = random.choice(wrong_chars[char.lower()])
            else:
                # Use a random character from nearby keys
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz0123456789')
            
            # Type the wrong character
            element.send_keys(wrong_char)
            time.sleep(random.uniform(0.1, 0.3))  # Pause after mistake
            
            # Realize mistake and backspace
            element.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.15, 0.4))  # Pause before correction
            
            # Type the correct character
            element.send_keys(char)
            time.sleep(random.uniform(0.08, 0.25))
        else:
            # Normal typing
            element.send_keys(char)
            
            # Longer pause after special characters (natural breakpoints)
            if char == '@':
                delay = random.uniform(0.4, 0.7)  # Longer pause after @
            elif char == '.':
                delay = random.uniform(0.3, 0.6)  # Medium pause after .
            elif char in [' ', '-', '_']:
                delay = random.uniform(0.2, 0.5)  # Pause after separators
            else:
                # Irregular typing speed - sometimes faster, sometimes slower
                if random.random() < 0.1:  # 10% chance of longer pause (thinking)
                    delay = random.uniform(0.3, 0.8)
                elif random.random() < 0.2:  # 20% chance of medium pause
                    delay = random.uniform(0.15, 0.4)
                else:  # 70% chance of normal typing speed
                    delay = random.uniform(min_delay, max_delay)
            
            time.sleep(delay)
        
        i += 1

def inject_stealth_scripts(driver):
    """
    Inject JavaScript to hide automation signatures and make browser appear more human-like
    """
    stealth_script = """
    // Hide webdriver property
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    
    // Override the plugins property to use a custom getter
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
    });
    
    // Override the languages property
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en']
    });
    
    // Override permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
    
    // Mock chrome object
    window.chrome = {
        runtime: {}
    };
    
    // Override WebGL vendor and renderer
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) {
            return 'Intel Inc.';
        }
        if (parameter === 37446) {
            return 'Intel Iris OpenGL Engine';
        }
        return getParameter.call(this, parameter);
    };
    
    // Override canvas fingerprinting
    const toBlob = HTMLCanvasElement.prototype.toBlob;
    const toDataURL = HTMLCanvasElement.prototype.toDataURL;
    const getImageData = CanvasRenderingContext2D.prototype.getImageData;
    
    // Add noise to canvas to prevent fingerprinting
    const noise = () => Math.random() * 0.0001;
    CanvasRenderingContext2D.prototype.getImageData = function() {
        const imageData = getImageData.apply(this, arguments);
        for (let i = 0; i < imageData.data.length; i += 4) {
            imageData.data[i] += noise();
            imageData.data[i + 1] += noise();
            imageData.data[i + 2] += noise();
        }
        return imageData;
    };
    
    // Mock battery API
    if (navigator.getBattery) {
        navigator.getBattery = () => Promise.resolve({
            charging: true,
            chargingTime: 0,
            dischargingTime: Infinity,
            level: 1
        });
    }
    
    // Override connection property
    if (navigator.connection) {
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                effectiveType: '4g',
                rtt: 50,
                downlink: 10,
                saveData: false
            })
        });
    }
    
    // Remove automation indicators
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    
    // Override toString methods to hide automation
    window.navigator.webdriver = undefined;
    """
    
    try:
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': stealth_script
        })
        print("  ✓ Stealth scripts injected")
    except Exception as e:
        print(f"  ⚠ Could not inject stealth scripts: {str(e)[:50]}")

def check_network_info(driver):
    """
    Check network information to detect proxy usage
    """
    print()
    print("  Checking network configuration...")
    try:
        # Get IP information via JavaScript
        network_info = driver.execute_script("""
            return {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                languages: navigator.languages,
                hardwareConcurrency: navigator.hardwareConcurrency,
                deviceMemory: navigator.deviceMemory,
                connection: navigator.connection ? {
                    effectiveType: navigator.connection.effectiveType,
                    downlink: navigator.connection.downlink,
                    rtt: navigator.connection.rtt
                } : null
            };
        """)
        
        # Try to detect proxy via WebRTC (if available)
        try:
            proxy_info = driver.execute_script("""
                // Try to get local IP via WebRTC (may reveal proxy)
                return new Promise((resolve) => {
                    const pc = new RTCPeerConnection({iceServers: []});
                    pc.createDataChannel('');
                    pc.createOffer().then(offer => pc.setLocalDescription(offer));
                    pc.onicecandidate = (ice) => {
                        if (ice && ice.candidate && ice.candidate.candidate) {
                            const candidate = ice.candidate.candidate;
                            const match = candidate.match(/([0-9]{1,3}(\.[0-9]{1,3}){3})/);
                            if (match) {
                                resolve({localIP: match[1], candidate: candidate});
                            }
                        }
                    };
                    setTimeout(() => resolve({localIP: 'Not detected'}), 2000);
                });
            """)
            if proxy_info and proxy_info.get('localIP'):
                print(f"    Local IP detected: {proxy_info.get('localIP')}")
        except:
            pass
        
        print(f"    Platform: {network_info.get('platform', 'Unknown')}")
        print(f"    Language: {network_info.get('language', 'Unknown')}")
        if network_info.get('connection'):
            conn = network_info['connection']
            print(f"    Connection: {conn.get('effectiveType', 'Unknown')} (downlink: {conn.get('downlink', 'N/A')} Mbps)")
        
    except Exception as e:
        print(f"    ⚠ Could not check network info: {str(e)[:50]}")

def test_headless_login():
    """Test the headless browser login and credential extraction"""
    
    print("=" * 80)
    print("HEADLESS LOGIN AUTOMATION TEST")
    print("=" * 80)
    print()
    print("This script will test:")
    print("  1. Headless browser initialization")
    print("  2. Navigation to login page")
    print("  3. Login form interaction")
    print("  4. Credential extraction (cookies and auth token)")
    print("  5. API call test with extracted credentials")
    print()
    print("NOTE: If you see 'Proxy IP' in error messages but don't use a proxy:")
    print("  - Your ISP may be using CGNAT (Carrier-Grade NAT)")
    print("  - You might be on a corporate/work network with a proxy")
    print("  - IPv6 tunneling might be routing through a proxy")
    print("  - Try disabling IPv6 or using a different network")
    print()
    
    response = input("Continue with test? (y/n): ")
    if response.lower() != 'y':
        print("Test aborted.")
        return
    
    driver = None
    extracted_cookies = None
    extracted_token = None
    
    try:
        # Step 1: Initialize headless browser
        print()
        print("=" * 80)
        print("STEP 1: Initializing Chrome browser (VISIBLE MODE)")
        print("=" * 80)
        
        # Check for proxy environment variables that might be set by libraries
        print("  Checking for proxy environment variables...")
        proxy_env_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 
                          'NO_PROXY', 'no_proxy', 'ALL_PROXY', 'all_proxy']
        found_proxy_vars = []
        for var in proxy_env_vars:
            if var in os.environ:
                found_proxy_vars.append(f"{var}={os.environ[var]}")
        
        if found_proxy_vars:
            print(f"  ⚠ WARNING: Found proxy environment variables:")
            for var_info in found_proxy_vars:
                print(f"    - {var_info}")
            print("  Chrome options will override these to use direct connection")
        else:
            print("  ✓ No proxy environment variables found")
        
        chrome_options = Options()
        # Run in visible mode so user can see the automation
        # chrome_options.add_argument('--headless')  # Commented out to show browser
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        # User agent matches Chrome 120 (common version)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        # Start maximized for better visibility
        chrome_options.add_argument('--start-maximized')
        
        # NOTE: If you're using a proxy/VPN and getting blocked, consider:
        # 1. Using a residential proxy instead of datacenter/VPN proxy
        # 2. Using your own IP address if possible
        # 3. Proxy IPs are often flagged by Imperva security services
        # To add a proxy, uncomment and configure:
        # chrome_options.add_argument('--proxy-server=http://proxy-server:port')
        
        # EXPLICITLY DISABLE PROXY - Prevent Selenium/Chrome from using any proxy
        # This ensures we use direct connection, not through proxy servers
        # Some libraries/drivers may automatically route through proxies
        chrome_options.add_argument('--no-proxy-server')
        chrome_options.add_argument('--proxy-bypass-list=*')
        # Explicitly set proxy to direct connection
        chrome_options.add_experimental_option('prefs', {
            'proxy': {
                'mode': 0,  # 0 = Direct connection, no proxy
            }
        })
        
        # NOTE: If you're getting "Proxy IP" errors without using a proxy:
        # - Your ISP may be using CGNAT (Carrier-Grade NAT) - common with IPv6
        # - You might be on a corporate/work network with automatic proxy
        # - Selenium/ChromeDriver might be routing through a proxy automatically
        # - Try: Windows Settings > Network > Proxy (check if proxy is enabled)
        # - Try: Using a mobile hotspot or different network
        # - Try: Contacting your ISP about CGNAT/proxy usage
        
        # Anti-detection arguments
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-extensions-file-access-check')
        chrome_options.add_argument('--disable-extensions-http-throttling')
        chrome_options.add_argument('--disable-plugins-discovery')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--no-default-browser-check')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-translate')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        
        # Enable performance logging to capture network requests (but we'll use it carefully)
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        print("  Creating Chrome driver...")
        try:
            # Try using Selenium's built-in driver management first (Selenium 4.6+)
            driver = webdriver.Chrome(options=chrome_options)
            print("  ✓ Browser initialized successfully (using Selenium Manager)")
        except Exception as e:
            # Fallback to webdriver-manager if needed
            print(f"  Trying webdriver-manager... ({str(e)[:50]})")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("  ✓ Browser initialized successfully (using webdriver-manager)")
        
        driver.set_page_load_timeout(60)
        
        # Proxy settings have been explicitly disabled via Chrome options
        # Actual proxy usage will be verified after page load via network diagnostics
        
        # Inject stealth scripts BEFORE navigating to hide automation
        print("  Injecting anti-detection scripts...")
        inject_stealth_scripts(driver)
        
        # Enable Chrome DevTools Protocol (but only if needed, and make it less detectable)
        global_captured_headers = {}  # Store captured headers by URL (global for access later)
        # Note: CDP can be detected, so we'll enable it only when needed for token extraction
        # We'll enable it later, not at browser startup
        
        # Step 2: Navigate to login page
        print()
        print("=" * 80)
        print("STEP 2: Navigating to login page")
        print("=" * 80)
        print(f"  URL: {LOGIN_URL}")
        
        driver.get(LOGIN_URL)
        time.sleep(random.uniform(2, 4))  # Random wait time
        print(f"  Current URL: {driver.current_url}")
        print("  ✓ Page loaded")
        
        # Inject additional stealth scripts after page load
        print("  Applying additional anti-detection measures...")
        try:
            driver.execute_script("""
                // Remove webdriver property completely
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false
                });
                
                // Override webdriver property in window object
                delete window.navigator.__proto__.webdriver;
                
                // Mock plugins to look like real browser
                Object.defineProperty(navigator, 'plugins', {
                    get: () => {
                        return [
                            {
                                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                                description: "Portable Document Format",
                                filename: "internal-pdf-viewer",
                                length: 1,
                                name: "Chrome PDF Plugin"
                            },
                            {
                                0: {type: "application/pdf", suffixes: "pdf", description: ""},
                                description: "",
                                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                                length: 1,
                                name: "Chrome PDF Viewer"
                            }
                        ];
                    }
                });
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Ensure chrome object exists
                if (!window.chrome) {
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
                    };
                }
            """)
            print("  ✓ Additional stealth measures applied")
        except Exception as e:
            print(f"  ⚠ Could not apply additional stealth: {str(e)[:50]}")
        
        # Check network configuration to help diagnose proxy issues
        check_network_info(driver)
        
        # Step 3: Find and click login button (if needed)
        print()
        print("=" * 80)
        print("STEP 3: Finding login elements")
        print("=" * 80)
        
        login_selectors = [
            "a[href*='login']",
            "a[href*='signin']",
            "#login",
            ".login",
            "button:contains('Login')",
            "a:contains('Sign In')"
        ]
        
        login_clicked = False
        for selector in login_selectors:
            try:
                if ':contains(' in selector:
                    text = selector.split("'")[1]
                    element = driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
                else:
                    element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                element.click()
                login_clicked = True
                print(f"  ✓ Clicked login element: {selector}")
                time.sleep(2)
                break
            except:
                continue
        
        if not login_clicked:
            print("  ℹ No login button found, assuming already on login page")
        
        # Step 4: Enter credentials
        print()
        print("=" * 80)
        print("STEP 4: Entering login credentials")
        print("=" * 80)
        
        # Find username field
        username_selectors = [
            "input[name='identifier']",  # Okta login field
            "input[id='input28']",  # Specific ID from the website
            "input[name='username']",
            "input[name='email']",
            "input[type='email']",
            "input[autocomplete='username']",
            "input[id*='username']",
            "input[id*='email']",
            "#username",
            "#email"
        ]
        
        username_field = None
        for selector in username_selectors:
            try:
                username_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"  ✓ Found username field: {selector}")
                break
            except:
                continue
        
        if not username_field:
            raise Exception("❌ Could not find username field")
        
        # Click on the field first (human behavior)
        username_field.click()
        time.sleep(random.uniform(0.3, 0.6))  # Pause before starting to type
        
        print(f"  Typing username slowly (character by character with mistakes)...")
        type_slowly(username_field, LOGIN_USERNAME, min_delay=0.06, max_delay=0.35, make_mistakes=True)
        print(f"  ✓ Entered username: {LOGIN_USERNAME[:20]}...")
        time.sleep(random.uniform(0.5, 1.2))  # Pause after typing
        
        # Find password field
        password_selectors = [
            "input[name='credentials.passcode']",  # Okta password field
            "input[id='input36']",  # Specific ID from the website
            "input[autocomplete='current-password']",
            "input[name='password']",
            "input[type='password']",
            "input[id*='password']",
            "#password"
        ]
        
        password_field = None
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"  ✓ Found password field: {selector}")
                break
            except:
                continue
        
        if not password_field:
            raise Exception("❌ Could not find password field")
        
        # Click on the field first (human behavior)
        password_field.click()
        time.sleep(random.uniform(0.4, 0.8))  # Longer pause before typing password
        
        print("  Typing password slowly (character by character with mistakes)...")
        type_slowly(password_field, LOGIN_PASSWORD, min_delay=0.08, max_delay=0.4, make_mistakes=True)
        print("  ✓ Entered password: [HIDDEN]")
        time.sleep(random.uniform(0.6, 1.5))  # Pause after typing password
        
        # Step 5: Submit login form
        print()
        print("=" * 80)
        print("STEP 5: Submitting login form")
        print("=" * 80)
        
        submit_selectors = [
            "input[type='submit'][value='Sign in']",  # Specific Okta submit button
            "input.button.button-primary[type='submit']",  # Okta submit button by class
            "input[data-type='save'][type='submit']",  # Okta submit by data attribute
            "#okta-signin-submit",
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Sign In')",
            "button:contains('Log In')",
            "button:contains('Continue')"
        ]
        
        submit_clicked = False
        for selector in submit_selectors:
            try:
                if ':contains(' in selector:
                    text = selector.split("'")[1]
                    submit_button = driver.find_element(By.XPATH, f"//button[contains(text(), '{text}')]")
                else:
                    submit_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                # Pause before clicking (human behavior - reviewing before submitting)
                time.sleep(random.uniform(0.5, 1.2))
                submit_button.click()
                submit_clicked = True
                print(f"  ✓ Clicked submit button: {selector}")
                break
            except:
                continue
        
        if not submit_clicked:
            password_field.send_keys(Keys.RETURN)
            print("  ✓ Pressed Enter on password field")
        
        # Step 6: Wait for login to complete
        print()
        print("=" * 80)
        print("STEP 6: Waiting for login to complete")
        print("=" * 80)
        
        max_wait = 30
        waited = 0
        login_success = False
        
        while waited < max_wait:
            current_url = driver.current_url
            page_source = driver.page_source.lower()
            
            # Check if we're past the login page
            if 'login' not in current_url.lower() and 'signin' not in current_url.lower():
                if 'bizfileonline' in current_url.lower():
                    print(f"  ✓ Login successful! Current URL: {current_url}")
                    login_success = True
                    break
            
            # Check for error messages
            if 'error' in page_source or 'invalid' in page_source or 'incorrect' in page_source:
                error_elements = driver.find_elements(By.CSS_SELECTOR, ".error, .alert, [role='alert']")
                if error_elements:
                    error_text = error_elements[0].text
                    raise Exception(f"❌ Login failed: {error_text}")
            
            time.sleep(2)
            waited += 2
            print(f"  Waiting... ({waited}s/{max_wait}s)")
        
        if not login_success:
            raise Exception("❌ Login timeout - could not verify successful login")
        
        # Step 7: Navigate to search page and extract credentials
        print()
        print("=" * 80)
        print("STEP 7: Extracting credentials")
        print("=" * 80)
        
        print("  Navigating to search page...")
        driver.get(SEARCH_URL)
        time.sleep(8)
        print(f"  ✓ Current URL: {driver.current_url}")
        
        # Clear performance logs BEFORE making any API calls
        print("  Clearing old performance logs...")
        driver.get_log('performance')
        time.sleep(1)
        
        # Set up CDP to capture all network requests with headers
        # Note: CDP can be detected, so we enable it only when needed for token extraction
        print("  Setting up network monitoring (for token extraction)...")
        try:
            # Enable Network domain (needed for token extraction)
            # This is done only after successful login to minimize detection
            driver.execute_cdp_cmd('Network.enable', {})
            print("  ✓ Network monitoring enabled")
        except Exception as e:
            print(f"  ⚠ Could not enable network monitoring: {str(e)[:50]}")
            print("  Will use JavaScript interception instead")
        
        try:
            # Try request interception (optional, may not be supported)
            driver.execute_cdp_cmd('Network.setRequestInterception', {
                'patterns': [{'urlPattern': '*api*'}]
            })
        except:
            # Some Chrome versions don't support setRequestInterception
            # We'll use performance logs and JavaScript interception instead
            pass
        
        # Install JavaScript interceptor FIRST, before any API calls happen
        print("  Installing authorization token interceptor...")
        driver.execute_script("""
            window._capturedAuthToken = null;
            window._apiCallsMade = 0;
            window._allRequestHeaders = {};
            
            // Intercept fetch - capture headers BEFORE they're sent
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                const url = args[0];
                const options = args[1] || {};
                let headers = options.headers || {};
                
                if (url.includes('/api/')) {
                    window._apiCallsMade++;
                    // Store all headers for this request
                    window._allRequestHeaders[url] = headers;
                    
                    // Check all header variations (case-insensitive)
                    for (const key in headers) {
                        if (key.toLowerCase() === 'authorization' && headers[key]) {
                            window._capturedAuthToken = headers[key];
                            console.log('✓ Captured auth token from fetch:', headers[key].substring(0, 50) + '...');
                            break;
                        }
                    }
                    
                    // Also try to get headers that might be added automatically
                    // by checking the actual request object after it's created
                    const request = new Request(url, options);
                    if (request.headers) {
                        request.headers.forEach((value, key) => {
                            if (key.toLowerCase() === 'authorization' && value) {
                                window._capturedAuthToken = value;
                                console.log('✓ Captured auth token from Request object:', value.substring(0, 50) + '...');
                            }
                        });
                    }
                }
                return originalFetch.apply(this, args);
            };
            
            // Intercept XMLHttpRequest
            const originalSetRequestHeader = XMLHttpRequest.prototype.setRequestHeader;
            XMLHttpRequest.prototype.setRequestHeader = function(header, value) {
                if (header.toLowerCase() === 'authorization' && value) {
                    window._capturedAuthToken = value;
                    window._apiCallsMade++;
                    console.log('✓ Captured auth token from XHR:', value.substring(0, 50) + '...');
                }
                return originalSetRequestHeader.apply(this, arguments);
            };
            
            // Also intercept XMLHttpRequest open to capture headers set later
            const originalOpen = XMLHttpRequest.prototype.open;
            XMLHttpRequest.prototype.open = function(method, url, ...rest) {
                this._url = url;
                return originalOpen.apply(this, [method, url, ...rest]);
            };
            
            // Intercept send to capture headers right before sending
            const originalSend = XMLHttpRequest.prototype.send;
            XMLHttpRequest.prototype.send = function(...args) {
                if (this._url && this._url.includes('/api/')) {
                    // Try to get all request headers
                    try {
                        const headers = {};
                        // Note: We can't directly access all headers, but we can check
                        // if authorization was set via setRequestHeader
                    } catch(e) {}
                }
                return originalSend.apply(this, args);
            };
            
            console.log('Interceptor installed');
        """)
        time.sleep(2)
        
        # Try to trigger a REAL search on the page (this will use the app's code which adds auth header)
        print("  Attempting to trigger real search on page...")
        search_triggered = False
        try:
            # Look for various search input selectors
            search_input_selectors = [
                "input[type='search']",
                "input[name*='search' i]",
                "input[id*='search' i]",
                "input[placeholder*='search' i]",
                "#search",
                ".search-input",
                "input[type='text']"  # Fallback
            ]
            
            for selector in search_input_selectors:
                try:
                    search_input = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    # Clear and type search term
                    search_input.clear()
                    search_input.send_keys("A")
                    time.sleep(1)
                    # Try to submit
                    search_input.send_keys(Keys.RETURN)
                    print(f"  ✓ Triggered search via input field: {selector}")
                    search_triggered = True
                    time.sleep(8)  # Wait for API call to complete
                    break
                except:
                    continue
            
            # If no search input, try clicking search button
            if not search_triggered:
                search_button_selectors = [
                    "button[type='submit']",
                    "button:contains('Search')",
                    "input[type='submit']",
                    "button.search",
                    "#search-button"
                ]
                for selector in search_button_selectors:
                    try:
                        if ':contains(' in selector:
                            search_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Search')]")
                        else:
                            search_button = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        search_button.click()
                        print(f"  ✓ Clicked search button")
                        time.sleep(8)
                        search_triggered = True
                        break
                    except:
                        continue
        except Exception as e:
            print(f"  ℹ Could not trigger search automatically: {str(e)[:50]}")
        
        # Also try making API call via JavaScript (but interceptor should catch it)
        if not search_triggered:
            print("  Making API call via JavaScript as fallback...")
            # Try the GET endpoint first (as shown in user's network request)
            driver.execute_script("""
                window._apiTestDone = false;
                // Try GET request to /api/search/description/business (as shown in user's example)
                fetch('https://bizfileonline.sos.ca.gov/api/search/description/business', {
                    method: 'GET',
                    headers: {
                        'Accept': '*/*',
                    }
                }).then(r => {
                    window._apiTestDone = true;
                    window._apiResponse = r.status;
                    return r.text();
                }).catch(e => {
                    window._apiTestDone = true;
                    window._apiError = e.toString();
                });
            """)
            time.sleep(5)
            
            # If still no token, try POST request
            if not driver.execute_script("return window._capturedAuthToken;"):
                print("  Trying POST API call as additional fallback...")
                driver.execute_script("""
                    fetch('""" + API_URL + """', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            "SEARCH_VALUE": "A",
                            "SEARCH_FILTER_TYPE_ID": "0",
                            "SEARCH_TYPE_ID": "1",
                            "STATUS_ID": "43"
                        })
                    }).then(r => {
                        return r.text();
                    }).catch(e => {
                        console.error('API call error:', e);
                    });
                """)
                time.sleep(5)
        
        # Wait a bit more for any pending API calls
        time.sleep(3)
        
        # Extract cookies
        print("  Extracting cookies...")
        cookies = driver.get_cookies()
        cookie_string = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
        extracted_cookies = cookie_string
        print(f"  ✓ Extracted {len(cookies)} cookies ({len(cookie_string)} characters)")
        
        # Extract authorization token
        print("  Extracting authorization token...")
        auth_token = None
        
        # Method 1: Check JavaScript interceptor first (most reliable)
        api_calls = driver.execute_script("return window._apiCallsMade || 0;")
        print(f"  API calls detected by interceptor: {api_calls}")
        
        # Get console logs to see if interceptor is working
        console_logs = driver.get_log('browser')
        if console_logs:
            print(f"  Console messages: {len(console_logs)}")
            relevant_logs = []
            for log in console_logs:
                msg = log['message'].lower()
                if 'auth token' in msg or 'captured' in msg or 'interceptor' in msg:
                    relevant_logs.append(log['message'])
            if relevant_logs:
                print(f"  Relevant console messages:")
                for log_msg in relevant_logs[-5:]:  # Show last 5 relevant messages
                    print(f"    {log_msg}")
        
        auth_token = driver.execute_script("return window._capturedAuthToken;")
        if auth_token:
            print(f"  ✓ Found authorization token via JavaScript interceptor")
            print(f"    Token length: {len(auth_token)} characters")
            print(f"    Token preview: {auth_token[:50]}...")
        else:
            print(f"  ⚠ Interceptor did not capture token (API calls: {api_calls})")
            if api_calls == 0:
                print(f"    No API calls were intercepted - the app may not have made any API calls yet")
                print(f"    This could mean:")
                print(f"      - The page hasn't loaded completely")
                print(f"      - The app uses a different method to make API calls")
                print(f"      - The interceptor was installed too late")
            else:
                print(f"    API calls were made but no authorization header was found")
                print(f"    This could mean:")
                print(f"      - The authorization header is added by the browser automatically")
                print(f"      - The header name is different (check case sensitivity)")
                print(f"      - The token is added via a different mechanism")
        
        # Method 2: Use CDP to get actual request headers (including those added by browser/extensions)
        if not auth_token:
            print("  Using Chrome DevTools Protocol to capture actual request headers...")
            try:
                # Get all network requests via CDP
                logs = driver.get_log('performance')
                print(f"  Checking {len(logs)} performance log entries for authorization header...")
                
                api_requests_found = 0
                request_ids = {}  # Map URL to request ID
                
                for log in logs:
                    try:
                        message = json.loads(log['message'])
                        method = message.get('message', {}).get('method', '')
                        params = message.get('message', {}).get('params', {})
                        
                        if method == 'Network.requestWillBeSent':
                            request = params.get('request', {})
                            url = request.get('url', '')
                            request_id = params.get('requestId', '')
                            headers = request.get('headers', {})
                            
                            # Check if this is an API request
                            if '/api/' in url:
                                api_requests_found += 1
                                request_ids[request_id] = url
                                
                                # Check all case variations of authorization header
                                for key in headers.keys():
                                    if key.lower() == 'authorization':
                                        potential_token = headers[key]
                                        if potential_token and len(potential_token) > 50:  # JWT tokens are long
                                            auth_token = potential_token
                                            print(f"  ✓ Found authorization token in performance logs")
                                            print(f"    URL: {url[:80]}...")
                                            print(f"    Token length: {len(auth_token)} characters")
                                            break
                                if auth_token:
                                    break
                    except Exception as e:
                        continue
                
                # Try to get request headers via CDP getResponseBody or getRequestPostData
                if not auth_token and request_ids:
                    print(f"  Attempting to get request headers via CDP for {len(request_ids)} requests...")
                    for request_id, url in list(request_ids.items())[:5]:  # Check first 5 requests
                        try:
                            # Try to get the actual request that was sent
                            # Note: CDP doesn't directly provide a way to get request headers after they're sent
                            # But we can try to get response headers which might give us clues
                            response = driver.execute_cdp_cmd('Network.getResponseBody', {
                                'requestId': request_id
                            })
                            # This won't give us request headers, but confirms the request was made
                        except:
                            # Request might not have a body or might have failed
                            pass
                
                if api_requests_found > 0 and not auth_token:
                    print(f"  ⚠ Found {api_requests_found} API requests but no authorization header in logs")
                    print(f"    The authorization header is likely added by:")
                    print(f"      - Browser's automatic header injection (from cookies/session)")
                    print(f"      - Chrome extensions or service workers")
                    print(f"      - Network layer (before JavaScript can intercept)")
                    print(f"    Trying alternative method: Check JavaScript stored headers...")
                    
                    # Check if JavaScript interceptor stored any headers
                    stored_headers = driver.execute_script("return window._allRequestHeaders || {};")
                    if stored_headers:
                        print(f"    Found {len(stored_headers)} stored request header objects")
                        for url, headers in stored_headers.items():
                            if isinstance(headers, dict):
                                for key, value in headers.items():
                                    if key.lower() == 'authorization' and value:
                                        auth_token = value
                                        print(f"  ✓ Found authorization token in stored headers!")
                                        print(f"    URL: {url[:60]}...")
                                        break
                                if auth_token:
                                    break
                    
                    # Try to inspect responseReceived events for any clues
                    for log in logs:
                        try:
                            message = json.loads(log['message'])
                            method = message.get('message', {}).get('method', '')
                            if method == 'Network.responseReceived':
                                params = message.get('message', {}).get('params', {})
                                response = params.get('response', {})
                                url = response.get('url', '')
                                if '/api/' in url:
                                    status = response.get('status', 0)
                                    if status == 200:
                                        print(f"    ✓ API request succeeded: {url[:60]}... (status: {status})")
                        except:
                            continue
            except Exception as e:
                print(f"  ⚠ Error using CDP: {str(e)[:100]}")
        
        # Method 3: Try to get token from the actual page's JavaScript context
        if not auth_token:
            print("  Checking page's JavaScript context for token...")
            try:
                # Try to access the application's internal state
                auth_token = driver.execute_script("""
                    // Try to find token in various places the app might store it
                    return window.authToken || 
                           window.token || 
                           window.accessToken ||
                           (window.app && window.app.token) ||
                           (window.config && window.config.authToken) ||
                           null;
                """)
                if auth_token:
                    print(f"  ✓ Found token in page's JavaScript context")
            except:
                pass
        
        # Method 4: Check localStorage/sessionStorage
        if not auth_token:
            print("  Checking localStorage/sessionStorage...")
            try:
                auth_token = driver.execute_script("""
                    // Check all possible storage keys
                    let token = null;
                    for (let i = 0; i < localStorage.length; i++) {
                        let key = localStorage.key(i);
                        if (key.toLowerCase().includes('token') || key.toLowerCase().includes('auth')) {
                            token = localStorage.getItem(key);
                            if (token && token.length > 50) break;
                        }
                    }
                    if (!token) {
                        for (let i = 0; i < sessionStorage.length; i++) {
                            let key = sessionStorage.key(i);
                            if (key.toLowerCase().includes('token') || key.toLowerCase().includes('auth')) {
                                token = sessionStorage.getItem(key);
                                if (token && token.length > 50) break;
                            }
                        }
                    }
                    return token;
                """)
                if auth_token:
                    print(f"  ✓ Found token in storage")
            except:
                pass
        
        extracted_token = auth_token
        
        # Step 8: Display results
        print()
        print("=" * 80)
        print("STEP 8: TEST RESULTS")
        print("=" * 80)
        print()
        
        if extracted_cookies:
            print("✓ COOKIES EXTRACTION: SUCCESS")
            print(f"  Total cookies: {len(cookies)}")
            print(f"  Cookie string length: {len(cookie_string)} characters")
            print(f"  Sample cookies: {', '.join([c['name'] for c in cookies[:5]])}...")
        else:
            print("❌ COOKIES EXTRACTION: FAILED")
        
        print()
        
        if extracted_token:
            print("✓ AUTHORIZATION TOKEN EXTRACTION: SUCCESS")
            print(f"  Token length: {len(extracted_token)} characters")
            print(f"  Token preview: {extracted_token[:50]}...")
            
            # Check token expiration
            try:
                import base64
                parts = extracted_token.split('.')
                if len(parts) == 3:
                    payload = parts[1]
                    payload += '=' * (4 - len(payload) % 4)
                    decoded = base64.urlsafe_b64decode(payload)
                    token_data = json.loads(decoded)
                    exp_timestamp = token_data.get('exp')
                    if exp_timestamp:
                        from datetime import datetime
                        exp_datetime = datetime.fromtimestamp(exp_timestamp)
                        now = datetime.now()
                        time_until_expiry = (exp_datetime - now).total_seconds()
                        print(f"  Token expires: {exp_datetime}")
                        print(f"  Time until expiry: {time_until_expiry/3600:.1f} hours")
            except:
                pass
        else:
            print("⚠ AUTHORIZATION TOKEN EXTRACTION: NOT FOUND")
            print("  Note: Token may be added dynamically by the application")
            print("  Cookies alone may be sufficient for API calls")
        
        print()
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        if extracted_cookies:
            print("✓ Login automation: SUCCESS")
            print("✓ Cookie extraction: SUCCESS")
            if extracted_token:
                print("✓ Token extraction: SUCCESS")
            else:
                print("⚠ Token extraction: PARTIAL (cookies extracted, token not found)")
            print()
            print("The automation appears to be working correctly!")
            print("You can now use these credentials in the main script.")
        else:
            print("❌ Login automation: FAILED")
            print("Please check the error messages above.")
        
        # Save credentials to file for inspection
        if extracted_cookies:
            credentials = {
                "cookies": extracted_cookies,
                "token": extracted_token,
                "cookie_count": len(cookies),
                "extraction_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            with open('test_credentials.json', 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=2, ensure_ascii=False)
            print()
            print("Credentials saved to: test_credentials.json")
        
    except Exception as e:
        print()
        print("=" * 80)
        print("TEST FAILED")
        print("=" * 80)
        print(f"Error: {str(e)}")
        import traceback
        print()
        print("Full traceback:")
        traceback.print_exc()
        
    finally:
        if driver:
            try:
                print()
                print("Closing browser...")
                driver.quit()
                print("✓ Browser closed")
            except:
                pass

if __name__ == "__main__":
    test_headless_login()

