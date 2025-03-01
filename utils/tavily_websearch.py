# from langchain_community.tools.tavily_search import TavilySearchResults , TavilyAnswer
from langchain.tools.tavily_search import TavilySearchResults , TavilyAnswer
import os
from dotenv import load_dotenv
load_dotenv()

api_key_t = os.getenv("TAVILY_API_KEY")

search = TavilySearchResults(
  name="tavily_search_engine",
  description="A web search engine that provides accurate information as well as all related information for the user query.",
  max_results=8,
  search_depth="advanced",
  include_answer=True,
  include_raw_content=True,
  include_images=False,
  verbose=False,
)
searchnn = TavilyAnswer()
