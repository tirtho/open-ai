import os
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.formrecognizer import *

def getFormRecognizerCredential():
  try:
    api_key = os.getenv("FORM_RECOGNIZER_API_KEY")
    if api_key and not api_key.isspace():
      # the string is non-empty      
      print("\nGot Azure Form Recognizer API Key from environment variable")
      # Return credential
      return AzureKeyCredential(api_key)
    else:
      # the string is empty
      try:
        print(f"\nCould not get API key from environment variable FORM_RECOGNIZER_API_KEY. Trying Managed ID")
        default_credential = DefaultAzureCredential()
        print("\nAuthenticated successfully with AAD token")
        return default_credential
      except:
        print("\nSomething went wrong getting token with Managed Identity")
        return
  except:
    print("\nSomething went wrong getting access key from environment variable")
    return

def getDocumentAnalysisClient(endpoint, credential):
  return DocumentAnalysisClient(endpoint, credential)

def getDocumentModelAdminClient(endpoint, credential):
  from azure.ai.formrecognizer import DocumentModelAdministrationClient
  return  DocumentModelAdministrationClient(endpoint=endpoint, credential=credential)


# Extract from local file
def extractResultFromLocalDocument(client, model, filepath):
    with open(filepath, "rb") as f:
        poller = client.begin_analyze_document(model_id=model, document=f)
    result = poller.result()
    return getExtract(result)

# Extract from Online File (e.g. from Blob Store)
def extractResultFromOnlineDocument(client, model, url):
  poller = client.begin_analyze_document_from_url(model, url)
  result = poller.result()
  return getExtract(result)

# Get metadata and results from extracted document
# Returns -
# Azure Document Intelligence API version
# Model Id
# hand_wrtten = True, If there is any hand written text found in document with confidence score of > 0.5
# result
def getExtract(result):
  hand_written = False
  for idx, style in enumerate(result.styles):
    if style.confidence > 0.5:
      hand_written = True
      break
  return result.api_version, result.model_id, hand_written, result

def getLabeledDataFromExtractedDocument(document):
  return document.doc_type, document.confidence, document.fields.items

# Train document classifier
# https://learn.microsoft.com/en-us/python/api/azure-ai-formrecognizer/azure.ai.formrecognizer.documentmodeladministrationclient?view=azure-python#Overview
def trainClassifier(admin_client, blob_url, class_file_list):
    import json
    from azure.ai.formrecognizer import (
        ClassifierDocumentTypeDetails,
        BlobSource,
        BlobFileListSource,
    )

    classifierDocTypes = {}
    for theClass in class_file_list:
      filePath = f'{class_file_list[theClass]}'
      classDocTypeDetails = ClassifierDocumentTypeDetails(
                              source=BlobFileListSource(
                                      container_url=blob_url, 
                                      file_list=filePath
                                    )
                            )
      classifierDocTypes[theClass] = classDocTypeDetails
    #print(classifierDocTypes)

    poller = admin_client.begin_build_document_classifier(
        doc_types=classifierDocTypes,
        description="Auto Insurance Email Classifier"
    )

    return poller.result()

def getClassifier(admin_client, classifier_id):
  from azure.core.exceptions import ResourceNotFoundError
  try:
    return admin_client.get_document_classifier(classifier_id)
  except ResourceNotFoundError:
    return None

def classifyDocument(client, classifier_id, file_path):
  import os
  with open(file_path, "rb") as f:
    poller = client.begin_classify_document(
                      classifier_id=classifier_id,
                      document=f
              )
  return poller.result()

def classifyDocumentFromUrl(client, classifier_id, file_url):
  poller = client.begin_classify_document_from_url(
                  classifier_id=classifier_id,
                  document_url=file_url
            )
  return poller.result()

def deleteClassifier(admin_client, classifier_id):
  admin_client.delete_document_classifier(classifier_id)
  if getClassifier(admin_client=admin_client, classifier_id=classifier_id) == None:
    print(f'Classifier {classifier_id} deleted')
