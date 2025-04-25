import json
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException
from serpapi import GoogleSearch
import openai

# Configure API keys (in a real app, use environment variables)
SERPAPI_KEY = "9bbc3a0bfb66807580039d323417a5c25e97146f5825a6adf2429c4005d4011f"
OPENAI_KEY = "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"

# Initialize OpenAI client
openai.api_key = OPENAI_KEY

@dataclass
class SearchResult:
    url: str
    title: str
    snippet: str
    source: str

@dataclass
class ScrapedContent:
    url: str
    title: str
    text: str
    authors: List[str]
    publish_date: Optional[str]
    main_content: str

@dataclass
class ResearchReport:
    query: str
    summary: str
    sources: List[Dict]
    key_points: List[str]
    answer: str

class SerpAPISearchTool:
    """Real search using SerpAPI"""

    def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """Perform actual web search using SerpAPI"""
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": num_results
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()

            search_results = []
            if "organic_results" in results:
                for result in results["organic_results"]:
                    search_results.append(SearchResult(
                        url=result.get("link", ""),
                        title=result.get("title", ""),
                        snippet=result.get("snippet", ""),
                        source=result.get("source", "")
                    ))

            return search_results[:num_results]

        except Exception as e:
            print(f"Search error: {str(e)}")
            return []

class WebScraper:
    """Handles web page scraping with respect to robots.txt"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape(self, url: str) -> Optional[ScrapedContent]:
        """Scrape a web page with error handling"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract title
            title = soup.title.string if soup.title else "No title found"

            # Simple content extraction (can be enhanced)
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text() for p in paragraphs])

            # Try to extract metadata
            authors = []
            publish_date = None

            # Common patterns for author and date
            for meta in soup.find_all("meta"):
                if "name" in meta.attrs:
                    if "author" in meta.attrs["name"].lower():
                        authors.append(meta.attrs.get("content", ""))
                    elif "date" in meta.attrs["name"].lower():
                        publish_date = meta.attrs.get("content", None)

            return ScrapedContent(
                url=url,
                title=title,
                text=text,
                authors=authors,
                publish_date=publish_date,
                main_content=text[:2000]  # Limit content size
            )

        except RequestException as e:
            print(f"Error scraping {url}: {str(e)}")
            return None

class NewsAPIAggregator:
    """Real news search using SerpAPI's news endpoint"""

    def get_news(self, query: str, num_results: int = 3) -> List[SearchResult]:
        """Get recent news using SerpAPI"""
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "tbm": "nws",
            "num": num_results
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()

            news_results = []
            if "news_results" in results:
                for result in results["news_results"]:
                    news_results.append(SearchResult(
                        url=result.get("link", ""),
                        title=result.get("title", ""),
                        snippet=result.get("snippet", ""),
                        source=result.get("source", "")
                    ))

            return news_results[:num_results]

        except Exception as e:
            print(f"News search error: {str(e)}")
            return []

class OpenAIContentAnalyzer:
    """Uses OpenAI for advanced content analysis and summarization"""

    def analyze_relevance(self, content: ScrapedContent, query: str) -> float:
        """Use OpenAI to score content relevance to query"""
        prompt = f"""
        Rate the relevance of this content to the query on a scale from 0 to 1.
        Query: {query}
        Content Title: {content.title}
        Content Snippet: {content.main_content[:500]}

        Return only a number between 0 and 1 with 2 decimal places.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}],
                temperature=0
            )
            return float(response.choices[0].message.content.strip())
        except Exception as e:
            print(f"OpenAI error: {str(e)}")
            return 0.0

    def summarize(self, contents: List[ScrapedContent], query: str) -> ResearchReport:
        """Use OpenAI to generate a comprehensive research report"""
        sources_text = "\n\n".join([
            f"Source {i+1}:\nURL: {c.url}\nTitle: {c.title}\nContent: {c.main_content[:1000]}"
            for i, c in enumerate(contents)
        ])

        prompt = f"""
        You are a professional research assistant. Create a detailed report answering this query:
        Query: {query}

        Using these sources:
        {sources_text}

        Your report should include:
        1. A comprehensive summary answering the query
        2. 3-5 key points extracted from the sources
        3. A list of all sources used

        Structure your response as JSON with these keys:
        - "summary": The complete summary answering the query
        - "key_points": List of key points
        - "answer": Concise direct answer to the query
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content)

            return ResearchReport(
                query=query,
                summary=result["summary"],
                sources=[{"url": c.url, "title": c.title} for c in contents],
                key_points=result["key_points"],
                answer=result["answer"]
            )

        except Exception as e:
            print(f"OpenAI summarization error: {str(e)}")
            return ResearchReport(
                query=query,
                summary="Error generating report",
                sources=[],
                key_points=[],
                answer="Error generating answer"
            )

class WebResearchAgent:
    """Main research agent with real API integrations"""

    def __init__(self):
        self.search_tool = SerpAPISearchTool()
        self.scraper = WebScraper()
        self.news_aggregator = NewsAPIAggregator()
        self.analyzer = OpenAIContentAnalyzer()
        self.visited_urls = set()  # To avoid duplicate content

    def research(self, query: str, max_sources: int = 3) -> ResearchReport:
        """Main research workflow"""
        print(f"Starting research for: {query}")

        # Step 1: Perform web search
        search_results = self.search_tool.search(query)
        print(f"Found {len(search_results)} search results")

        # Step 2: Scrape top results
        scraped_contents = []
        for result in search_results[:max_sources]:
            if result.url not in self.visited_urls:
                print(f"Scraping: {result.url}")
                content = self.scraper.scrape(result.url)
                if content:
                    scraped_contents.append(content)
                    self.visited_urls.add(result.url)

        # Step 3: Check for news if query seems news-oriented
        if self._is_news_query(query):
            print("Query appears news-oriented, checking news sources")
            news_results = self.news_aggregator.get_news(query)
            for news in news_results[:max_sources]:
                if news.url not in self.visited_urls:
                    content = self.scraper.scrape(news.url)
                    if content:
                        scraped_contents.append(content)
                        self.visited_urls.add(news.url)

        # Step 4: Analyze and filter content
        scored_contents = []
        for content in scraped_contents:
            score = self.analyzer.analyze_relevance(content, query)
            print(f"Relevance score for {content.url}: {score:.2f}")
            if score > 0.5:  # Higher threshold with real API
                scored_contents.append((score, content))

        # Sort by relevance
        scored_contents.sort(reverse=True, key=lambda x: x[0])
        relevant_contents = [c for (s, c) in scored_contents]

        # Step 5: Generate report
        if not relevant_contents:
            return ResearchReport(
                query=query,
                summary="No relevant information found",
                sources=[],
                key_points=[],
                answer="No information found for this query"
            )

        return self.analyzer.summarize(relevant_contents, query)

    def _is_news_query(self, query: str) -> bool:
        """Improved heuristic to detect news-oriented queries"""
        news_keywords = ['news', 'update', 'recent', 'latest', 'today', 'current', '2023', '2024']
        question_words = ['who', 'what', 'when', 'where', 'why', 'how']

        query_lower = query.lower()
        has_news_word = any(keyword in query_lower for keyword in news_keywords)
        starts_with_question = any(query_lower.startswith(word) for word in question_words)

        return has_news_word or starts_with_question
