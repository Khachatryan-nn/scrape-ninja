# Define prompt templates
prompt_templates = [
    """Search the provided Venture company's website for contact information.
Look for pages with titles or URLs containing keywords such as 'contact-us', 'contact', 'connect', 'connect-us', 'locations', or any other relevant terms that might indicate a page with contact information.
Extract and return the following information in JSON format:
- Company name
- Email addresses
- Phone numbers
- Physical addresses
- Contact forms (if available)""",
    """Search the provided Venture company's website for information about the industries they invest in.
Look for pages with titles or URLs containing keywords such as 'investment', 'industries','sectors', 'portfolio', or any other relevant terms that might indicate a page with investment information.
Extract and return the industries the company invests in, in JSON format.
If the information is not found on the company's website, search for relevant news articles or press releases that mention the company's investment industries.""",
    """Search the provided Venture company's website for information about their funding series.
Look for pages with titles or URLs containing keywords such as 'funding', 'investment','series', 'round', or any other relevant terms that might indicate a page with funding information.
Extract and return the series of funding (e.g., Series A, Series B, etc.) and the count of each series if available, in JSON format.
If the information is not found on the company's website, search for relevant news articles or press releases that mention the company's funding series.""",
]

conclusion_prompt = """Using the results from the previous three prompts, create a comprehensive JSON response that contains the following information:
- Company name
- Contact information:
  - Email addresses
  - Phone numbers
  - Physical addresses
  - Contact forms (if available)
- Investment industries
- Funding series:
  - Series of funding (e.g., Series A, Series B, etc.)
  - Count of each series (if available)
Combine the extracted information into a single JSON response."""

similarity_prompt = f"""Compare the website content of {0} to the other venture companies in the database and identify the 3 most similar venture companies based on their investment industries, funding series, and contact information.

Input: {1}

Scraped Venture Company: {0}
Database: {2}
Task:

Extract the relevant information from the scraped venture company, including investment industries, funding series, and contact information.
Compare the extracted information to the corresponding information of each venture company in the database.
Calculate a similarity score for each venture company in the database based on the comparison.
Rank the venture companies in the database by their similarity scores.
Return the 3 most similar venture companies to the scraped venture company.
Example Output:

The 3 most similar venture companies to [Scraped Venture Company] are:

[Venture Company 1] - Similarity score: [Score]
[Venture Company 2] - Similarity score: [Score]
[Venture Company 3] - Similarity score: [Score]

Output in JSON format with the described above structure."""