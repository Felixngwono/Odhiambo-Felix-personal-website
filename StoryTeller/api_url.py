from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_view import (
    BlogPostViewSet,
    CertificationViewSet,
    EventViewSet,
    ImageGalleryViewSet,
    PortfolioItemViewSet,
    SkillViewSet,
    TaskViewSet,
)

router = DefaultRouter()
router.register(r"gallery", ImageGalleryViewSet)
router.register(r"blog", BlogPostViewSet)
router.register(r"portfolio", PortfolioItemViewSet)
router.register(r"events", EventViewSet)
router.register(r"skills", SkillViewSet)
router.register(r"certifications", CertificationViewSet)
router.register(r"tasks", TaskViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]