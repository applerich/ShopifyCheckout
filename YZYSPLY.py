#-*- coding: utf-8 -*-
import requests, time, json, sys, datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from config import *

session = requests.session()

chromedriver = "/Users/alexb_000/Documents/CODING/gui/bin/chromedriver"
driver = webdriver.Chrome(chromedriver)
#urlOfCrappyItem = raw_input("Enter Yeezy Link: ")
#urlOfYeezy = raw_input("Enter Yeezy Link: ")

urlOfYeezy = "https://yeezysupply.com/products/mens-combat-boot-light-sand/"
cartLink = "https://yeezysupply.com/cart/"
shopifyServerCheckoutLink = "https://purchase.yeezysupply.com"
size = "42"

def writeToFile(message):
    with open('logFile.txt','a') as logFile:
        logFile.write(message)

def scrapeForVariant():
    ##############################################################################
    #VARIANT SCRAPING ADDING TO CART AND GETTING TO CUSTOMER INFO PAGE, ALSO SET UP FOR QUEUE BYPASS
    ##############################################################################

    writeToFile('\nNEW SHOPIFY SESSION\n' + str(datetime.datetime.now()) + "\n\n")

    try:
        driver.get(urlOfYeezy)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        selectSizesTag = soup.findAll('option')
        for item in selectSizesTag:
            if size in item:
                global variantOfYeezy
                variantOfYeezy = item['value']
    except Exception as e:
        writeToFile(e)
        frontEndCheckout()

    writeToFile('Got the variant of desired shoe.\n')

def submitCustomerInfo():
    ##############################################################################
    #GENERATING CHECKOUT LINK, SUBMITTING CUSTOMER INFO, GETTING COOKIES AND GETTING TO SHIPPING PAGE
    ##############################################################################

    submitCustomerInfoHeaders = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'en-US,en;q=0.8',
        'Connection':'keep-alive',
        'Content-Type':'application/x-www-form-urlencoded',
        'Origin':shopifyServerCheckoutLink,
        'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    try:
        resp = session.get(cartLink+variantOfYeezy+":1", allow_redirects=True, headers=submitCustomerInfoHeaders, timeout=4)
    except Exception as e:
        writeToFile(e)
        frontEndCheckout()

    if 'Continue to shipping method' in resp.content:
        writeToFile('Got to Customer Information Page.\n')

    global shopifyGeneratedCheckoutLink
    shopifyGeneratedCheckoutLink = resp.url

    soup = BeautifulSoup(resp.content, 'html.parser')
    authenticity_token = soup.findAll('input', {'name':'authenticity_token'})[2]['value']

    customerInfoData = {
        #params to pass
        'utf8' : '✓',
        '_method' : 'patch',
        'authenticity_token' : authenticity_token,
        'previous_step' : 'contact_information',
        'step':'shipping_method',
        'checkout[email]' : email,
        'checkout[buyer_accepts_marketing]' : '0',
        'checkout[buyer_accepts_marketing]' : '1',
        'checkout[shipping_address][first_name]' : firstName,
        'checkout[shipping_address][last_name]': lastName,
        'checkout[shipping_address][address1]' : address1,
        'checkout[shipping_address][address2]' : address2,
        'checkout[shipping_address][city]' : city,
        'checkout[shipping_address][country]' : country,#United States
        'checkout[shipping_address][province]' : province, #Ohio
        'checkout[shipping_address][zip]' : zipCode,
        'checkout[shipping_address][phone]' : phone, #no spaces
        'checkout[shipping_address][first_name]' : firstName,
        'checkout[shipping_address][last_name]' : lastName,
        'checkout[shipping_address][address1]' : address1,
        'checkout[shipping_address][address2]' : address2,
        'checkout[shipping_address][city]' : city,
        'checkout[shipping_address][country]' : country,
        'checkout[shipping_address][province]' : province,
        'checkout[shipping_address][zip]' : zipCode,
        'checkout[shipping_address][phone]' : phone,
        'g-recaptcha-response' : '',
        'button' : '',
        'checkout[client_details][browser_width]' : '527',
        'checkout[client_details][browser_height]' : '620',
        'checkout[client_details][javascript_enabled]' : '1'
    }

    try:
        resp = session.post(shopifyGeneratedCheckoutLink, data=customerInfoData, allow_redirects=True,timeout=4)
    except Exception as e:
        writeToFile(e)
        frontEndCheckout()

    if(resp.status_code == 200):
        writeToFile('Successfully submitted customer info to shopify server.\n')
    else:
        sys.exit()

    #IMPLEMENT THE CAPTCHA BYPASS HERE

    resp = session.get(shopifyGeneratedCheckoutLink+"?previous_step=shipping_method&step=payment_method", allow_redirects=True, timeout=4)

    if 'Complete order' or 'Complete order'.upper in resp.content:
        writeToFile('Successfully bypassed captcha and got to payment method page.\n')

    soup = BeautifulSoup(resp.content, 'html.parser')

    global newAuthToken
    newAuthToken = soup.findAll('input', {'name':'authenticity_token'})[2]['value']

def submitPayment():
    ##############################################################################
    #SUBMITTING SHIPPING METHOD, GET TO PAYMENT METHOD PAGE
    ##############################################################################

    submitPaymentSessionHeaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
        'Content-Type': 'application/json'
    }

    ccINfo = {
        "credit_card": {
        "number": cardNumber,
        "name": cardFirstNameAndLastName,
        "month": cardMonth,
        "year": cardYear,
        "verification_value": CVV
        }
    }

    try:
        r = session.post('https://elb.deposit.shopifycs.com/sessions', data=json.dumps(ccINfo), headers = submitPaymentSessionHeaders, timeout=4, allow_redirects=True)
    except Exception as e:
        writeToFile(e)
        frontEndCheckout()

    if r.status_code == 200:
        writeToFile('Retrieved unique session ID.\n')
    else:
        writeToFile(str(r.status_code)+"\n")

    sessionIDvalue = json.loads(str(r.text))

def frontEndCheckout():
    print('No function yet')

if __name__ == "__main__":
    scrapeForVariant()
    submitCustomerInfo()
    submitPayment()
