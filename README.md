# Conversation Helper Beta   

## Overview  
**Conversation Helper Beta** is an AI-powered assistant designed to enhance conversations by providing relevant assistance when needed. Users can engage in discussions, and at any point, they can press a button to convert the conversation to text, identify key questions, and receive AI-generated answers using retrieval-augmented generation (RAG), Tavily, or direct LLM calls.  

## Features  
- **Speech-to-Text (STT) & Text-to-Speech (TTS):** Powered by Deepgram for seamless conversation transcription and response generation.  
- **LLM Inference:** Utilizes Groq for fast and efficient large language model processing.  
- **AI Agents for Query Resolution:** Leverages LangChain for building RAG agents, Tavily agents, or direct LLM calls to fetch relevant answers.  
- **Qdrant for Vector Storage:** Ensures efficient storage and retrieval of embeddings.  
- **User-Friendly UI:** Built using Streamlit for an intuitive and interactive experience.  

## Installation  

### 1. Clone the Repository  
```bash
git clone https://github.com/nareshis21/convo_helper_beta.git
cd convo_helper_beta
```

### 2. Install Dependencies  
Make sure you have Python installed, then install the required packages:  
```bash
pip install -r requirements.txt
```

### 3. Set Up API Keys  
Create a `.env` file in the project directory and add the following API keys:  
```
GROQ_API_KEY="your_groq_api_key"
TAVILY_API_KEY="your_tavily_api_key"
DEEPGRAM_API_KEY="your_deepgram_api_key"
LLAMA_PARSER_API_KEY="your_llama_parser_api_key"
QDRANT_API_KEY="your_qdrant_api_key"
QDRANT_URL="your_qdrant_url"
```

### 4. Run the Application  
Launch the Streamlit app:  
```bash
streamlit run app.py
```

## Usage  
1. Start a conversation using the voice or text input.  
2. If assistance is required, press the designated button.  
3. The system will transcribe the conversation and extract key questions.  
4. AI agents will fetch the most relevant answers and display them in the chat.  

## Contributing  
Feel free to contribute to this project! You can modify and enhance features as needed. Fork the repository, make changes, and submit a pull request.  

## Sample Demo  
A sample video demonstrating the project is available [here](https://drive.google.com/file/d/18ACVUB6TotDYXW7A0B7uQ_H7CHRNocop/view?usp=drivesdk).  

## License  
This project is open-source and available for use and modification.  
