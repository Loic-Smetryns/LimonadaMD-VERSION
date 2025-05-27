from rest_framework.serializers import HyperlinkedModelSerializer, Field

from .models import Reference

class ReferenceSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Reference
        fields = [ 'doi', 'title', 'journal', 'year', 'date', 'volume', 'refid' ]

class FileField(Field):
    """
    Custom serializer field for handling file URLs with absolute URI generation.

    This field serializes FileField content to return:
    - Empty string if filename is empty
    - Absolute URI if request context is available
    - Relative URL if no request context is present
    """
    
    def to_representation(self, file):
        request = self.context.get('request')
        
        if file.name == "":
            return ""
        
        return request.build_absolute_uri(file.url) if request is not None else file.url
    
class UrlField(Field):
    """
    Custom serializer field for handling URLs with absolute URI generation.

    This field serializes URL content to return:
    - Absolute URI if request context is available
    - Original URL if no request context is present
    """
    
    def to_representation(self, url):
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request is not None else url