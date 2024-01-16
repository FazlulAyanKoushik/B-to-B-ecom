from rest_framework.generics import DestroyAPIView, get_object_or_404

from mediaroomio.models import MediaImage

from weapi.rest.serializers.images import PrivateImageSerializer


class PrivateImageDetail(DestroyAPIView):
    serializer_class = PrivateImageSerializer

    def get_object(self):
        return get_object_or_404(
            MediaImage.objects.filter(), uid=self.kwargs.get("uid")
        )
