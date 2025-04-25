# 🔍 Web Research Agent 🤖


An AI-powered research assistant that automatically searches, analyzes, and synthesizes web information into comprehensive reports using **Gemini** and **SerpAPI**.

![Demo GIF](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcDk1dWk4b3V4Z2V1Z3R5d2VjZGNiY2V6dGJtN2R6eWZ1bHZ5eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3orieS4jfHJaKwkeli/giphy.gif)
*(Example output - replace with your actual demo GIF)*

## ✨ Features

| Component | Technology | Description |
|-----------|------------|-------------|
| **Web Search** | SerpAPI | Gets real-time search results |
| **Content Analysis** | Gemini Pro | Evaluates relevance & summarizes |
| **Scraping** | BeautifulSoup | Extracts clean text from pages |
| **Reporting** | Markdown | Generates structured outputs |

graph TD
    A[User Query] --> B(SerpAPI Search)
    B --> C[Scrape Content]
    C --> D(Gemini Analysis)
    D --> E[Generate Report]
    E --> F((Output))

```python
# Example usage
from web_research_agent import WebResearchAgent
agent = WebResearchAgent()
report = agent.research("Explain quantum computing")
print(report.summary)
