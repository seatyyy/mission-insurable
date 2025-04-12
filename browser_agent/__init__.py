import asyncio
from typing import List

from pydantic import BaseModel
from browser_use import Browser, BrowserConfig, Agent as BrowserAgent, Controller
from pydantic_ai import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


load_dotenv(verbose=True)


class ResearchedData(BaseModel):
    build_date: Optional[str] = Field(None, description="Date when the building was constructed")
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms in the property")
    bathrooms: Optional[float] = Field(None, description="Number of bathrooms in the property")
    lot_size: Optional[str] = Field(None, description="Size of the property lot")
    construction_type: Optional[str] = Field(None, description="Type of construction (frame, masonry, fire resistant)")
    seismic_zone: Optional[bool] = Field(None, description="Whether the property is located in a seismic zone")

    # Original fields from task description can be added here as needed
    # occupancy_type: Optional[str] = None
    # building_value: Optional[str] = None
    # year_built: Optional[str] = None
    # stories: Optional[int] = None
    # square_footage: Optional[str] = None
    # basement: Optional[bool] = None
    # sprinkler_system: Optional[bool] = None
    # roof_type: Optional[str] = None


browser = Browser(
    config=BrowserConfig(
        headless=True,
        # cdp_url="http://localhost:9222"
        chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS path
    )
)
llm = ChatOpenAI(model="gpt-4o")
task_template = """
perform the following task
{task}
"""

information_template = """
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
"""


async def research_gov_website(address: str, website: str):
    task = f"""
    Research webiste: {website}
    To find information about address: {address}
    {information_template}
    Try to find as much information as possible
    If you see PDF file on the website - do not try to extract information from it, just extract the url of this file.
    Present the information in a structured format
    """
    controller = Controller()
    result = await run_browser_agent(task, controller)
    return result


async def search(address: str):
    task = f"""    
    Research the information about {address} in different webistes.
    {information_template}
    Try to find as much information as possible
    Present the information in a structured format
    """

    controller = Controller()
    result = await run_browser_agent(task, controller)
    return result.model_dump()


async def summarize_info(results: List[str]):
    pass


async def run_browser_agent(task: str, controller: Controller):
    """Run the browser-use agent with the specified task."""
    agent = BrowserAgent(
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
    address = "200 Madison Ave, Manhattan NY"
    # asyncio.run(search(address))

    results = []
    # result = asyncio.run(research_gov_website(address, "https://a810-dobnow.nyc.gov/publish/Index.html#!/"))
    # result.append(result)

    # result = asyncio.run(research_gov_website(address, "https://a810-bisweb.nyc.gov/bisweb/PropertyProfileOverviewServlet?boro=1&houseno=200&street=Madison+Ave&go2=+GO+&requestid=0"))
    # results.append(result)
    # print(result)


