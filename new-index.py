from llama_index import MockEmbedding, SimpleDirectoryReader, GPTSimpleVectorIndex, LLMPredictor, PromptHelper, MockLLMPredictor
from langchain.chat_models import ChatOpenAI

def construct_index(directory_path):
    print("读取"+str(directory_path)+"目录里的所有文件（不包括子目录）...")
    documents = SimpleDirectoryReader(directory_path).load_data()

    max_input_size = 4096
    # set number of output tokens
    num_outputs = 2000
    # set maximum chunk overlap
    max_chunk_overlap = 20
    # set chunk size limit
    chunk_size_limit = 2000 
    #os.environ["OPENAI_API_KEY"] = 'your OpenAI API Key'

    # define LLM 
    # first, we count the tokens
    llm_predictor = MockLLMPredictor(max_tokens=2000)
    embed_model = MockEmbedding(embed_dim=1536)
    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)
    index = GPTSimpleVectorIndex(
        documents, llm_predictor=llm_predictor, prompt_helper=prompt_helper, embed_model=embed_model
    )
    # get number of tokens used
    embedding_token_usage = embed_model.last_token_usage
    token_price = 0.0004  # cost of embedding per 1000 tokens
    price_per_token = token_price / 1000
    total_price = round(price_per_token * embedding_token_usage,3)
    print("建索引所需Token数：", embedding_token_usage, "，预计花费：", total_price, "美元")
    ask_user()
    #正式开始创建索引
    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0,model_name="gpt-3.5-turbo", max_tokens=num_outputs))
    index = GPTSimpleVectorIndex(
        documents, llm_predictor=llm_predictor, prompt_helper=prompt_helper
    )
    index.save_to_disk('index.json')
    print("索引文件已存盘")
    return
def ask_user():
    user_input = input("是否继续？(y/n)")

    if user_input.lower() == "y":
    # 用户想要继续执行程序
        pass
    else:
    # 用户不想继续执行程序
        print("那么就不再继续执行，再见！")
        exit()
    return
construct_index('input')