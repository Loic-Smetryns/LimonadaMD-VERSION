# -*- coding: utf-8; Mode: python; tab-width: 4; indent-tabs-mode:nil; -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
#    Limonada is accessible at https://limonada.univ-reims.fr/
#    Copyright (C) 2016-2020 - The Limonada Team (see the AUTHORS file)
#
#    This file is part of Limonada.
#
#    Limonada is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Limonada is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Limonada.  If not, see <http://www.gnu.org/licenses/>.

"""limonada URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

# Django
from django.conf import settings
from django.urls import path, include as inc
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

# Django REST framework
from rest_framework.schemas import get_schema_view

# local Django
from .views import bad_request_view, get_error, error_view, page_not_found_view, permission_denied_view
from membranes.views import APIMemList, APIMemDetails
from lipids.views import APILipidList, APILipidDetails, APITopolList, APITopolDetails
from forcefields.views import APIFfList, APIFfDetails

handler400 = bad_request_view.as_view()
handler403 = permission_denied_view.as_view()
handler404 = page_not_found_view.as_view()
handler500 = error_view
handler502 = get_error.as_view()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('homepage.urls')),
    url(r'^', include('lipids.urls')),
    url(r'^', include('forcefields.urls')),
    url(r'^', include('membranes.urls')),
    url(r'^', include('properties.urls')),
    url(r'^', include('documentation.urls')),
    url(r'^', include('users.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
    URL API
"""

urlpatterns_api = [
    url(r'^api/v1/membranes/$', APIMemList.as_view(), name="api-memlist"),
    url(r'^api/v1/membranes/(?P<pk>\d+)/$', APIMemDetails.as_view(), name="api-memdetail"),
    url(r'^api/v1/lipids/$', APILipidList.as_view(), name='api-liplist'),
    url(r'^api/v1/lipids/(?P<slug>\w+)/$', APILipidDetails.as_view(), name='api-lipdetail'),
    url(r'^api/v1/topologies/$', APITopolList.as_view(), name="api-toplist"),
    url(r'^api/v1/topologies/(?P<pk>\d+)/$', APITopolDetails.as_view(), name="api-topdetail"),
    url(r'^api/v1/forcefields/$', APIFfList.as_view(), name="api-fflist"),
    url(r'^api/v1/forcefields/(?P<pk>\d+)/$', APIFfDetails.as_view(), name="api-ffdetail")
]

urlpatterns += urlpatterns_api + [
    url(r'^api/v1/$', get_schema_view(
            title="Limonada REST API",
            description=
            "The Limonada REST API is a comprehensive web service designed to provide access to a rich "+
            "dataset of molecular dynamics simulations, focusing on force fields, lipids, membranes, "+
            "and topologies. This API is intended for researchers, scientists, and developers who need "+
            "detailed and structured information for their simulations and analyses.",
            version="1.0.0",
            patterns=urlpatterns_api,
        )
    ),
]

if settings.DEBUG:
    import debug_toolbar
    
    urlpatterns = [
        url(r'^__debug__/', include('debug_toolbar.urls')),
    ] + urlpatterns
