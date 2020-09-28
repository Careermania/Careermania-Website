from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from .models import *
from django.contrib.auth import authenticate, login, logout
from .decorators import unauthenticated_user
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.sites.models import Site
# Create your views here.
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
from django.views import View
from datetime import *


def send_confirmation_email(request, user):
    current_site = get_current_site(request)
    email_subject = 'Activate Your Account'
    message = render_to_string('confirmation/activate.html',
                            {
                                'user': user, 
                                'domain': current_site.domain, 
                                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                'token': generate_token.make_token(user)
                            })

    email_message = EmailMessage(
    email_subject,
    message,
    settings.EMAIL_HOST_USER,
    [user.email],
    )

    email_message.send()

def add_forms_mail(request, user):
    current_site = get_current_site(request)
    email_subject = 'Fill the Information'
    message = render_to_string('merchant/forms.html',
                            {
                                'user': user, 
                                'domain': current_site.domain, 
                            })

    email_message = EmailMessage(
    email_subject,
    message,
    settings.EMAIL_HOST_USER,
    [user.email],
    )

    email_message.send()

class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except:
            user = None
        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.add_message(request, messages.INFO, 'Account Activated Successfully.')
            add_forms_mail(request, user)
            return redirect('login_merchant')
        return render(request, 'confirmation/activate_failed.html', status=401)

#from django.contrib.sites.models import Site
def index(request):
    """sites = Site.objects.all()
    for site in sites:
        print(site.id, site.domain)"""
    return render(request, 'merchant/index.html')

