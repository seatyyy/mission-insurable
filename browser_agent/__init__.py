import asyncio
from pydantic import BaseModel, Field
from typing import Optional
from browser_use import Browser, BrowserConfig, Agent, Controller
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
    
    Additionally, research the following information if not included above:
    - Build date (when was the property constructed)
    - Number of bedrooms and bathrooms
    - Lot size
    - Construction type (specifically whether it's frame, masonry, or fire resistant)
    - Is the address in a seismic zone (areas prone to earthquakes)
    
    Try to find as much information as possible
    Present the information in a structured format
    """

    controller = Controller()
    result = await run_browser_agent(task, controller)
    
    # Convert the result to a ResearchedData object
    # The result contains key-value pairs that need to be parsed
    data_dict = {}
    
    # Parse the result and extract the required fields
    # This is a simple approach - you might need a more sophisticated parsing
    # based on the actual structure of the result
    try:
        # Convert result to a dictionary if it's not already
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
        else:
            result_dict = result
            
        # Map fields from result to ResearchedData fields
        # This mapping should be adjusted based on the actual output format
        data_dict = {
            'build_date': result_dict.get('build_date') or result_dict.get('year_built'),
            'bedrooms': result_dict.get('bedrooms'),
            'bathrooms': result_dict.get('bathrooms'),
            'lot_size': result_dict.get('lot_size'),
            'construction_type': result_dict.get('construction_type'),
            'seismic_zone': result_dict.get('seismic_zone'),
            # 'occupancy_type': result_dict.get('occupancy_type'),
            # 'building_value': result_dict.get('building_value'),
            # 'year_built': result_dict.get('year_built'),
            # 'stories': result_dict.get('stories') or result_dict.get('# of stories'),
            # 'square_footage': result_dict.get('square_footage') or result_dict.get('gross_area'),
            # 'basement': result_dict.get('basement'),
            # 'sprinkler_system': result_dict.get('sprinkler_system'),
            # 'roof_type': result_dict.get('roof_type')
        }
    except Exception as e:
        print(f"Error parsing result: {e}")
        # Return the original result if parsing fails
        return result
    
    # Create and return a ResearchedData object
    return ResearchedData(**data_dict)


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