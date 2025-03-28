from pydantic import BaseModel
from typing import Union
from typing import Literal
from typing import Optional

class userInput(BaseModel):
    skill:str
    location:str
    pagenumber:int


class indeedInput(BaseModel):
    #site_name: Union[str, Literal["indeed", "google"]]
    search_term:str
    google_search_term: Optional[str]
    location:str 
    results_wanted:int = 20
    hours_old:int = 12
    country_indeed:str = "usa"



