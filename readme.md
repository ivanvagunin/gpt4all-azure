*DOCUMENT CHAT BOT FUNCTION*

Azure function for running GPT4ALL document chatbot

**Running locally**
Tested on PYTHON 3.10 and PYTHON 3.11

Add local.settings.json to root folder:
```
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    "PathToModels": "./models",
    "PathToIndexes": "./indexes",
    "QuestionsConnectionString": "<PROVIDE VALID AZURE STORAGE QUEUE CONNECTION STRING, BECAUSE DEV STORAGE DOES NOT WORK WITH QUEUE CLIENT>"
  }
}
```

**Web API**
* POST /api/ask - submit question to the queue
```
{
    "question": "Summarize the document",
    "document": "HARMONISED RULES ON ARTIFICIAL INTELLIGENCE"
}
```

* GET /api/answer?id=<question_id> - poll for the answer
* GET /api/documents - get list of indexed document names


