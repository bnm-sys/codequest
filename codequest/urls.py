# codequest/urls.py (append)
from django.urls import path, include
from courses.views import EnrollView, LearningCenterView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("courses/enroll/<slug:slug>/", EnrollView.as_view(), name="enroll"),
    path("courses/<slug:slug>/learning-center/", LearningCenterView.as_view(), name="learning_center"),
]
