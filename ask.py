#for gpt-index0.5.8 and above
from flask import Flask, render_template, request, json, session, redirect, url_for
from flask_session import Session
from langchain.chat_models import ChatOpenAI
from gpt_index import GPTSimpleVectorIndex, LLMPredictor, PromptHelper, QuestionAnswerPrompt, RefinePrompt, ServiceContext
from gpt_index.logger import LlamaLogger
from gpt_index.langchain_helpers.text_splitter import SentenceSplitter
from gpt_index.node_parser import SimpleNodeParser
import uuid

app = Flask(__name__)
# Set a secret key for encrypting the session
app.config['SECRET_KEY'] = 'look_at_me'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

max_input_size = 4096
num_output = 2000
max_chunk_overlap = 5
QA_PROMPT_TMPL = (
    "提示： \n"
    "---------------------\n"
    "{context_str}"
    "\n---------------------\n"
    "不要提到上下文或所给文档等。优先使用上下文中[概念]与###之间的内容作答，如果找不到关联信息，就以你自己的知识用中文来回答: {query_str}\n"
)
QA_PROMPT = QuestionAnswerPrompt(QA_PROMPT_TMPL)
REFINE_PROMPT_TMPL = (
    "The original question is as follows: {query_str}\n"
    "We have provided an existing answer: {existing_answer}\n"
    "We have the opportunity to refine the above answer"
    "(only if needed) with some more context below.\n"
    "------------\n"
    "{context_msg}\n"
    "------------\n"
    "Given the new context, refine the original answer to better "
    "answer to the question in Chinese,but don't mention words like"
    "'context','given information' etc."
    "If the context isn't useful, output the original answer again."
)
REFINE_PROMPT = RefinePrompt(REFINE_PROMPT_TMPL)

myindex = GPTSimpleVectorIndex.load_from_disk('index.json')

@app.route("/", methods=["GET"])
def index():
    query = session.get("query", "")
    user_id = str(uuid.uuid4())
    session["user_id"] = user_id
    return render_template("index.html", response="", query=query)

@app.route("/ask", methods=["POST"])

def ask_ai():
    llama_logger = LlamaLogger()
    chunk_size_limit = int(request.form["chunk_size_limit"])
    response_mode = request.form["response_mode"]
    temperature = float(request.form["temperature"])
    similarity_top_k = int(request.form["similarity_top_k"])
    sentence_splitter = SentenceSplitter(chunk_size=chunk_size_limit, chunk_overlap=max_chunk_overlap) 
    node_parser = SimpleNodeParser(text_splitter=sentence_splitter) 
    prompt_helper = PromptHelper(max_input_size=max_input_size, num_output=num_output, max_chunk_overlap=max_chunk_overlap,chunk_size_limit=chunk_size_limit)
    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=temperature, model_name="gpt-3.5-turbo"))
    service_context = ServiceContext.from_defaults(node_parser=node_parser, llm_predictor=llm_predictor, prompt_helper=prompt_helper, llama_logger=llama_logger, chunk_size_limit=chunk_size_limit)
    query_string = request.form["query"]
    session["query"] = query_string
    
    response = myindex.query(query_string, text_qa_template=QA_PROMPT, refine_template=REFINE_PROMPT, response_mode=response_mode, service_context = service_context, similarity_top_k=similarity_top_k)
    output = {
        "response": str(response),
        "tokens": str(llm_predictor.last_token_usage),
        "source_nodes": str(response.source_nodes),
        "logs": str(llama_logger.get_logs())
    }
    llama_logger.reset()
    return (json.dumps(output))

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=80)