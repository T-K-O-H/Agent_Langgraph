@echo off
git add app.py
git add agent_graph.py
git add tools.py
git add README.md
git add Dockerfile
git add requirements.txt
git add chainlit.md
git add .gitignore
git add .chainlit/
git commit -m "Initial commit"
git branch -M main
git remote add origin https://huggingface.co/spaces/Shipmaster1/Agent_Langgraph
git remote add upstream git@github.com:T-K-O-H/Agent_Langgraph.git
git pull origin main --allow-unrelated-histories
git push -u origin main
git push -u upstream main 