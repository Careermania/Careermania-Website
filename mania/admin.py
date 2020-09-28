from django.contrib import admin
from . models import *
admin.site.register(User)

admin.site.register(Coaching)
admin.site.register(CoachingMetaData)
admin.site.register(Branch)
admin.site.register(Address)
admin.site.register(Course)
admin.site.register(Batch)
admin.site.register(CoachingFacultyMember)
admin.site.register(Geolocation)
admin.site.register(BankAccountDetails)
admin.site.register(Merchant_Details)
admin.site.register(Message)

