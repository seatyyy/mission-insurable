import asyncio
import os
from distutils.util import strtobool
from typing import List, Optional

from pydantic import BaseModel, Field
from browser_use import Browser, BrowserConfig, Agent as BrowserAgent, Controller
from pydantic_ai import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


load_dotenv(verbose=False)

USE_MOCK_DATA = strtobool(os.environ.get("USE_MOCK_DATA", "False"))
DEMO = strtobool(os.environ.get("DEMO", "True"))

class ResearchedData(BaseModel):
    build_date: Optional[str] = Field(None, description="Date when the building was constructed")
    bedrooms: Optional[str] = Field(None, description="Number of bedrooms in the property")
    bathrooms: Optional[str] = Field(None, description="Number of bathrooms in the property")
    stories: Optional[str] = Field(None, description="Number of stories in the property")
    lot_size: Optional[str] = Field(None, description="Size of the property lot")
    construction_type: Optional[str] = Field(None, description="Type of construction (frame, masonry, fire resistant)")
    seismic_zone: Optional[bool] = Field(None, description="Whether the property is located in a seismic zone")

    # Original fields from task description can be added here as needed
    occupancy_type: Optional[str] = None
    building_value: Optional[str] = None
    year_built: Optional[str] = None
    square_footage: Optional[str] = None
    basement: Optional[bool] = None
    sprinkler_system: Optional[bool] = None
    roof_type: Optional[str] = None


browser = Browser(
    config=BrowserConfig(
        headless=True,
        cdp_url="http://localhost:9222"
        # chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS path
    )
)
llm = ChatOpenAI(model="gpt-4o-mini")
task_template = """
perform the following task
{task}
"""

information_retrieval_1_template = """
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

information_retrieval_2_template = """
Extract all useful information about property
Everything that you can extract about address, lot, construction, sales, zoning, area and not limited to that.
Extract everything you can extract about property
"""


async def research_gov_website(address: str, website: str, retrieval_template: str) -> str:
    task = f"""
    Open the webiste: {website}
    Extract information about address: {address}
    {retrieval_template}
    Try to find as much information as possible
    If you see PDF file on the website - do not try to extract information from it, just extract the url of this file.
    Return all information that you have extracted in on big json
    """
    controller = Controller()
    result = await run_browser_agent(task, controller)
    return result


async def search(address: str):
    results = []

    if not USE_MOCK_DATA:
        result = await research_gov_website(address, "https://a810-bisweb.nyc.gov/bisweb/bispi00.jsp",
                                            information_retrieval_2_template)
        results.append(result)

        if not DEMO:

            result = await research_gov_website(address, "https://a810-dobnow.nyc.gov/publish/Index.html#!/",
                                                information_retrieval_2_template)
            results.append(result)

            result = await research_gov_website(address,
                                                "https://a810-bisweb.nyc.gov/bisweb/PropertyProfileOverviewServlet?boro=1&houseno=200&street=Madison+Ave&go2=+GO+&requestid=0",
                                                information_retrieval_2_template)
            results.append(result)

            result = await research_gov_website(address,
                                                "https://www.propertyshark.com/mason/Property/13364/200-Madison-Ave-New-York-NY-10016/",
                                                information_retrieval_2_template)
            results.append(result)
    else:
        with open("browser_agent/property_shark_data.md", "r") as file:
            results.append(file.read())
        with open(f"browser_agent/nyc.gov.txt", "r") as file:
            results.append(file.read())

    if DEMO:
        return ResearchedData(
            build_date="1926",
            bedrooms="NA",
            bathrooms="NA",
            lot_size="197.5 ft x 220 ft",
            construction_type="Office Only with or without Commercial - 20 Stories or More (O4)",
            seismic_zone=False,
            stories="20"
        )

    return await summarize_info(results)



async def general_search(address: str):
    task = f"""    
        Research the information about {address} in different webistes.
        {information_retrieval_1_template}
        Try to find as much information as possible
        Present the information in a structured format
        """

    controller = Controller()
    result = await run_browser_agent(task, controller)
    return result.model_dump()


async def summarize_info(results: List[str]):
    agent = Agent(
        'openai:gpt-4o',
        result_type=ResearchedData,
        system_prompt=(
            f"You're helping assistant that can summarize the data. "
            f"You take the unstructured data from Researcher and structure it "
            f"into the format:\n{ResearchedData.model_json_schema()}"
        ),
    )
    result = await agent.run("\n".join(results), result_type=ResearchedData)
    print(result)


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
    # final_result = result.final_result()
    final_result = ""
    for item in result.history:
        for res in item.result:
            final_result += "\n" + res.extracted_content

    return final_result


if __name__ == '__main__':
    address = "200 Madison Ave, New York"
    res = asyncio.run(search(address))
    print(res)

