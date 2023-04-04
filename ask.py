from flask import Flask, render_template, request, json
from langchain.chat_models import ChatOpenAI
from llama_index import GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from llama_index import QuestionAnswerPrompt, RefinePrompt
from llama_index.logger import LlamaLogger

app = Flask(__name__)

max_input_size = 4096
num_outputs = 3000
max_chunk_overlap = 20
llama_logger = LlamaLogger()
myindex = GPTSimpleVectorIndex.load_from_disk('index.json')

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", response="")

@app.route("/ask", methods=["POST"])

def ask_ai():
    
    QA_PROMPT_TMPL = (
        "提示： \n"
        "---------------------\n"
        "{context_str}"
        "\n---------------------\n"
        "不要说：以上信息、上下文等。优先使用[概念]与###之间的内容作答，如果找不到关联信息，就以你自己的知识用中文来回答: {query_str}\n"
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
        "answer to the question in Chinese. "
        "If the context isn't useful, output the original answer again."
    )

    REFINE_PROMPT = RefinePrompt(REFINE_PROMPT_TMPL)

    chunk_size_limit = int(request.form["chunk_size_limit"])
    response_mode = request.form["response_mode"]
    temperature = float(request.form["temperature"])
    similarity_top_k = int(request.form["similarity_top_k"])
    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)
    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=temperature, model_name="gpt-3.5-turbo", max_tokens=num_outputs))

    query_string = request.form["query"]
    response = myindex.query(query_string, text_qa_template=QA_PROMPT, refine_template=REFINE_PROMPT, mode='embedding', response_mode=response_mode, llm_predictor=llm_predictor, prompt_helper=prompt_helper, llama_logger=llama_logger, similarity_top_k=similarity_top_k)
    output = {
        "response": str(response),
        "tokens": str(llm_predictor.last_token_usage),
        "source_nodes": str(response.source_nodes),
        "logs": str(llama_logger.get_logs())
    }
    llama_logger.reset()
    return (json.dumps(output))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)