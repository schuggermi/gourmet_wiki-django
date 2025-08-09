from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny

from ingredients.models import IngredientLookup


class IngredientLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientLookup
        fields = ['fdc_id', 'description']


class IngredientLookupSearchView(generics.ListAPIView):
    serializer_class = IngredientLookupSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return IngredientLookup.objects.filter(description__icontains=query).order_by('description')[:20]
        return IngredientLookup.objects.none()


IngredientLookupSearchView.serializer_class = IngredientLookupSerializer
