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

# 一次调用llm请求中所有内容（包括prompt、提问、回答等合在一起）的最大token数，取决于llm，对gpt-3.5-turbo来说，是4096
max_input_size = 4096

# 设置回答最多可以用多少token，不能设太大，因为要给传过去的上下文信息留额度
num_output = 2000

# 文本块之间允许的重叠token数
max_chunk_overlap = 5

QA_PROMPT_TMPL = (
    "提示： \n"
    "####\n"
    "{context_str}"
    "\n####\n"
    "对于询问概念定义，优先使用提示中[概念]后的部分作答。不要提上下文或所给文档等字样。如果找不到关联信息但问题确实与佛法或哲学相关，就以你自己的知识用中文来回答: {query_str}\n"
)

QA_PROMPT = QuestionAnswerPrompt(QA_PROMPT_TMPL)

# 当匹配到的文本块总长度（考虑到文本块定义过大或指定返回多个文本块的情形）加上预留的回复长度与prompt长度之和大于llm一次调用的最大长度时，会进入　refine　模式，每次结合一部分内容做总结，最后给出最终答案，这样会反复调用llm，导致耗时过长。
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

# 分段符号，默认是"/n/n/n"，这里改成"###",作为切分文本块的标志，制作文本时，在###之间安放同主题的文本段落，以备接下来逐文本块制作成语义向量索引。
paragraph_separator="###"
    # 备用分段符默认是"/n",就不改了

# 句内分词符号，默认只有英文标点符号和中文句号
secondary_chunking_regex="[^,.;，。、：”？！；》】“《【（]+[,.;，。、：”？！；》】“《【（]?" 
    # 默认的备选分词符号是英文空格，这里就不改了

myindex = GPTSimpleVectorIndex.load_from_disk('index.json')

@app.route("/", methods=["GET"])
def index():
    query = session.get("query", "")
    return render_template("index.html", response="", query=query)

@app.route("/ask", methods=["POST"])

def ask_ai():
    llama_logger = LlamaLogger()
    chunk_size_limit = int(request.form["chunk_size_limit"])
    response_mode = request.form["response_mode"]
    temperature = float(request.form["temperature"])
    similarity_top_k = int(request.form["similarity_top_k"])

    # Chunk_size 默认值为4000，过大了，容易引起多次调用llm做refined_response，这里改小，因此chunk_overlap（文本块之间可重叠的部分）也改小   
    sentence_splitter = SentenceSplitter(chunk_size=chunk_size_limit, chunk_overlap=max_chunk_overlap, paragraph_separator=paragraph_separator, secondary_chunking_regex=secondary_chunking_regex) 
    node_parser = SimpleNodeParser(text_splitter=sentence_splitter) 
    prompt_helper = PromptHelper(max_input_size=max_input_size, num_output=num_output, max_chunk_overlap=max_chunk_overlap,chunk_size_limit=chunk_size_limit)
    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=temperature, model_name="gpt-3.5-turbo"))
    service_context = ServiceContext.from_defaults(node_parser=node_parser, llm_predictor=llm_predictor, prompt_helper=prompt_helper, llama_logger=llama_logger, chunk_size_limit=chunk_size_limit)
    query_string = request.form["query"]
    user_id = str(uuid.uuid4())
    session["user_id"] = user_id

    # 根据gpt-index开发者说的注意事项，查询向量库时的参数要与建立向量库时的参数一致
    response = myindex.query(query_string, text_qa_template=QA_PROMPT, refine_template=REFINE_PROMPT, response_mode=response_mode, service_context = service_context, similarity_top_k=similarity_top_k)
    #read user_id from session, if it matches the user_id above, then proceed to the next step
    #if not, then return a message saying that the user_id is not valid
    stored_user_id = session.get("user_id")
    if stored_user_id != user_id:
        return json.dumps({"error": "Invalid user_id"})
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