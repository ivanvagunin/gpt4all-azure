import azure.functions as func

app = func.FunctionApp()

import base64
import json
import os
import logging
from document_bot import DocumentBot
from azure.data.tables import TableServiceClient
from azure.storage.queue import QueueServiceClient

questions_conn_str = os.getenv('QuestionsConnectionString')
queue_service_client = QueueServiceClient.from_connection_string(conn_str=questions_conn_str)
queue_client = queue_service_client.get_queue_client('questions')
table_service_client = TableServiceClient.from_connection_string(conn_str=questions_conn_str)
table_client = table_service_client.get_table_client(table_name="Answers")

path_to_models = os.getenv('PathToModels')
path_to_indexes = os.getenv('PathToIndexes')

# add question to the queue
@app.route(route="ask", auth_level=func.AuthLevel.ANONYMOUS, methods=['POST'] )
def ask(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
      req_body = req.get_json()
      question = req_body['question']
      index = req_body['document']

      # put question to queue
      message =  {"text": question, "index": index}
      encoded_msg = base64.b64encode(bytes(json.dumps(message), 'utf-8')).decode('utf-8')
      item = queue_client.send_message(encoded_msg) 

      # return queue message id
      response = {"id": item.id}
      return func.HttpResponse(json.dumps(response), mimetype="application/json")
    except:
       return func.HttpResponse(status_code=400)

#process question from the queue
@app.queue_trigger(arg_name="item", queue_name="questions", connection="QuestionsConnectionString") 
def process_question(item: func.QueueMessage):
    bot = DocumentBot(path_to_models + '/mistral-7b-openorca.Q4_0.gguf', path_to_indexes + '/state_of_the_union')
    # get answer from the bot
    question = json.loads(item.get_body().decode('utf-8'))
    logging.info('New question: %s', question)
    response = bot.ask(question['text'], question['index'])

    # save response to the table
    entity = {
      u'PartitionKey': 'Answer',
      u'RowKey': item.id,
      u'Question': question['text'],
      u'Document': question['index'],
      u'Answer': response
    }
    table_client.create_entity(entity=entity)
    logging.info('Response: %s', response)

# get answer from the table
@app.route(route="answer", auth_level=func.AuthLevel.ANONYMOUS, methods=['GET'] )
def answer(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    id = req.params['id']
    try:
      entity = table_client.get_entity('Answer', id)
      response = {"text": entity['Answer']}
      return func.HttpResponse(json.dumps(response), mimetype="application/json",)
    except:
        return func.HttpResponse(status_code=404)
    

# get list of indexed documents
@app.route(route="documents", auth_level=func.AuthLevel.ANONYMOUS, methods=['GET'] )
def get_indexed_documents(req: func.HttpRequest) -> func.HttpResponse:
   indexes = [name for name in os.listdir(path_to_indexes) if os.path.isdir(os.path.join(path_to_indexes, name))]
   return func.HttpResponse(json.dumps(indexes), mimetype="application/json",)