def register_merchant(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        mobile = request.POST['mobile']
        stream = request.POST['stream']
        password = request.POST['password']
        organization = request.POST['organization']
        try:
            try:
                user = User.objects.get(email=email)
                if user:
                    return render(request, 'merchant/signup_merchant.html', {'error': 'User already exist with this email.'})
            except:
                user = User.objects.get(username=username)
                if user:
                    return render(request, 'merchant/signup_merchant.html', {'error': 'User already exist with this Username.'})
        except:
            user = User.objects.create_merchant(email, username, password)
            user.is_active = False
            user.save()
            merchant = Merchant_Details(first_name=fname, last_name=lname, email=email, mobile=mobile, organization=organization,
            stream=stream, merchant=user)
            merchant.save()
            send_confirmation_email(request, user)
            return render(request, 'merchant/signup_merchant.html', {'success': 'Verification Mail Sent Successfully. Please Verify your Account.'})
           
    return render(request, "merchant/signup_merchant.html")

def login_merchant(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(email=email, password=password)
        if user is not None and user.is_merchant:
            login(request, user)
            return HttpResponseRedirect(reverse('merchant'))
        return render(request, 'merchant/login_merchant.html', {'error': 'Invalid Username or Password.'})
    return render(request, 'merchant/login_merchant.html')

def forms_details(request, user):
    user = User.objects.get(username=str(user))
    if user.is_merchant:
        try:
            coaching = Coaching.objects.get(merchant=user)
        except:
            coaching = None
        try:
            info = CoachingMetaData.objects.get(coaching=coaching)
        except:
            info = None
        if not coaching:
            return redirect('add_coaching', user=user.username)
        if not info:
            return redirect('add_coaching_metadata', user=user.username)
        return redirect("index")
    return render(request, 'merchant/login_merchant.html')

@login_required(login_url='index')
def merchant_dashboard(request):
    if request.user.is_merchant:
        coaching = Coaching.objects.get(merchant=request.user)
        context = {'merchant': request.user, 'coaching':coaching}
        return render(request, 'merchant/new_dashboard/merchant_dashboard.html', context=context)
    return render(request, 'merchant/login_merchant.html')


@login_required
def merchant_messages(request):
    if request.user.is_merchant:
        coaching = Coaching.objects.get(merchant=request.user)
        receiver = User.objects.get(username="pratik")
        if request.method=="POST":
            msg = request.POST['msg']
            print(msg)
            message = Message(sender=request.user, receiver=receiver, message=msg, timestamp=datetime.now())
            message.save()
            print(message)
            return redirect('merchant_messages')
        messages = list(Message.objects.filter(sender=request.user).filter(receiver=receiver))
        messages += list(Message.objects.filter(sender=receiver).filter(receiver=request.user))
        from operator import attrgetter
        messages = sorted(messages, key=attrgetter('id'))
        context = {'messages': messages, 'merchant': request.user, 'coaching':coaching}
        print(messages)
        return render(request, 'merchant/new_dashboard/chat.html', context)

@login_required
def merchant_table(request):
    return render(request, 'merchant/new_dashboard/export-table.html')
    
@login_required
def merchant_contact(request):
    return render(request, 'merchant/new_dashboard/contact.html')

@login_required
def merchant_forms2(request):
    return render(request, 'merchant/new_dashboard/basic-form2.html')

@login_required
def merchant_gallery(request):
    return render(request, 'merchant/new_dashboard/gallery1.html')

@login_required
def merchant_invoice(request):
    return render(request, 'merchant/new_dashboard/invoice.html')

@login_required
def merchant_payment(request):
    if request.user.is_merchant:
        coaching = Coaching.objects.get(merchant=request.user)
        try:
            payment = BankAccountDetails.objects.get(coaching=coaching)
        except:
            payment = None
        if request.method == "POST":
            account_holder = request.POST['name']
            bank_name = request.POST['bank_name']
            ifsc = request.POST['ifsc']
            mobile = request.POST['mobile']
            try:
                adhar = request.FILES['adhar']
            except:
                adhar = None
            try:
                pan = request.FILES['pan']
            except:
                pan = None
            account_no = request.POST['number']
            if payment:
                payment = BankAccountDetails.objects.filter(coaching=coaching).update(account_holder=account_holder,
                 account_no=account_no, ifsc_code=ifsc, bank_name=bank_name, mobile_no=mobile)
                payment = BankAccountDetails.objects.get(coaching=coaching)
                if adhar:
                    payment.adhar_card = adhar
                if pan:
                    payment.pan_card = pan
                payment.save()
            else:
                payment = BankAccountDetails(account_holder=account_holder, account_no=account_no, ifsc_code=ifsc, bank_name=bank_name,
                adhar_card=adhar, pan_card=pan, coaching=coaching, mobile_no=mobile)
                payment.save()
            return redirect('payment')
        context = {'merchant': request.user, 'coaching':coaching, 'account': payment}
        return render(request, 'merchant/new_dashboard/payment.html', context)

@login_required(login_url='index')
def merchant_profile(request):
    if request.user.is_merchant:
        info = Merchant_Details.objects.get(merchant=request.user)
        coaching = Coaching.objects.get(merchant=request.user)
        if request.method == "POST":
            fname = request.POST['fname']
            lname = request.POST['lname']
            mobile = request.POST['mobile']
            organization = request.POST['organization']
            stream = request.POST['stream']
            info = Merchant_Details.objects.filter(id=info.id).update(first_name=fname, last_name=lname, mobile=mobile, organization=organization, stream=stream)
            return redirect('merchant_profile')
        context = {'info': info, 'merchant': request.user, 'coaching':coaching}
        return render(request, 'merchant/new_dashboard/profile.html', context)
    return render(request, 'signup.html')

@login_required
def logout_user(request):
    logout(request)
    return redirect('index')

def add_coaching(request, user):
    user = User.objects.get(username=user)
    if user.is_merchant:
        if request.method == "POST":
            name = request.POST['name']
            description = request.POST['description']
            image = request.FILES['image']
            merchant = user
            coaching = Coaching(name=name, description=description, merchant=merchant,logo=image)
            coaching.save()
            return redirect('add_coaching_metadata', user=user.username)
        return render(request, 'merchant/dashboard/add_coaching.html', {'merchant': user})
    return render(request, 'signup.html')

def add_coaching_metadata(request, user):
    user = User.objects.get(username=user)
    if user.is_merchant:
        if request.method == "POST":
            name = request.POST['name']
            description = request.POST['description']
            contact1 = request.POST['contact1']
            contact2 = request.POST['contact2']
            establish = request.POST['date']
            owner_image = request.FILES['owner_image']
            merchant = user
            coaching = Coaching.objects.get(merchant=merchant) 
            coaching_data = CoachingMetaData(coaching=coaching, contact=contact1, help_contact=contact2, 
            owner_name=name, owner_description=description, established_on=establish,owner_image=owner_image)
            coaching_data.save()
            return redirect('index')
        return render(request, 'merchant/dashboard/add_coaching_metadata.html', {'merchant': user})
    return render(request, 'signup.html')

@login_required(login_url='index')
def update_coaching(request):
    if request.user.is_merchant:
        merchant = request.user
        coaching = Coaching.objects.get(merchant=merchant)
        if request.method == "POST":   
            name = request.POST['name']
            description = request.POST['description']
            coaching.name = name
            coaching.description = description
            try:
                image = request.FILES['logo']
            except:
                image = None
            if image:
                coaching.logo = image
            coaching.save()
            return redirect('coaching')
        context = {'merchant': request.user, 'coaching':coaching}
        return render(request, 'merchant/new_dashboard/coaching.html', context=context)
    return render(request, 'signup.html')

@login_required(login_url='index')
def update_coaching_metadata(request):
    if request.user.is_merchant:
        coaching = Coaching.objects.get(merchant=request.user)
        info = CoachingMetaData.objects.get(coaching=coaching)
        if request.method == "POST":
            name = request.POST['name']
            description = request.POST['description']
            contact1 = request.POST['contact1']
            contact2 = request.POST['contact2']
            establish = request.POST['date']
            info.owner_name = name
            info.owner_description = description
            info.established_on = establish
            info.contact = contact1
            info.help_contact = contact2
            try:
                owner_image = request.FILES['owner_image']
            except:
                owner_image = None
            print(owner_image)
            if owner_image:
                info.owner_image = owner_image
            info.save()
            return redirect('owner')
        context = {'merchant': request.user, 'coaching':coaching, 'owner': info}
        return render(request, 'merchant/new_dashboard/owner.html', context)
    return render(request, 'signup.html')

@login_required(login_url='index')
def add_branch(request):
    if request.user.is_merchant:
        merchant = request.user
        coaching = Coaching.objects.get(merchant=merchant)
        if request.method == "POST":
            name = request.POST['name']
            branch_type = request.POST['branch_type']
            branch = Branch(name=name, coaching=coaching, branch_type=branch_type)
            branch.save()
            line = request.POST['line']
            apartment = request.POST['apartment']
            building = request.POST['building']
            landmark = request.POST['landmark']
            city = request.POST['city']
            district = request.POST['district']
            state = request.POST['state']
            pincode = request.POST['pincode']
            address = Address(line1=line, apartment=apartment, building=building, landmark=landmark, city=city,
            district=district, state=state, pincode=pincode, branch=branch)
            address.save()
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']
            geolocation = Geolocation(address=address, lat = latitude, lng = longitude )
            geolocation.save()
            return redirect('add_branch')
        all_address = []
        geolocations = []
        branches = Branch.objects.filter(coaching=coaching)
        for branch in branches:
            all_address += list(Address.objects.filter(branch=branch))
        for address in all_address:
            geolocations += list(Geolocation.objects.filter(id=address.id))
        context = {'merchant': request.user, 'coaching':coaching, 'branches': branches, 'all_address': all_address, 'geolocations': geolocations}
        return render(request, 'merchant/new_dashboard/branch.html', context)
    return render(request, 'signup.html')

@login_required(login_url='index')
def update_branch(request, id):
    if request.user.is_merchant:
        merchant = request.user
        coaching = Coaching.objects.get(merchant=merchant)
        geolocation = Geolocation.objects.get(id=id)
        if request.method == "POST":
            name = request.POST['name']
            branch_type = request.POST['branch_type']
            line = request.POST['line']
            apartment = request.POST['apartment']
            building = request.POST['building']
            landmark = request.POST['landmark']
            city = request.POST['city']
            district = request.POST['district']
            state = request.POST['state']
            pincode = request.POST['pincode']
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']
            geolocation = Geolocation.objects.filter(id=id).update(lat=latitude, lng=longitude)
            geolocation = Geolocation.objects.get(id=id)
            address = Address.objects.filter(id=geolocation.address.id).update(line1=line, apartment=apartment, building=building, landmark=landmark, city=city,
            district=district, state=state, pincode=pincode)
            address = Address.objects.get(id=geolocation.address.id)
            branch = Branch.objects.filter(id=address.branch.id).update(name=name, branch_type=branch_type)
            return redirect('add_branch')
        all_address = []
        geolocations = []
        branches = Branch.objects.filter(coaching=coaching)
        for branch in branches:
            all_address += list(Address.objects.filter(branch=branch))
        for address in all_address:
            geolocations += list(Geolocation.objects.filter(id=address.id))
        context = {'merchant': request.user, 'coaching':coaching, 'branches': branches, 'all_address': all_address, 'geolocations': geolocations, 'geolocation': geolocation}
        return render(request, 'merchant/new_dashboard/branch.html', context)
    return render(request, 'signup.html')

@login_required(login_url='index')
def delete_branch(request, id):
    if request.user.is_merchant:
        geolocation = Geolocation.objects.get(id=id)
        address = Address.objects.get(id=geolocation.address.id)
        branch = Branch.objects.get(id=address.branch.id)
        branch.delete()
        address.delete()
        geolocation.delete()
        return redirect('add_branch')
    return render(request, 'signup.html')

@login_required(login_url='index')
def merchant_courses(request):
    if request.user.is_merchant:
        coaching = Coaching.objects.get(merchant=request.user)
        branches = Branch.objects.filter(coaching=coaching)
        courses = Course.objects.filter(coaching=coaching)
        context = {'courses': courses, 'merchant': request.user, 'coaching':coaching}
        branches = Branch.objects.filter(coaching=coaching)
        return render(request, 'merchant/new_dashboard/courses.html', context)

@login_required(login_url='index')
def add_course(request):
    if request.user.is_merchant:
        merchant = request.user
        coaching = Coaching.objects.get(merchant=merchant)
        if request.method == "POST":
            branch_taken = request.POST['branch']
            details = Merchant_Details.objects.get(merchant=merchant)
            stream = details.stream
            name = request.POST['name']
            description = request.POST['description']
            start = request.POST['start']
            end = request.POST['end']
            fees = float(request.POST['fees'])
            currency = request.POST['currency']
            active = request.POST['active']
            branch = Branch.objects.get(name=branch_taken)
            course = Course(name=name, description=description, branch=branch, start_date=start, end_date=end, 
            stream=stream, fees=fees, currency=currency, coaching=coaching)
            myfile = request.FILES["syllabus"]
            course.syllabus = myfile
            if active == "off":
                course.is_active = False
            elif active == "on":
                course.is_active = True
            course.save()
            return redirect('add_course')
        branches = Branch.objects.filter(coaching=coaching)
        context = {'merchant': request.user, 'coaching':coaching, 'branches': branches}
        return render(request, 'merchant/new_dashboard/add_course.html', context)
    return render(request, 'merchant/signup_merchant.html')

@login_required(login_url='index')
def update_course(request, id):
    if request.user.is_merchant:
        merchant = request.user
        coaching = Coaching.objects.get(merchant=merchant)
        if request.method == "POST":
            branch_taken = request.POST['branch']
            details = Merchant_Details.objects.get(merchant=merchant)
            stream = details.stream
            name = request.POST['name']
            description = request.POST['description']
            start = request.POST['start']
            end = request.POST['end']
            fees = float(request.POST['fees'])
            currency = request.POST['currency']
            active = request.POST['active']
            branch = Branch.objects.get(name=branch_taken)
            course = Course.objects.filter(id=id).update(name=name, description=description, branch=branch, start_date=start, end_date=end, 
            stream=stream, fees=fees, currency=currency)
            course = Course.objects.get(id=id)
            try:
                myfile = request.FILES["syllabus"]
                course.syllabus = myfile
            except:
                myfile = None           
            if active == "off":
                course.is_active = False
            elif active == "on":
                course.is_active = True
            course.save()
            return redirect('merchant_courses')
        branches = Branch.objects.filter(coaching=coaching)
        course = Course.objects.get(id=id)
        context = {'merchant': request.user, 'coaching':coaching, 'branches': branches, 'course': course}
        return render(request, 'merchant/new_dashboard/add_course.html', context)
    return render(request, 'merchant/signup_merchant.html')

@login_required(login_url='index')
def delete_course(request, id):
    if request.user.is_merchant:
        course = Course.objects.get(id=id)
        course.delete()
        return redirect('merchant_courses')
    return render(request, 'signup.html')

@login_required(login_url='index')
def add_faculty(request):
    if request.user.is_merchant:
        merchant = request.user
        coaching = Coaching.objects.get(merchant=merchant)
        if request.method == "POST":
            name = request.POST['name']
            age = request.POST['age']
            specialization = request.POST['specialization']
            description = request.POST['description']
            faculty_image = request.FILES['pic']
            faculty = CoachingFacultyMember(name=name, age=age, specialization=specialization, meta_description=description,
            coaching=coaching,faculty_image=faculty_image)
            faculty.save()
            return redirect('add_faculty')
        faculties = CoachingFacultyMember.objects.filter(coaching=coaching)
        context = {'merchant': request.user, 'coaching':coaching, 'faculties': faculties}
        return render(request, 'merchant/new_dashboard/faculty.html', context)
    return render(request, 'merchant/signup_merchant.html')

@login_required(login_url='index')
def update_faculty(request, id):
    if request.user.is_merchant:
        coaching = Coaching.objects.get(merchant=request.user)
        if request.method == "POST":
            name = request.POST['name']
            age = request.POST['age']
            specialization = request.POST['specialization']
            description = request.POST['description']
            try:
                faculty_image = request.FILES['pic']
            except:
                faculty_image = None
            faculty = CoachingFacultyMember.objects.filter(id=id).update(name=name, age=age, specialization=specialization, meta_description=description)
            faculty = CoachingFacultyMember.objects.get(id=id)
            if faculty_image:
                faculty.faculty_image = faculty_image
            faculty.save()
            return redirect('add_faculty')
        faculties = CoachingFacultyMember.objects.filter(coaching=coaching)
        faculty = CoachingFacultyMember.objects.get(id=id)
        context = {'merchant': request.user, 'coaching':coaching, 'faculties': faculties, 'edit_faculty': faculty}
        return render(request, 'merchant/new_dashboard/faculty.html', context)
    return render(request, 'merchant/signup_merchant.html')

@login_required(login_url='index')
def delete_faculty(request, id):
    if request.user.is_merchant:
        faculty = CoachingFacultyMember.objects.get(id=id)
        faculty.delete()
        return redirect('add_faculty')
    return render(request, 'signup.html')

@login_required(login_url='index')
def add_batch(request):
    if request.user.is_merchant:
        merchant = request.user
        if request.method == "POST":
            name = request.POST['name']
            limit = request.POST['limit']
            start = request.POST['start']
            end = request.POST['end']
            enrolled = float(request.POST['enrolled'])
            active = request.POST['active']
            course_taken = request.POST['course']
            course = Course.objects.get(name=course_taken)
            faculty_taken = request.POST['faculty']
            faculty = CoachingFacultyMember.objects.get(name=faculty_taken)
            batch = Batch(name=name, student_limit=limit, start_time=start, end_time=end, students_enrolled=enrolled,
            course=course, teacher=faculty)
            if active == "off":
                batch.is_active = False
            elif active == "on":
                batch.is_active = True
            batch.save()
            return redirect('add_batch')
        coaching = Coaching.objects.get(merchant=merchant)
        branches = Branch.objects.filter(coaching=coaching)
        batches = []
        courses = Course.objects.filter(coaching=coaching)
        for course in courses:
            batches += list(Batch.objects.filter(course=course))
        faculties = CoachingFacultyMember.objects.filter(coaching=coaching)
        context = {'merchant': request.user, 'coaching':coaching, 'courses': courses, 'faculties': faculties, 'batches':batches}
        return render(request, 'merchant/new_dashboard/batch.html', context)
    return render(request, 'merchant/signup_merchant.html')

@login_required(login_url='index')
def update_batch(request, id):
    if request.user.is_merchant:
        merchant = request.user
        batch = Batch.objects.get(id=id)
        if request.method == "POST":
            name = request.POST['name']
            limit = request.POST['limit']
            start = request.POST['start']
            end = request.POST['end']
            enrolled = float(request.POST['enrolled'])
            active = request.POST['active']
            course_taken = request.POST['course']
            course = Course.objects.get(name=course_taken)
            faculty_taken = request.POST['faculty']
            faculty = CoachingFacultyMember.objects.get(name=faculty_taken)
            batch = Batch.objects.filter(id=id).update(name=name, student_limit=limit, start_time=start, end_time=end, students_enrolled=enrolled,
            course=course, teacher=faculty)
            batch = Batch.objects.get(id=id)
            if active == "off":
                batch.is_active = False
            elif active == "on":
                batch.is_active = True
            batch.save()
            return redirect('add_batch')
        coaching = Coaching.objects.get(merchant=merchant)
        branches = Branch.objects.filter(coaching=coaching)
        courses = []
        batches = []
        for branch in branches:
            courses += list(Course.objects.filter(branch=branch))
        for course in courses:
            batches += list(Batch.objects.filter(course=course))
        faculties = CoachingFacultyMember.objects.filter(coaching=coaching)
        context = {'merchant': request.user, 'coaching':coaching, 'courses': courses, 'faculties': faculties, 'batches':batches, 'edit_batch': batch}
        return render(request, 'merchant/new_dashboard/batch.html', context)
    return render(request, 'signup.html')

@login_required(login_url='index')
def delete_batch(request, id):
    if request.user.is_merchant:
        batch = Batch.objects.get(id=id)
        batch.delete()
        return redirect('add_batch')
    return render(request, 'signup.html')

@login_required(login_url='index')
def add_offer(request):
    if request.user.is_merchant:
        coaching = Coaching.objects.get(merchant=request.user)
        if request.method == "POST":
            name = request.POST['name']
            description = request.POST['description']
            offer = Offer(name=name, description=description, coaching=coaching)
            offer.save()
            return redirect('add_offer')
        offers = Offer.objects.filter(coaching=coaching)
        return render(request, 'merchant/new_dashboard/offer.html', {'offers': offers, 'merchant': request.user, 'coaching':coaching})
    return render(request, 'signup.html')

@login_required(login_url='index')
def update_offer(request, id):
    if request.user.is_merchant:
        coaching = Coaching.objects.get(merchant=request.user)
        offer = Offer.objects.get(id=id)
        if request.method == "POST":
            name = request.POST['name']
            description = request.POST['description']
            offer.name = name
            offer.description = description
            offer.save()
            return redirect('add_offer')
        offers = Offer.objects.filter(coaching=coaching)
        return render(request, 'merchant/new_dashboard/offer.html', {'offers': offers, 'edit_offer': offer, 'merchant': request.user, 'coaching':coaching})
    return render(request, 'signup.html')

@login_required(login_url='index')
def delete_offer(request, id):
    if request.user.is_merchant:
        offer = Offer.objects.get(id=id)
        offer.delete()
        return redirect('add_offer')
    return render(request, 'signup.html')

@login_required(login_url='index')
def add_discount(request):
    if request.user.is_merchant:
        coaching = Coaching.objects.get(merchant=request.user)
        if request.method == "POST":
            coupon = request.POST['coupon']
            description = request.POST['description']
            percent = request.POST['percent']
            discount = Discount(disc_code=coupon, description=description, disc_percent=percent, coaching=coaching)
            discount.save()
            return redirect('add_discount')
        discounts = Discount.objects.filter(coaching=coaching)
        return render(request, 'merchant/new_dashboard/discount.html', {'discounts': discounts, 'merchant': request.user, 'coaching':coaching})
    return render(request, 'signup.html')

@login_required(login_url='index')
def update_discount(request, id):
    if request.user.is_merchant:
        coaching = Coaching.objects.get(merchant=request.user)
        discount = Discount.objects.get(id=id)
        if request.method == "POST":
            coupon = request.POST['coupon']
            description = request.POST['description']
            percent = request.POST['percent']
            discount.disc_code = coupon
            discount.description = description
            discount.disc_percent = percent
            discount.save()
            return redirect('add_discount')
        discounts = Discount.objects.filter(coaching=coaching)
        return render(request, 'merchant/new_dashboard/discount.html', {'discounts': discounts, 'edit_discount': discount, 'merchant': request.user, 'coaching':coaching})
    return render(request, 'signup.html')

@login_required(login_url='index')
def delete_discount(request, id):
    if request.user.is_merchant:
        discount = Discount.objects.get(id=id)
        discount.delete()
        return redirect('add_discount')
    return render(request, 'signup.html')


@login_required(login_url='index')
def merchant_filter_coaching(request):
    if request.user.is_merchant:
        merchant = request.user
        coaching = Coaching.objects.get(merchant=merchant)
        branches = Branch.objects.filter(coaching=coaching)
        courses = []
        for branch in branches:
            courses = courses + list(Course.objects.filter(branch=branch))
        name_of_course = courses[0].stream
        other_courses = Course.objects.filter(stream=name_of_course)
        return render(request, 'merchant_filter_coaching.html', {'merchant': request.user, 'coaching':coaching, 'courses': other_courses})




