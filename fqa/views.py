from rest_framework.generics import ListAPIView

from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import FAQ
from .serializers import FAQSerializer

class FAQListView(ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]
    
class FAQByCategoryListView(ListAPIView):
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category = self.kwargs['category']
        return FAQ.objects.filter(category=category)