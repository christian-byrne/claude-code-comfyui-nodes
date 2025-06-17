"""
Claude Reddit Scraper Node
Scrapes Reddit posts and comments using Claude Code with Playwright MCP
"""

import json
import subprocess
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import os
import uuid

try:
    from server import PromptServer
except ImportError:
    PromptServer = None


class ClaudeRedditScraper:
    """
    Scrape Reddit posts and comments using Claude Code with Playwright MCP.
    Automatically configures MCP and handles data extraction.
    """

    CATEGORY = "claude_code/scrapers"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "source_type": (
                    ["url", "subreddit", "search", "user"],
                    {
                        "default": "subreddit",
                        "tooltip": "Type of Reddit source to scrape",
                    },
                ),
                "source": (
                    "STRING",
                    {
                        "default": "programming",
                        "tooltip": "Reddit URL, subreddit name, search query, or username",
                    },
                ),
                "scrape_mode": (
                    ["comments", "posts", "both", "metadata"],
                    {"default": "comments", "tooltip": "What to scrape from Reddit"},
                ),
                "max_items": (
                    "INT",
                    {
                        "default": 10,
                        "min": 1,
                        "max": 100,
                        "tooltip": "Maximum items to scrape",
                    },
                ),
                "model": (
                    ["default", "sonnet", "opus"],
                    {"default": "sonnet", "tooltip": "Claude model to use"},
                ),
            },
            "optional": {
                "sort_by": (
                    ["hot", "new", "top", "rising", "controversial"],
                    {
                        "default": "hot",
                        "tooltip": "Sort order for posts (subreddit mode only)",
                    },
                ),
                "time_filter": (
                    ["hour", "day", "week", "month", "year", "all"],
                    {
                        "default": "day",
                        "tooltip": "Time filter for top/controversial posts",
                    },
                ),
                "include_metadata": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "Include post metadata (author, score, date, etc)",
                    },
                ),
                "max_comment_depth": (
                    "INT",
                    {
                        "default": 2,
                        "min": 1,
                        "max": 10,
                        "tooltip": "Maximum comment thread depth to scrape",
                    },
                ),
                "memory": (
                    "CLAUDE_MEMORY",
                    {"tooltip": "Additional context/memory for Claude"},
                ),
                "previous_output": (
                    "CLAUDE_OUTPUT",
                    {"tooltip": "Output from previous Claude execution"},
                ),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }

    RETURN_TYPES = ("CLAUDE_OUTPUT", "JSON", "STRING", "INT")
    RETURN_NAMES = ("output", "scraped_data", "summary", "item_count")
    DESCRIPTION = "Scrape Reddit posts and comments using Playwright MCP"
    FUNCTION = "scrape_reddit"

    OUTPUT_NODE = False

    def __init__(self):
        self.output_base_dir = os.path.join(os.getcwd(), "claude_code_outputs")
        os.makedirs(self.output_base_dir, exist_ok=True)

    def send_progress(self, message: str, unique_id: str):
        """Send progress update to UI"""
        if PromptServer and unique_id:
            PromptServer.instance.send_sync(
                "claude.progress", {"node_id": unique_id, "message": message}
            )

    def ensure_playwright_mcp(self, unique_id: str) -> bool:
        """Ensure Playwright MCP is configured"""
        try:
            # Check if already configured
            result = subprocess.run(
                ["claude", "mcp", "list", "--json"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                mcps = json.loads(result.stdout)
                if any(mcp.get("name") == "playwright" for mcp in mcps):
                    self.send_progress("Playwright MCP already configured", unique_id)
                    return True

            # Add Playwright MCP
            self.send_progress("Configuring Playwright MCP...", unique_id)
            result = subprocess.run(
                [
                    "claude",
                    "mcp",
                    "add-json",
                    "--scope",
                    "user",
                    "playwright",
                    '{"command": "playwright-mcp-server"}',
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                self.send_progress("Playwright MCP configured successfully", unique_id)
                return True
            else:
                self.send_progress(
                    f"Failed to configure Playwright MCP: {result.stderr}", unique_id
                )
                return False

        except Exception as e:
            self.send_progress(f"Error configuring MCP: {str(e)}", unique_id)
            return False

    def build_reddit_url(
        self, source_type: str, source: str, sort_by: str, time_filter: str
    ) -> str:
        """Build the Reddit URL based on parameters"""
        if source_type == "url":
            # Direct URL provided
            return source
        elif source_type == "subreddit":
            # Clean subreddit name
            subreddit = source.strip().lstrip("/r/")
            if sort_by in ["top", "controversial"]:
                return f"https://reddit.com/r/{subreddit}/{sort_by}/?t={time_filter}"
            else:
                return f"https://reddit.com/r/{subreddit}/{sort_by}/"
        elif source_type == "search":
            # Search query
            return f"https://reddit.com/search/?q={source}"
        elif source_type == "user":
            # User profile
            username = source.strip().lstrip("/u/").lstrip("u/")
            return f"https://reddit.com/user/{username}"
        else:
            return source

    def build_scraping_prompt(
        self, params: Dict[str, Any], output_folder: str, memory: str
    ) -> str:
        """Build the complete prompt for Reddit scraping"""
        url = params["url"]
        scrape_mode = params["scrape_mode"]
        max_items = params["max_items"]
        include_metadata = params["include_metadata"]
        max_comment_depth = params.get("max_comment_depth", 2)

        parts = []

        # Add memory if provided
        if memory:
            parts.append("# Context/Memory\n")
            parts.append(memory)
            parts.append("\n\n")

        # Add main command
        parts.append("# Command\n")
        parts.append(f"Use the Playwright MCP to scrape Reddit data from: {url}\n\n")

        parts.append("## Scraping Instructions:\n")
        parts.append("1. Navigate to the URL\n")
        parts.append("2. Wait for the page to load completely\n")
        parts.append("3. Scrape the following data:\n")

        if scrape_mode in ["posts", "both"]:
            parts.append(f"\n### Posts (first {max_items} items):\n")
            parts.append("- Title\n")
            parts.append("- URL/link\n")
            parts.append("- Subreddit\n")

            if include_metadata:
                parts.append("- Author username\n")
                parts.append("- Score/upvotes\n")
                parts.append("- Number of comments\n")
                parts.append("- Post time\n")
                parts.append("- Awards (if any)\n")
                parts.append("- Post flair\n")
                parts.append("- Whether it's pinned/stickied\n")

        if scrape_mode in ["comments", "both"]:
            if scrape_mode == "comments":
                parts.append(f"\n### Comments (from first {max_items} posts):\n")
                parts.append("- Find the post with the most comments (at least 20+ comments)\n")
                parts.append("- Click into that specific post to view the full comment thread\n")
            else:
                parts.append(f"\n### Comments (for each scraped post):\n")
                parts.append("- Click into each post\n")

            parts.append(f"- Scrape ALL visible comments up to {max_comment_depth} levels deep\n")
            parts.append("- For each comment, capture:\n")
            parts.append("  * Full comment text (don't truncate)\n")
            parts.append("  * Author username\n")
            parts.append("  * Score/upvotes\n")
            parts.append("  * Timestamp\n")
            parts.append("  * Comment ID (if available)\n")
            parts.append("  * Parent comment ID (to preserve threading)\n")
            parts.append("  * Depth level (0=top-level, 1=reply, 2=reply-to-reply, etc.)\n")
            parts.append("  * Awards (if any)\n")
            parts.append("  * Whether it's highlighted/pinned\n")
            parts.append("- Expand 'Continue this thread' links to get deeper comments\n")
            parts.append("- Include deleted/removed comments with appropriate markers\n")
            parts.append("- Preserve the exact thread hierarchy in nested structure\n")

        if scrape_mode == "metadata":
            parts.append("\n### Subreddit Metadata:\n")
            parts.append("- Subreddit name and description\n")
            parts.append("- Member count\n")
            parts.append("- Rules\n")
            parts.append("- Moderators (if visible)\n")
            parts.append("- Pinned posts\n")
            parts.append("- Sidebar information\n")

        parts.append("\n## Data Processing:\n")
        parts.append("- Structure the data as clean JSON with this format:\n")
        parts.append("```json\n")
        parts.append("{\n")
        parts.append('  "post": {\n')
        parts.append('    "title": "...",\n')
        parts.append('    "url": "...",\n')
        parts.append('    "author": "...",\n')
        parts.append('    "score": 123,\n')
        parts.append('    "content": "...",\n')
        parts.append('    "num_comments": 45\n')
        parts.append('  },\n')
        parts.append('  "comments": [\n')
        parts.append('    {\n')
        parts.append('      "id": "abc123",\n')
        parts.append('      "parent_id": null,\n')
        parts.append('      "author": "username",\n')
        parts.append('      "text": "Full comment text...",\n')
        parts.append('      "score": 10,\n')
        parts.append('      "timestamp": "2 hours ago",\n')
        parts.append('      "depth": 0,\n')
        parts.append('      "awards": 1,\n')
        parts.append('      "is_highlighted": false,\n')
        parts.append('      "replies": [\n')
        parts.append('        {\n')
        parts.append('          "id": "def456",\n')
        parts.append('          "parent_id": "abc123",\n')
        parts.append('          "author": "another_user",\n')
        parts.append('          "text": "Reply text...",\n')
        parts.append('          "score": 5,\n')
        parts.append('          "timestamp": "1 hour ago",\n')
        parts.append('          "depth": 1,\n')
        parts.append('          "replies": []\n')
        parts.append('        }\n')
        parts.append('      ]\n')
        parts.append('    }\n')
        parts.append('  ],\n')
        parts.append('  "metadata": {\n')
        parts.append('    "total_comments_scraped": 45,\n')
        parts.append('    "max_depth_reached": 3,\n')
        parts.append('    "scraped_at": "2024-06-16T16:00:00Z"\n')
        parts.append('  }\n')
        parts.append("}\n")
        parts.append("```\n")
        parts.append("- Use consistent field names\n")
        parts.append("- Handle missing data gracefully (use null)\n")
        parts.append("- Include a summary count of items scraped\n")
        parts.append("- If any errors occur, include them in an 'errors' field\n")

        parts.append("\n# Output Instructions\n")
        parts.append(
            f"Save all scraped data to a file named 'reddit_data.json' in: {output_folder}\n"
        )
        parts.append("Also create a 'scraping_summary.txt' file with:\n")
        parts.append("- Post title and URL\n")
        parts.append("- Total comments scraped\n")
        parts.append("- Top 5 comments by score (with author and score)\n")
        parts.append("- Most controversial comments (lowest/negative scores)\n")
        parts.append("- Thread depth statistics\n")
        parts.append("- Key discussion themes or topics mentioned\n")
        parts.append("- Any issues encountered\n")
        parts.append("- Timestamp of scraping\n")
        parts.append("\nDo not create files elsewhere.\n")

        return "".join(parts)

    def generate_output_folder(self) -> Tuple[str, str]:
        """Generate unique output folder"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        folder_name = f"reddit_scrape_{timestamp}_{unique_id}"
        folder_path = os.path.join(self.output_base_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_name, folder_path

    def read_scraped_data(self, folder_path: str) -> Tuple[Dict[str, Any], str, int]:
        """Read the scraped data from output files"""
        scraped_data = {}
        summary = "No data found"
        item_count = 0

        # Read reddit_data.json
        data_file = os.path.join(folder_path, "reddit_data.json")
        if os.path.exists(data_file):
            try:
                with open(data_file, "r") as f:
                    scraped_data = json.load(f)

                # Count items
                if isinstance(scraped_data, list):
                    item_count = len(scraped_data)
                elif isinstance(scraped_data, dict):
                    if "posts" in scraped_data:
                        item_count = len(scraped_data.get("posts", []))
                    elif "data" in scraped_data:
                        item_count = len(scraped_data.get("data", []))
                    else:
                        item_count = 1

            except Exception as e:
                scraped_data = {"error": f"Failed to read data file: {str(e)}"}

        # Read summary
        summary_file = os.path.join(folder_path, "scraping_summary.txt")
        if os.path.exists(summary_file):
            try:
                with open(summary_file, "r") as f:
                    summary = f.read().strip()
            except:
                pass

        if item_count > 0 and not summary.startswith("No data"):
            return scraped_data, summary, item_count
        else:
            # Generate summary from data
            if item_count > 0:
                summary = f"Successfully scraped {item_count} items"
            return scraped_data, summary, item_count

    def scrape_reddit(
        self,
        source_type: str,
        source: str,
        scrape_mode: str,
        max_items: int,
        model: str,
        sort_by: str = "hot",
        time_filter: str = "day",
        include_metadata: bool = True,
        max_comment_depth: int = 2,
        memory: Optional[str] = None,
        previous_output: Optional[Dict] = None,
        unique_id: str = "",
        **kwargs,
    ) -> Tuple[Dict[str, Any], Dict[str, Any], str, int]:
        """Execute Reddit scraping using Claude Code with Playwright MCP"""

        self.send_progress("Initializing Reddit scraper...", unique_id)

        # Ensure Playwright MCP is configured
        if not self.ensure_playwright_mcp(unique_id):
            error_output = {"error": "Failed to configure Playwright MCP"}
            return (error_output, {}, "Failed to configure Playwright MCP", 0)

        # Generate output folder
        folder_name, folder_path = self.generate_output_folder()
        self.send_progress(f"Created output folder: {folder_name}", unique_id)

        # Build Reddit URL
        url = self.build_reddit_url(source_type, source, sort_by, time_filter)
        self.send_progress(f"Target URL: {url}", unique_id)

        # Build complete prompt
        prompt = self.build_scraping_prompt(
            {
                "url": url,
                "scrape_mode": scrape_mode,
                "max_items": max_items,
                "include_metadata": include_metadata,
                "max_comment_depth": max_comment_depth,
            },
            folder_path,
            memory or "",
        )

        # Build CLI command
        cmd_parts = [
            "claude",
            "-p",
            "--max-turns",
            "15",  # More turns for complex scraping
            "--allowedTools",
            "mcp__playwright",
            "--dangerously-skip-permissions",  # Skip confirmations for automation
        ]

        if model != "default":
            cmd_parts.extend(["--model", model])

        # Execute scraping
        self.send_progress(f"Scraping Reddit ({scrape_mode})...", unique_id)
        start_time = datetime.now()

        try:
            result = subprocess.run(
                cmd_parts,
                input=prompt,
                cwd=folder_path,
                capture_output=True,
                text=True,
                check=False,
                timeout=600,  # 10 minute timeout for complex scraping
            )

            duration = (datetime.now() - start_time).total_seconds()

            # Log any errors
            if result.returncode != 0:
                self.send_progress(
                    f"Warning: Command exited with code {result.returncode}", unique_id
                )
                if result.stderr:
                    error_log = os.path.join(folder_path, "error_log.txt")
                    with open(error_log, "w") as f:
                        f.write(result.stderr)

            # Read scraped data from files
            scraped_data, summary, item_count = self.read_scraped_data(folder_path)

            if item_count > 0:
                self.send_progress(
                    f"Successfully scraped {item_count} items", unique_id
                )
            else:
                self.send_progress("Scraping completed but no data found", unique_id)

            # Create metadata
            metadata = {
                "source_type": source_type,
                "source": source,
                "url": url,
                "scrape_mode": scrape_mode,
                "max_items_requested": max_items,
                "items_scraped": item_count,
                "sort_by": sort_by,
                "time_filter": time_filter,
                "include_metadata": include_metadata,
                "duration_seconds": duration,
                "timestamp": datetime.now().isoformat(),
                "model": model,
                "folder": folder_name,
                "files": [
                    f
                    for f in os.listdir(folder_path)
                    if os.path.isfile(os.path.join(folder_path, f))
                ],
            }

            # Save metadata
            metadata_file = os.path.join(folder_path, "_claude_code_metadata.json")
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            # Create CLAUDE_OUTPUT compatible output
            output = {"folder": folder_name, "response": summary, "metadata": metadata}

            return (output, scraped_data, summary, item_count)

        except subprocess.TimeoutExpired:
            error_msg = "Scraping timeout after 10 minutes - Reddit might be slow or the request is too complex"
            self.send_progress(error_msg, unique_id)

            # Still try to read any partial data
            scraped_data, summary, item_count = self.read_scraped_data(folder_path)
            if item_count > 0:
                output = {
                    "folder": folder_name,
                    "response": f"Partial data scraped before timeout: {item_count} items",
                    "metadata": {"error": error_msg, "partial_data": True},
                }
                return (
                    output,
                    scraped_data,
                    f"Timeout - partial data: {item_count} items",
                    item_count,
                )
            else:
                return ({"error": error_msg}, {}, error_msg, 0)

        except Exception as e:
            error_msg = f"Scraping error: {str(e)}"
            self.send_progress(error_msg, unique_id)
            return ({"error": error_msg}, {}, error_msg, 0)
