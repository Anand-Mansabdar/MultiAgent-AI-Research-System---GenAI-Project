from agents import build_search_agent, build_scrape_agent, writer_chain, critic_chain

def execute_research_pipeline(topic: str) -> dict :
  state = {}
  # Implementing Search Agent Working
  print("\n-------------------------------------------------")
  print("Step 1 : Search Agent Working...")
  print("-------------------------------------------------")
  
  search_agent = build_search_agent()
  search_agent_result = search_agent.invoke({
    "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
  })
  
  state["search_results"] = search_agent_result['messages'][-1].content
  
  print("\nSearch Agent Result: ", state['search_results'])
  
  print("\n-------------------------------------------------")
  print("Step 2 : Scraping Agent Working...")
  print("-------------------------------------------------")
  scrape_agent = build_scrape_agent()
  scrape_agent_result = scrape_agent.invoke({
    "messages": [("user",
      f"Based on the following search results about '{topic}', "
      f"pick the most relevant URL and scrape it for deeper content.\n\n"            f"Search Results:\n{state['search_results'][:800]}"
    )]
  })
  
  state['scrape_content'] = scrape_agent_result['messages'][-1].content
  
  print("\nScraped Agent Result :",state['scrape_content'])
  
  
  print("\n-------------------------------------------------")
  print("Step 3 : Drafting the report (Search Agent + Scraping Agent)...")
  print("-------------------------------------------------")
  
  combined_research = (
    f"SEARCH RESULTS : \n {state['search_results']} \n\n",
    f"SCRAPED CONTENT : \n {state['scrape_content']} \n\n"
  )
  
  state['report'] = writer_chain.invoke({
    "topic": topic,
    "research": combined_research
  })
  print("\nFinal Report:\n", state['report'])
  
  
  # CRITIC REPORT
  print("\n-------------------------------------------------")
  print("Step 4 : Drafting the critic report...")
  print("-------------------------------------------------")
  
  state['critic_report'] = critic_chain.invoke({
    "report": state['report']
  })
  print("\nCritic Report: \n",state['critic_report'])
  
  return state
  

if __name__ == "__main__":
  topic = input("Enter a topic: ")
  execute_research_pipeline(topic=topic)