# chatgpt on internal doc
 a QA bot on contents of given docs
给出文档，可以基于文档进行问答的机器人。

edit .env file, paste your OPENAI_API_KEY there
编辑.env 文件，设置好你的OPENAI_API_KEY

. .env
执行 . .env 让环境变量生效.

the default doc is on Buddism, you can chat directly, if you don't want to chat on this, it's easy to make a new index file:
内置的文档是一个佛法文档，可以直接进行问答。如果你想不想对此做问答，生成新的索引文档也很容易：

copy your docs(txt, editable pdf...) into the folder: input
把若干文档（纯文本文件、可编辑的pdf）拷贝到 input 目录

python new-index.py

move the generated output file: index.json to the main folder
把生成的文件：index.json 移到主目录

运行：
nohup flask run -h 0.0.0.0 --port 8080 &

open a browser, access http://your-ip-address:8080
在浏览器里输入 http://your-ip-address:8080 , 用对外IP 或 http://127.0.0.1:8000 都可以。

ask things around your docs.
对文档内容进行提问。

you can adjust the parameters to see the diffrence, check the logger box to see the working steps.
可以设置各参数来看不同的效果，查看日志记录窗来了解问答的工作步骤。
