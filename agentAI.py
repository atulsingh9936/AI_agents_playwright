import asyncio
import os
from browser_use.agent.service import Agent
from browser_use.agent.views import ActionResult
from browser_use.browser.context import BrowserContext
from browser_use.controller.service import Controller
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr, BaseModel





class  CheckoutResult(BaseModel):
    login_status:str
    cart_status:str
    checkout_status:str
    total_update_status:str
    delivery_location_status:str
    confirmation_message:str



controller= Controller(output_model=CheckoutResult)

@controller.action("open base website")
async def open_website(browser:BrowserContext):
  page=  await browser.get_current_page()
  await page.goto("https://rahulshettyacademy.com/loginpagePractise/")
  return ActionResult(extracted_content='browser opened')



@controller.action('Get attribute and url of the page')
async def get_attr_url(browser:BrowserContext):
 page = await browser.get_current_page()
 current_url=page.url
 attr= await page.get_by_text("Shop Name").get_attribute('class')
 print(current_url)
 return  ActionResult(extracted_content=f'current url is {current_url} a nd att is {attr}')


async def SiteValidation():
    """
    This function defines an asynchronous test case for validating a website.
    It uses an agent to perform UI automation tasks on the specified website.
    """
    os.environ["Gemini_API_KEY"] = "AIzaSyCqDDJp5zxcnRqCPGdmFpG9V5Gz-hOOnaU"

    task = (
        "Important: I am a UI Automation tester validating the tasks. "
        "Open base website"
        "Login with username and password. Login details are available on the same page. "
        "Get attribute and url of the page"
        "After login, select the first 2 products and add them to the cart. "
        "Then checkout and store the total value you see on the screen. "
        "Increase the quantity of any product and check if the total value updates accordingly. "
        "Checkout and select a country, agree to terms, and purchase. "
        "Verify that the 'Thank you' message is displayed."
    )
    api_key = os.environ["Gemini_API_KEY"]
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", api_key=SecretStr(api_key))
    agent = Agent(task=task,
                  llm=llm,
                  controller=controller,
                  use_vision=True)
    history = await agent.run()
    history.save_to_file('agentresult.json')
    test_result = history.final_result()
    validated_result=  CheckoutResult.model_validate_json(test_result)
    print(test_result)
    assert validated_result.confirmation_message=="Success! Thank you! Your order will be delivered in next few weeks :-)."

asyncio.run(SiteValidation())
