import time
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain.vectorstores import DeepLake
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyMuPDFLoader
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_qdrant import Qdrant
from utils.llm_intiate import llm_g
from utils.tavily_websearch import search
search_tool = search
llm = llm_g

# Update prompt to ensure tool usage is mentioned in the response
prompt = ChatPromptTemplate([
    ("system",
    f"""You are a helpful chatbot. You need to IDENTIFY THE TECH QUESTION FROM THE GIVEN CONVERSATION USER_INPUT TEXT and return the question and  answer the user's queries in 
    detail from the document context. IMPORTANT: PROVIDE ANSWER IN A SHORT SINGLE LINE SENTENCE.
    PROVIDE WHICH TOOL IS USED TO RETRIEVE THE ANSWER AS WELL: LLM ANSWER, RAG, or WEB SEARCH.
    You have access to two tools: 
    deeplake_vectorstore_retriever and tavily_search_engine. 
    Always use the deeplake_vectorstore_retriever tool first to retrieve IF USED AT THE START WRITE deeplake_vectorstore_retriever used,
    the context and answer the question. If the context does not contain relevant 
    answers for the user's query, use the tavily_search_engine to fetch web search 
    results to answer them IF tavily_search_engine used WRITE tavily_search_engine used .
    NEVER give an incomplete answer. Always try your best 
    to find an answer through web search if it is not found from the context.
    
    IF Both Tool wasnt used answer it your data and WRITE LLM ANSWER used.
    
    The response should be in this format:
    Question: "Question identified"
    Answer: "Answer"
    
   
    """),
    ("human", "{user_input}"),
    ("placeholder", "{messages}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Load and split document
data = r"sample_data\Naresh_Lahajal_Resume_SINGLE.pdf" 
loader = PyMuPDFLoader(file_path=data) 
text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200) 
docs = loader.load_and_split(text_splitter=text_splitter) 

# Set up embeddings and vectorstore
embeddings = FastEmbedEmbeddings()
vectorstore = Qdrant.from_documents(
  documents=docs,
  embedding=embeddings,
  location=":memory:",
  collection_name="data",
)

retriever_tool = create_retriever_tool(
	retriever=vectorstore.as_retriever(
	search_type="similarity",
	search_kwargs={
		"k": 6
	},
),
    name="deeplake_vectorstore_retriever",
    description="Searches and returns contents from uploaded document based on user query.",
)

# List of tools the agent can use
tools = [
    retriever_tool,
    search_tool,
]

# Set up memory for conversation history
history = SQLChatMessageHistory(
    session_id="ghdcfhdxgfx",
    connection_string="sqlite:///chat_history.db",
    table_name="message_store",
    session_id_field_name="session_id",
)

memory = ConversationBufferWindowMemory(chat_memory=history)

# Custom AgentExecutor to track which tool was used
class CustomAgentExecutor(AgentExecutor):
    def invoke(self, inputs):
        tool_used = None
        result = super().invoke(inputs)
        
        # Check the result to track which tool was used
        if "deeplake_vectorstore_retriever" in result["output"]:
            tool_used = "RAG (Document Retrieval)"
        elif "tavily_search_engine" in result["output"]:
            tool_used = "WEB SEARCH"
        else:
            tool_used = "LLM ANSWER"
        
        # Extracting question and answer dynamically
        output = result["output"]
        question_start = output.find('Question: ') + len('Question: ')
        question_end = output.find('Answer:', question_start)
        question = output[question_start:question_end].strip().replace('"', '')
        
        answer_start = output.find('Answer: ') + len('Answer: ')
        answer = output[answer_start:].strip().replace('"', '')
        
        # Prepare the final result with question, answer, and tool used
        result["output"] = {
            "question": question,
            "answer": answer,
            "tool_used": tool_used
        }
        
        return result


# Create the agent with the tools and prompt
agent = create_openai_tools_agent(llm, tools, prompt)

# Create the custom agent executor
agent_executor = CustomAgentExecutor(
    tools=tools,
    agent=agent,
    verbose=False,
    max_iterations=8,
    early_stopping_method="force",
    memory=memory,
)

# questions = [
#     "What is the capital of France?",
#     "How does photosynthesis work?",
#     "What are the latest advancements in AI?",
#     "Who won the Nobel Prize in Physics in 2023?",
#     "What is quantum computing?",
#     "Can you explain the theory of relativity?",
#     "How do black holes form?",
#     "What is the meaning of life?",
#     "What are the benefits of a balanced diet?",
#     "How do electric cars work?",
#     """
# Person 1:
# Hi! I’m John, a generative AI developer. I’ve been working in the field for a few years now, diving deep into the world of neural networks and machine learning. It’s been a fascinating journey so far. Apart from my work, I’m really passionate about chess. I love the strategy and deep thinking involved in it. I also play volleyball during the weekends – it’s a great way to relax and stay active. What about you? What do you do in your spare time?

# Person 2:
# Hey John! Nice to meet you. I'm Alex. I’m actually also really into generative AI, although I'm relatively new to it compared to you. I’ve been experimenting with some GPT-based models and have been working on a few personal projects in AI. It’s such an exciting field, right? There’s so much potential. I’ve heard a lot about LangGraph recently, though. I’m not entirely sure what it is. Do you know much about it? I’ve seen some people mention it in discussions about natural language processing and graph-based models, but I haven’t looked into it in-depth yet.

# Oh, and speaking of hobbies, I’m actually a huge fan of volleyball as well! I’ve been playing for a couple of years. It’s such a great mix of teamwork and skill. Since you mentioned volleyball, do you know of any good places around here to play? I’m always looking for a nice spot to hit the court. You know, where the vibe is fun but also competitive enough to get a good workout in! How do you usually find your spots to play?
# """

# ]

# # Variable to accumulate total time
# total_time = 0
# for question in questions:
#     # Start time calculation
#     start_time = time.time()

#     # Create a dictionary with the question in the required format
#     result = agent_executor.invoke({
#         "user_input": question
#     })

#     # Calculate elapsed time for this request
#     elapsed_time = time.time() - start_time
#     total_time += elapsed_time
    
#     print(f"Question: {result['output']['question']}")
#     print(f"Answer: {result['output']['answer']}")
#     print(f"Tool Used: {result['output']['tool_used']}")
#     print(f"Time taken: {elapsed_time:.4f} seconds")
#     print('-' * 50)
    
# average_time = total_time / len(questions)
# print(f"Average time taken: {average_time:.4f} seconds")

# # Print the result with the tool used
# print(f"Question: {result['output']['question']}")
# print(f"Answer: {result['output']['answer']}")
# print(f"Tool Used: {result['output']['tool_used']}")

# question = """
# Person 1:
# Hi! I’m John, a generative AI developer. I’ve been working in the field for a few years now, diving deep into the world of neural networks and machine learning. It’s been a fascinating journey so far. Apart from my work, I’m really passionate about chess. I love the strategy and deep thinking involved in it. I also play volleyball during the weekends – it’s a great way to relax and stay active. What about you? What do you do in your spare time?

# Person 2:
# Hey John! Nice to meet you. I'm Alex. I’m actually also really into generative AI, although I'm relatively new to it compared to you. I’ve been experimenting with some GPT-based models and have been working on a few personal projects in AI. It’s such an exciting field, right? There’s so much potential. I’ve heard a lot about LangGraph recently, though. I’m not entirely sure what it is. Do you know much about it? I’ve seen some people mention it in discussions about natural language processing and graph-based models, but I haven’t looked into it in-depth yet.

# Oh, and speaking of hobbies, I’m actually a huge fan of volleyball as well! I’ve been playing for a couple of years. It’s such a great mix of teamwork and skill. Since you mentioned volleyball, do you know of any good places around here to play? I’m always looking for a nice spot to hit the court. You know, where the vibe is fun but also competitive enough to get a good workout in! How do you usually find your spots to play?
# """

# result = agent_executor.invoke({
#     "user_input": question,
# })

# # Print the result with the tool used
# print(f"Question: {result['output']['question']}")
# print(f"Answer: {result['output']['answer']}")
# print(f"Tool Used: {result['output']['tool_used']}")

# result = agent_executor.invoke({
#     "user_input": "Todays Date",
# })

# # Print the result with the tool used
# print(f"Question: {result['output']['question']}")
# print(f"Answer: {result['output']['answer']}")
# print(f"Tool Used: {result['output']['tool_used']}")
