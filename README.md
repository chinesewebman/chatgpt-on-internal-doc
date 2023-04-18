# chatgpt on internal doc
 a QA bot on contents of given docs
可以基于给定的若干文档进行问答的机器人。

## Setup

1. Clone the repository: 
获取源文件:

git clone https://github.com/chinesewebman/chatgpt-on-internal-doc.git

2. Change to the project directory:
进入项目目录：

cd chatgpt-on-internal-doc

3. edit .env file, paste your OPENAI_API_KEY there
编辑.env 文件，设置好你的OPENAI_API_KEY

4. Load the environment variables:　
让环境变量生效：

. .env

5. Install the required packages:　
安装所需版本的相关软件包：

pip install -r requirements.txt

## Usage　用法
The default doc is on Buddhism. You can chat directly with the bot by jump to step 3. If you want to use your own documents, follow these steps:
内置的文档是三个佛法文档，可以直接跳到第3步进行问答。如果你想对自己的文档做问答，按以下两步生成新的索引库也很容易：

1. Copy your documents (txt, editable pdf, csv) into the `input` folder. For Chinese content, make sure to use utf-8 encoding to avoid garbled text.
把若干文档（纯文本文件、可以选取文字的pdf、从xlsx表格导出的csv文件）拷贝到 input 目录，中文内容的话，注意要以　utf-8　编码导出，避免出现乱码。

2. Generate a new index file:　生成新的索引文件

python new-index.py

制作索引库时做了部分的预分词处理，就是给中文标点符号和一些专有名词前后加了空格，这是为了避免出现A single term is larger than the allowed chunk size错误的原因，并且有助于专有名词不被错误切分。

the generated file: index.json is the local vector dababase, files in input and output can be removed by any time.
生成的文件：index.json 就是本地向量索引库了，output目录里是预分词的临时文件，可以随时删除。input目录里的文件也不需要了。


3. Run the application:　运行：

nohup flask --app ask.py run --host=0.0.0.0 --port=8080 &

4. Open a browser and access the application:
在浏览器里输入 http://your-ip-address:8080 , 用对外IP 或 http://127.0.0.1:8080 都可以。

5. Ask questions related to your documents, e.g., "介绍一下净名精舍".
对文档内容进行提问。比如问：介绍一下净名精舍

6. Hover your mouse over parameter names to see their descriptions.
所有的参数都有说明，可以将鼠标悬停在参数名称上来获得解释。

7. Adjust the parameters to see different results and check the logger box to see the process step by step. This will help you prepare better documents for QA.
可以设置各参数来看不同的效果，查看日志记录窗来了解问答的工作步骤，有助于整理出更适合答疑用的文档。

## Troubleshooting

If you encounter a `ValueError: Got a larger chunk overlap (5) than chunk size (-nnn)` error, reduce the values of `num_outpt`, `similarity_top_k`, or `chunk_size_limit`.

如果查询时出现ValueError: Got a larger chunk overlap (5) than chunk size (-nnn) 的问题，减少 num_outpt 的值或similarity_top_k、chunk_size_limit 的值。

## Requirements
This application needs to be run on a network with access to OpenAI.
需要在可以访问到 OpenAI 的网络环境里运行。