from firebase_functions.firestore_fn import (
  on_document_written,
  Event,
  Change,
  DocumentSnapshot,
)

@on_document_written(document="wizard/{sessionId}", region="europe-west3")
def onAuroraEvents(event: Event[Change[DocumentSnapshot]]) -> None:
  print(f"new file written: '{event.params["sessionId"]}'")
  print(f"value: {event.data.value.to_dict()}")
