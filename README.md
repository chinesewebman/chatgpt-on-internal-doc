# chatgpt on internal doc
 a QA bot on contents of given docs

edit .env file, paste your OPENAI_API_KEY there
. .env

to make a new index file: 
copy your docs(txt, editable pdf...) into the folder: input

edit new-index.py to update your OPENAI_API_KEY
python new-index.py
move the generated output file: index.json to the main folder

nohup flask run -h 0.0.0.0 --port 8080 &

open a browser, access http://your-ip-address:8080
ask things around your docs.
you can adjust the parameters to see the diffrence, check the logger box to see the working steps.