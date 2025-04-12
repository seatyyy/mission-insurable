import asyncio
from pydantic import BaseModel
from browser_use import Browser, BrowserConfig, Agent, Controller
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


load_dotenv(verbose=True)


class ResearchedData(BaseModel):
    pass


browser = Browser(
    config=BrowserConfig(
        headless=True,
        cdp_url="http://localhost:9222"
        # chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS path
    )
)
llm = ChatOpenAI(model="gpt-4o")
task_template = """
perform the following task
{task}
"""


async def search(address: str):
    task = f"""    
    Research the information about {address} in different webistes.
    Information that is needed for this address is:
    
    - Occupancy type (list tenants in comments)	
    - Building  Value
    - Tenant Improvements & Betterments
    - Business Personal Property Value
    - Stock
    - Outdoor Property - fences,, gazebos, towers
    - Business Income / Rental Income
    - Total Insured Value
    - Construction Type
    - Year Built 
    - # of Stories
    - Gross Area / Square Footage
    - Gross Area / Square Footage of indoor or covered parking
    - Habitational square footage
    - % Occupied
    - Basement  Y/N
    - Sprinkler System  Y/N
    - Sprinkler System type & % of area protected (wet, dry, ESFR, Foam /  GPM rating)
    - Fire Detection:  Heat or Smoke Batttery Operated  Auto/Manual  Local/Central Station
    - Sec Sys Y/N	
    - Security System Type & Monitoring	Electrical Updates  (type & year completed)
    - Electrical - Any knob & tube wiring, aluminum wiring, fuse boxes (describe)
    - Plumbing Updates (type & year completed)
    - HVAC Updates (type & year completed)
    - Roofing Updates (type & year completed)
    - Roof Type
    - Roof Material
    - Solar Panels
    - Additional Comments on occupancy / updates / unique features /historical register / etc.  (include rent rolls and list of tenants on separate sheet for leased buildings)
    
    Try to find as much information as possible
    Present the information in a structured format
    """

    controller = Controller()
    result = await run_browser_agent(task, controller)
    return result.model_dump()


async def run_browser_agent(task: str, controller: Controller):
    """Run the browser-use agent with the specified task."""
    agent = Agent(
        task=task_template.format(task=task),
        browser=browser,
        llm=llm,
        controller=controller
    )

    result = await agent.run()
    await browser.close()
    result = result.final_result()
    return result


if __name__ == '__main__':
    asyncio.run(search("200 Madison Ave, Manhattan NY"))