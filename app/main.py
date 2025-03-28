
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import schemas
from . import jobs

app=FastAPI()
origions=["*"] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origions,#domains which 
    allow_credentials=True,
    allow_methods=["*"],# allow specific mehods(get,update)
    allow_headers=["*"],#allwo which headers
)


jobscr = jobs.JobScraper()


@app.get("/") #decorator
async def root():
    return {"message": f"The API is working ! "}

@app.post("/linkdin/get")
def get_LIposts(title:schemas.userInput):
    linkdin=jobscr.search_linkedin(title.skill,title.location,title.pagenumber)

    return linkdin

@app.post("/ziprecuter/get")
def get_zip(title:schemas.userInput):
    ziprecuter = jobscr.search_ziprecruiter(title.skill,title.location, title.pagenumber)
    return ziprecuter

@app.post('/indeed/get')
def get_indeed(title:schemas.indeedInput):

    indeed = jobscr.search_with_jobspy(title.search_term, title.google_search_term)
    return indeed