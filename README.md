# chatgpt on internal doc
 a QA bot on contents of given docs
给出文档，可以基于文档进行问答的机器人。

edit .env file, paste your OPENAI_API_KEY there
编辑.env 文件，设置好你的OPENAI_API_KEY

. .env
执行 . .env 让环境变量生效.

pip install -r requirements.txt
安装所需版本的相关软件包

the default doc is on Buddism, you can chat directly, if you don't want to chat on this, it's easy to make a new index file:
内置的文档是三个佛法文档，可以直接进行问答。如果你想不想对此做问答，生成新的索引文档也很容易：

copy your docs(txt, editable pdf，csv) into the folder: input
把若干文档（纯文本文件、可以选取文字的pdf、从xlsx表格导出的csv文件）拷贝到 input 目录，中文内容的话，注意要以　utf-8　编码导出，避免出现乱码。

python new-index.py

the generated file: index.json is the local vector dababase, files in input and output can be removed by any time.
生成的文件：index.json 就是本地向量索引库了，output目录里是预分词的临时文件，可以随时删除。input目录里的文件也不需要了。

运行：
nohup flask --app ask.py run --host=0.0.0.0 --port=8080 &

open a browser, access http://your-ip-address:8080
在浏览器里输入 http://your-ip-address:8080 , 用对外IP 或 http://127.0.0.1:8080 都可以。

ask things around your docs. like: 介绍一下净名精舍
对文档内容进行提问。比如问：介绍一下净名精舍

move mouse over parameter name to see the introduciton of it
所有的参数都有说明，可以将鼠标悬停在参数名称上来获得解释。

you can adjust the parameters to see the diffrence, check the logger box to see the process step by step. it will be helpful to prepare better doc for QA.
可以设置各参数来看不同的效果，查看日志记录窗来了解问答的工作步骤，有助于整理出更适合答疑用的文档。

need to run from a openai accessiabe network.
需要在可以访问到 openai 的网络环境里运行。