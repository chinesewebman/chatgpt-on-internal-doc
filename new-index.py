# for gpt-index 0.5.8 and above
import os
import re
from langchain.chat_models import ChatOpenAI
from gpt_index import (
    GPTSimpleVectorIndex, 
    Document,
    MockLLMPredictor, 
    PromptHelper,
    LLMPredictor,
    MockEmbedding, 
    SimpleDirectoryReader,
    ServiceContext,
)
from gpt_index.langchain_helpers.text_splitter import SentenceSplitter
from gpt_index.node_parser import SimpleNodeParser
from gpt_index.embeddings.openai import OpenAIEmbedding

def load_buddha_dict(dict_path='./buddha-dict.txt'):
    with open(dict_path, 'r', encoding='utf-8') as f:
        words = f.read().splitlines()
    # 根据长度对词语列表进行排序
    words.sort(key=len, reverse=True)
    return words

def add_space_around_words(text, words):
    for word in words:
        # 使用正则表达式进行全词匹配，并在词语前后加空格
        pattern = r'\b{}\b'.format(re.escape(word))
        text = re.sub(pattern, f' {word} ', text)
    return text
def merge_consecutive_spaces(text):
    return re.sub(r'\s+', ' ', text)

def refine_doc(directory_path, output_dir='output'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    reader = SimpleDirectoryReader(directory_path)
    documents = reader.load_data()
    refined_documents = []

    add_space_after = '，。、：”？！；》】）'
    add_space_before = '“《【（'
    buddha_dict = load_buddha_dict()

    for i, doc in enumerate(documents):
        if isinstance(doc, Document):
            text = doc.text
        for char in add_space_after:
            text = text.replace(char, char + ' ')

        for char in add_space_before:
            text = text.replace(char, ' ' + char)

        text = add_space_around_words(text, buddha_dict)
        text = merge_consecutive_spaces(text)
        doc.text = text
        refined_documents.append(doc)

        with open(os.path.join(output_dir, f'output{i+1}.txt'), 'w', encoding='utf-8') as f:
            f.write(doc.text)

    return refined_documents

def construct_index(directory_path):
    print("读取"+str(directory_path)+"目录里的所有文件（不包括子目录）...")
    #documents = SimpleDirectoryReader(directory_path).load_data()
    documents = refine_doc(directory_path)
    max_input_size = 4096
    # set number of output tokens
    num_outputs = 2000
    # set maximum chunk overlap
    max_chunk_overlap = 5
    # set chunk size limit
    chunk_size_limit = 600
    # first, we count the tokens
    llm_predictor = MockLLMPredictor(max_tokens=num_outputs)
    # specify both a MockLLMPredictor as well as MockEmbedding
    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)
    embed_model = MockEmbedding(embed_dim=1536)
         
    sentence_splitter = SentenceSplitter(chunk_size=chunk_size_limit, chunk_overlap=max_chunk_overlap, secondary_chunking_regex="[^,.;，。、：”？！；》】“《【（]+[,.;，。、：”？！；》】“《【（]?") 
    node_parser = SimpleNodeParser(text_splitter=sentence_splitter) 
    service_context = ServiceContext.from_defaults(node_parser=node_parser, llm_predictor=llm_predictor, prompt_helper=prompt_helper, embed_model=embed_model, chunk_size_limit=chunk_size_limit)
    #documents = SimpleDirectoryReader('data').load_data()[0] 
    index = GPTSimpleVectorIndex.from_documents(documents, service_context=service_context)
    # get number of tokens used
    # Store the embedding token usage into a variable
    embedding_token_usage = embed_model.last_token_usage
    token_price = 0.0004  # cost of embedding per 1000 tokens
    price_per_token = token_price / 1000
    total_price = round(price_per_token * embedding_token_usage,3)
    print("建索引所需Token数：", embedding_token_usage, "，预计花费：", total_price, "美元")
    ask_user()
    #正式开始创建索引
    print("chunk_size_limit:", chunk_size_limit)
    embed_batch_size=round(max_input_size/chunk_size_limit*5)
    #print ("embed_batch_size=",embed_batch_size)

    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0,model_name="gpt-3.5-turbo", max_tokens=num_outputs))
    service_context = ServiceContext.from_defaults(node_parser=node_parser, llm_predictor=llm_predictor, prompt_helper=prompt_helper, chunk_size_limit=chunk_size_limit, embed_model=OpenAIEmbedding(embed_batch_size=embed_batch_size))
    
    index = GPTSimpleVectorIndex.from_documents(
        documents, service_context=service_context
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