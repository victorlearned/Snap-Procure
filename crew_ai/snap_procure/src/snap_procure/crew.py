from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Dict, Any
from snap_procure.tools.scraper import ProcurementScraper
import pandas as pd
import os

@CrewBase
class SnapProcure():
    """
    SnapProcure - A procurement assistant that helps find and compare
    construction materials from various suppliers.
    """

    agents: List[BaseAgent]
    tasks: List[Task]
    scraper: ProcurementScraper = ProcurementScraper(output_dir='data')

    @agent
    def data_collector(self) -> Agent:
        """Agent responsible for collecting product data from various suppliers."""
        return Agent(
            config=self.agents_config['data_collector'],
            tools=[],  # Can add tools here if needed
            verbose=True,
            allow_delegation=False
        )

    @agent
    def procurement_analyst(self) -> Agent:
        """Agent responsible for analyzing product options and making recommendations."""
        return Agent(
            config=self.agents_config['procurement_analyst'],
            verbose=True,
            allow_delegation=False
        )

    @task
    def collect_supplier_data(self) -> Task:
        """Task to collect product data from various suppliers."""
        return Task(
            config=self.tasks_config['collect_supplier_data'],
            agent=self.data_collector(),
            output_file='data/raw_products.json',
            callback=self._scrape_products
        )

    @task
    def analyze_suppliers(self) -> Task:
        """Task to analyze and compare products from different suppliers."""
        return Task(
            config=self.tasks_config['analyze_suppliers'],
            agent=self.procurement_analyst(),
            context=[self.collect_supplier_data()],
            output_file='data/analysis_report.md'
        )

    @task
    def generate_recommendation(self) -> Task:
        """Task to generate a final purchase recommendation."""
        return Task(
            config=self.tasks_config['generate_recommendation'],
            agent=self.procurement_analyst(),
            context=[self.analyze_suppliers()],
            output_file='data/recommendation.md'
        )

    def _scrape_products(self, task_output: str) -> str:
        """
        Callback function to handle product scraping.
        
        Args:
            task_output: The output from the previous task
            
        Returns:
            str: Status message about the scraping operation
        """
        try:
            # Extract product information from the task output
            # This is a simplified example - you might want to parse the output more carefully
            product = task_output.split("product: ")[1].split("\n")[0].strip()
            
            # Scrape data from all configured stores
            df = self.scraper.scrape_all_stores(product)
            
            if df.empty:
                return "No products found. Please try a different search term."
                
            return f"Successfully scraped {len(df)} products. Proceed with analysis."
            
        except Exception as e:
            return f"Error during scraping: {str(e)}"

    @crew
    def crew(self) -> Crew:
        """Creates the SnapProcure crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
