from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from langchain.docstore.document import Document
import numpy as np
from .serializers import TicketSerializer, PredictionSerializer
from .qdrant_utils import vectorstore

# ---------------------------------------------------------------------------
# COLLECT API - Stores a new ticket into Qdrant
# ---------------------------------------------------------------------------
class CollectTicketView(APIView):
    def post(self, request):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            page_content = (
                f"Ticket ID: {data['ticket_id']}, Summary: {data['summary']}, "
                f"Description: {data['description']}, Priority: {data['priority']}, "
                f"Status: {data['status']}, Reporter: {data['reporter']}, "
                f"Label: {data['label']}, Created At: {data['created_at']}"
            )
            metadata = serializer.validated_data

            # Create document object
            doc = Document(page_content=page_content, metadata=metadata)

            # Store in Qdrant
            vectorstore.add_documents([doc])

            return Response({"message": "Ticket collected successfully", "ticket_id": data["ticket_id"]}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# PREDICT API - Finds similar tickets & returns top labels with confidence
# ---------------------------------------------------------------------------
class PredictLabelView(APIView):
    def post(self, request):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            query_text = (
                f"Ticket ID: {data['ticket_id']}, Summary: {data['summary']}, "
                f"Description: {data['description']}, Priority: {data['priority']}, "
                f"Status: {data['status']}, Reporter: {data['reporter']}, "
                f"Created At: {data['created_at']}"
            )

            # Search in Qdrant
            results = vectorstore.similarity_search_with_score(query=query_text, k=5)

            if not results:
                return Response([], status=status.HTTP_200_OK)

            # Extract scores
            scores = np.array([score for _, score in results])

            # Softmax function to compute confidence scores
            def softmax(x: np.ndarray):
                exp_x = np.exp(x - np.max(x))
                return exp_x / exp_x.sum()

            confidence_scores = softmax(scores)

            response = [
                {"label": doc.metadata.get("label", "Unknown"), "confidence": float(conf_score)}
                for (doc, _), conf_score in zip(results, confidence_scores)
            ]


            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
