# Creating an Arxiv Chat Application (with sources) using Chainlit and LangChain

This code sample should get you up to speed with ChainLit in no time flat!

### Launching the Chainlit Application Locally

1. `git clone ...` this repository
2. `pip install -r requirements.txt` in whatever virtual environment you prefer
3. Create or modify the `.env.example` -> `.env` and enter your OpenAI API key
4. Navigate to the root of your local repository and run: `chainlit run app.py` 

### Launching the ChainLit App with Docker

1. `git clone ..` this repository
2. Run `docker build -t chainlit-eop-demo .` in the root directory of the local repository
3. Run `docker run -p 7860:7860 chainlit-eop-demo`
