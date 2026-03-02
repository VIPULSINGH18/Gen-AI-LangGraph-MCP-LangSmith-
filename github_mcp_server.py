from fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv
import base64

# Load env vars
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN not found in .env")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

mcp = FastMCP("github-mcp")

# -------------------------
# CREATE REPOSITORY
# -------------------------
@mcp.tool()
def create_repo(name: str, private: bool = True):
    """Create a new GitHub repository"""
    url = "https://api.github.com/user/repos"
    payload = {
        "name": name,
        "private": private
    }
    r = requests.post(url, headers=HEADERS, json=payload)
    return r.json()

# -------------------------
# READ FILE
# -------------------------
@mcp.tool()
def read_file(repo: str, path: str):
    """Read a file from a GitHub repository (owner/repo)"""
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    r = requests.get(url, headers=HEADERS)
    data = r.json()

    if "content" in data:
        content = base64.b64decode(data["content"]).decode()
        return content

    return data

# -------------------------
# COMMIT / UPDATE FILE
# -------------------------
@mcp.tool()
def commit_file(
    repo: str,
    path: str,
    content: str,
    message: str
):
    """Create or update a file in a repository"""

    url = f"https://api.github.com/repos/{repo}/contents/{path}"

    # check if file exists
    r = requests.get(url, headers=HEADERS)
    sha = r.json().get("sha") if r.status_code == 200 else None

    payload = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode()
    }

    if sha:
        payload["sha"] = sha

    r = requests.put(url, headers=HEADERS, json=payload)
    return r.json()

# -------------------------
# DELETE FILE
# -------------------------
@mcp.tool()
def delete_file(
    repo: str,
    path: str,
    message: str
):
    """Delete a file from a repository"""

    url = f"https://api.github.com/repos/{repo}/contents/{path}"

    r = requests.get(url, headers=HEADERS)
    sha = r.json().get("sha")

    if not sha:
        return {"error": "File not found"}

    payload = {
        "message": message,
        "sha": sha
    }

    r = requests.delete(url, headers=HEADERS, json=payload)
    return r.json()

# -------------------------
# START SERVER
# -------------------------
if __name__ == "__main__":
    mcp.run()
