from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from src.snap_procure.tools.scraper import ProcurementScraper

@CrewBase
class SnapProcure:
    """
    SnapProcure - A conversational assistant that helps general contractors
    with custom procurement queries.
    """

    agents: List[BaseAgent]
    tasks: List[Task]
    scraper: ProcurementScraper = ProcurementScraper(output_dir='data')

    @agent
    def order_manager(self) -> Agent:
        """Agent that chats with the user and assists general contractors."""
        return Agent(
            config=self.agents_config['order_manager'],
            tools=[],
            verbose=True,
            allow_delegation=True
        )

    @agent
    def data_collector(self) -> Agent:
        """Agent responsible for collecting product data from suppliers."""
        return Agent(
            config=self.agents_config['data_collector'],
            tools=[],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def procurement_analyst(self) -> Agent:
        """Agent responsible for analyzing and recommending products."""
        return Agent(
            config=self.agents_config['procurement_analyst'],
            verbose=True,
            allow_delegation=False
        )

    @task
    def chat(self) -> Task:
        """Task for handling user chat interactions."""
        return Task(
            config=self.tasks_config['chat'],
            agent=self.order_manager()
        )

    @task
    def collect_supplier_data(self) -> Task:
        return Task(
            config=self.tasks_config['collect_supplier_data'],
            agent=self.data_collector(),
            output_file='data/raw_products.json',
            callback=self._scrape_products
        )

    @task
    def analyze_suppliers(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_suppliers'],
            agent=self.procurement_analyst(),
            context=[self.collect_supplier_data()],
            output_file='data/analysis_report.md'
        )

    @task
    def generate_recommendation(self) -> Task:
        return Task(
            config=self.tasks_config['generate_recommendation'],
            agent=self.procurement_analyst(),
            context=[self.analyze_suppliers()],
            output_file='data/recommendation.md'
        )

    def _scrape_products(self, task_output: str) -> str:
        try:
            product = task_output.split("product: ")[1].split("\n")[0].strip()
            df = self.scraper.scrape_all_stores(product)
            if df.empty:
                return "No products found. Please try a different search term."
            return f"Successfully scraped {len(df)} products. Proceed with analysis."
        except Exception as e:
            return f"Error during scraping: {str(e)}"

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.data_collector(),
                self.procurement_analyst()
            ],
            tasks=[self.chat()],
            manager_agent=self.order_manager(),
            process=Process.hierarchical,
            verbose=True
        )


# def run_chatbot():
#     bot = SnapProcure()
#     print("🤖 SnapProcure Chatbot: assisting general contractors! (type 'exit' to quit)")
#     while True:
#         user_input = input("You: ")
#         if user_input.lower() in ("exit", "quit"):
#             print("Goodbye!")
#             break
#         crew_instance = bot.crew()
#         response = crew_instance.kickoff(
#             inputs={
#                 "user_request": user_input,
#                 "product": user_input  # Assuming the user input is the product they're inquiring about
#             }
#         )
#         print(f"Bot: {response}\n")

# if __name__ == "__main__":
#     run_chatbot()
