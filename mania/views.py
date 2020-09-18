from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from .models import *
from django.contrib.auth import authenticate, login, logout
from .decorators import unauthenticated_user
from django.contrib.auth.decorators import login_required
from django.urls import reverse
# Create your views here.
from django.contrib.sites.models import Site
def index(request):
    sites = Site.objects.all()
    lst = []
    for site in sites:
        lst.append([site.id, site.domain, site.name])
    return render(request, 'merchant/index.html', {'lst':lst})

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

@login_required(login_url='index')
def merchant_dashboard(request):
    if request.user.is_merchant:
        try:
            coaching = Coaching.objects.get(merchant=request.user)
        except:
            coaching = None
        try:
            branch = Branch.objects.get(coaching=coaching)
        except:
            branch = None
        try:
            address = Address.objects.get(branch=branch)
        except:
            address = None
        try:
            course = Course.objects.get(branch=branch)
        except:
            course = None
        try:
            faculty = CoachingFacultyMember.objects.get(coaching=coaching)
        except:
            faculty = None
        try:
            batch = Batch.objects.get(course=course)
        except:
            batch = None
        try:
            info = CoachingMetaData.objects.get(coaching=coaching)
        except:
            info = None
        try:
            geolocation = Geolocation.objects.get(address=address)
        except:
            geolocation = None
        context = {'merchant': request.user, 'coaching': coaching, 'branch': branch, 'address': address, 'course': course, 
        'faculty': faculty, 'batch': batch, 'info': info, 'geolocation': geolocation}
        return render(request, 'merchant/dashboard/dashboard.html', context=context)
    return render(request, 'merchant/login_merchant.html')


@login_required
def merchant_messages(request):
    return render(request, 'merchant/dashboard/message-task.html')

@login_required
def merchant_components(request):
    return render(request, 'merchant/dashboard/component.html')
    
@login_required
def merchant_error(request):
    return render(request, 'merchant/dashboard/error.html')

@login_required
def merchant_forms(request):
    return render(request, 'merchant/dashboard/form-advance.html')

@login_required
def merchant_gallery(request):
    return render(request, 'merchant/dashboard/gallery.html')

@login_required
def merchant_invoice(request):
    return render(request, 'merchant/dashboard/invoice.html')

@login_required
def merchant_products(request):
    return render(request, 'merchant/dashboard/product.html')

@login_required
def logout_user(request):
    logout(request)
    return redirect('index')


from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
from django.views import View

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

@login_required(login_url='index')
def add_coaching(request, user):
    user = User.objects.get(email=user)
    if user.is_merchant:
        if request.method == "POST":
            name = request.POST['name']
            description = request.POST['description']
            image = request.FILES['image']
            merchant = request.user
            coaching = Coaching(name=name, description=description, merchant=merchant,logo=image)
            coaching.save()
            return HttpResponseRedirect(reverse('merchant'))
        return render(request, 'merchant/dashboard/add_coaching.html', {'merchant': user})
    return render(request, 'signup.html')

@login_required(login_url='index')
def add_coaching_metadata(request):
    if request.user.is_merchant:
        if request.method == "POST":
            name = request.POST['name']
            description = request.POST['description']
            contact1 = request.POST['contact1']
            contact2 = request.POST['contact2']
            establish = request.POST['date']
            owner_image = request.FILES['owner_image']
            merchant = request.user
            coaching = Coaching.objects.get(merchant=merchant) 
            coaching_data = CoachingMetaData(coaching=coaching, contact=contact1, help_contact=contact2, 
            owner_name=name, owner_description=description, established_on=establish,owner_image=owner_image)
            coaching_data.save()
            return HttpResponseRedirect(reverse('merchant'))
        return render(request, 'add_coaching_metadata.html', {'merchant': request.user})
    return render(request, 'signup.html')

@login_required(login_url='index')
def add_branch(request):
    if request.user.is_merchant:
        if request.method == "POST":
            name = request.POST['name']
            branch_type = request.POST['branch_type']
            merchant = request.user
            coaching = Coaching.objects.get(merchant=merchant) 
            branch = Branch(name=name, coaching=coaching, branch_type=branch_type)
            branch.save()
            return HttpResponseRedirect(reverse('merchant'))
        return render(request, 'add_branch.html', {'merchant': request.user})
    return render(request, 'signup.html')

@login_required(login_url='index')
def add_address(request):
    if request.user.is_merchant:
        merchant = request.user
        coaching = Coaching.objects.get(merchant=merchant) 
        if request.method == "POST":
            branch_taken = request.POST['branch']
            line = request.POST['line']
            apartment = request.POST['apartment']
            building = request.POST['building']
            landmark = request.POST['landmark']
            city = request.POST['city']
            district = request.POST['district']
            state = request.POST['state']
            pincode = request.POST['pincode']
            branch = Branch.objects.get(name=branch_taken)
            address = Address(line1=line, apartment=apartment, building=building, landmark=landmark, city=city,
            district=district, state=state, pincode=pincode, branch=branch)
            address.save()
            return HttpResponseRedirect(reverse('merchant'))
        branches = Branch.objects.filter(coaching=coaching)
        return render(request, 'add_address.html', {'merchant': request.user, 'branches': branches})
    return render(request, 'signup.html')

@login_required(login_url='index')
def add_course(request):
    if request.user.is_merchant:
        merchant = request.user
        coaching = Coaching.objects.get(merchant=merchant)
        if request.method == "POST":
            branch_taken = request.POST['branch']
            stream = request.POST['stream']
            name = request.POST['name']
            description = request.POST['description']
            start = request.POST['start']
            end = request.POST['end']
            fees = float(request.POST['fees'])
            currency = request.POST['currency']
            active = request.POST['active']
            branch = Branch.objects.get(name=branch_taken)
            course = Course(name=name, description=description, branch=branch, start_date=start, end_date=end, 
            stream=stream, fees=fees, currency=currency)
            myfile = request.FILES["syllabus"]
            course.syllabus = myfile
            if active == "off":
                course.is_active = False
            elif active == "on":
                course.is_active = True
            course.save()
            return HttpResponseRedirect(reverse('merchant_filter'))
        branches = Branch.objects.filter(coaching=coaching)
        return render(request, 'add_course.html', {'merchant': request.user, 'branches': branches})
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
            return HttpResponseRedirect(reverse('merchant'))
        coaching = Coaching.objects.get(merchant=merchant)
        branches = Branch.objects.filter(coaching=coaching)
        courses = set()
        for branch in branches:
            courses = courses.union(Course.objects.filter(branch=branch))
        faculties = CoachingFacultyMember.objects.filter(coaching=coaching)
        return render(request, 'add_batch.html', {'merchant': request.user, 'courses': courses, 'faculties': faculties})
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
            return HttpResponseRedirect(reverse('merchant'))
        return render(request, 'add_coaching_faculty_member.html', {'merchant': request.user})
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
        return render(request, 'merchant_filter_coaching.html', {'merchant': request.user, 'courses': other_courses})

@login_required(login_url='index')
def update_page(request):
    if request.user.is_merchant:
        try:
            coaching = Coaching.objects.get(merchant=request.user)
        except:
            coaching = None
        try:
            branches = Branch.objects.filter(coaching=coaching)
        except:
            branches = []
        try:
            all_address = []
            for branch in branches:
                all_address += list(Address.objects.filter(branch=branch))
        except:
            all_address = []
        try:
            courses = []
            for branch in branches:
                courses += list(Course.objects.filter(branch=branch))
        except:
            courses = []
        try:
            faculties = CoachingFacultyMember.objects.filter(coaching=coaching)
        except:
            faculties = []
        try:
            batches = []
            for course in courses:
                batches += list(Batch.objects.filter(course=course))
        except:
            batches = []
        try:
            info = CoachingMetaData.objects.get(coaching=coaching)
        except:
            info = None
        try:
            geolocations = []
            for address in all_address:
                geolocations += list(Geolocation.objects.filter(address=address))
        except:
            geolocations = []
        context = {'merchant': request.user, 'coaching': coaching, 'branches': branches, 
        'all_address': all_address, 'courses': courses, 
        'faculties': faculties, 'batches': batches, 'info': info, 'geolocations': geolocations}
        return render(request, 'merchant_settings.html', context=context)
    return render(request, 'login.html')

     

@login_required(login_url='index')
def add_geolocation(request):
    if request.user.is_merchant:
        merchant = request.user
        if request.method == "POST":
            id = request.POST['address']
            address = Address.objects.get(id=id)
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']
            geolocation = Geolocation(address=address, lat = latitude, lng = longitude )
            geolocation.save()
            return HttpResponseRedirect(reverse('merchant'))
        coaching = Coaching.objects.get(merchant=merchant)
        branches = Branch.objects.filter(coaching=coaching)
        all_address = []
        for branch in branches:
            all_address += list(Address.objects.filter(branch=branch))
        return render(request, 'add_geolocation.html', {'merchant': request.user, 'all_address': all_address})
    return render(request, 'signup.html')

@login_required(login_url='index')
def update_coaching(request):
    if request.user.is_merchant:
        if request.method == "POST":
            merchant = request.user
            coaching = Coaching.objects.get(merchant=merchant)
            name = request.POST['name1']
            description = request.POST['description1']
            coaching.name = name
            coaching.description = description
            try:
                image = request.FILES['image1']
            except:
                image = None
            if image:
                coaching.logo = image
            coaching.save()
            return redirect('update_page')
    return render(request, 'signup.html')

@login_required(login_url='index')
def update_coaching_metadata(request):
    if request.user.is_merchant:
        if request.method == "POST":
            coaching = Coaching.objects.get(merchant=request.user)
            info = CoachingMetaData.objects.get(coaching=coaching)
            name = request.POST['name2']
            description = request.POST['description2']
            contact1 = request.POST['contact1']
            contact2 = request.POST['contact2']
            establish = request.POST['date1']
            info.owner_name = name
            info.owner_description = description
            info.established_on = establish
            info.contact = contact1
            info.help_contact = contact2
            try:
                owner_image = request.FILES['owner_image1']
            except:
                owner_image = None
            print(owner_image)
            if owner_image:
                info.owner_image = owner_image
            info.save()
            return redirect('update_page')
    return render(request, 'signup.html')

@login_required(login_url='index')
def update_branch(request, id):
    if request.user.is_merchant:
        if request.method == "POST":
            name = request.POST['name3']
            try:
                branch_type = request.POST['branch_type']
            except:
                branch_type = None
            merchant = request.user
            coaching = Coaching.objects.get(merchant=merchant) 
            branch = Branch.objects.get(id=id)
            branch.name = name
            if branch_type:
                branch.branch_type = branch_type
            branch.save()
            return redirect('update_page')
    return render(request, 'signup.html')

@login_required(login_url='index')
def update_address(request, id):
    if request.user.is_merchant:
        merchant = request.user
        coaching = Coaching.objects.get(merchant=merchant) 
        if request.method == "POST":
            branch_taken = request.POST['branch']
            line = request.POST['line']
            apartment = request.POST['apartment']
            building = request.POST['building']
            landmark = request.POST['landmark']
            city = request.POST['city']
            district = request.POST['district']
            state = request.POST['state']
            pincode = request.POST['pincode']
            branch = Branch.objects.get(name=branch_taken)
            address = Address.objects.get(id=id)
            address.branch = branch
            address.line1 = line
            address.apartment = apartment
            address.building = building
            address.landmark = landmark
            address.city = city
            address.district = district
            address.state = state
            address.pincode = pincode
            address.save()
            return redirect('update_page')
    return render(request, 'signup.html')
    

@login_required(login_url='index')
def update_course(request, id):
    if request.user.is_merchant:
        merchant = request.user
        coaching = Coaching.objects.get(merchant=merchant)
        if request.method == "POST":
            branch_taken = request.POST['branch1']
            stream = request.POST['stream']
            name = request.POST['name4']
            description = request.POST['description4']
            start = request.POST['start']
            end = request.POST['end']
            fees = float(request.POST['fees'])
            currency = request.POST['currency']
            active = request.POST['active']
            print(active)
            branch = Branch.objects.get(name=branch_taken)
            course = Course.objects.filter(id=id).update(branch=branch, stream=stream, name=name, description=description, start_date=start, end_date=end,
            fees=fees, currency=currency)
            try:
                myfile = request.FILES["myfile"]
            except:
                myfile = None
            course = Course.objects.get(id=id)
            if myfile:
                course.syllabus = myfile
            if active == "off":
                course.is_active = False
            elif active == "on":
                course.is_active = True
            course.save()
            return redirect('update_page')
    return render(request, 'signup.html')

@login_required(login_url='index')
def update_batch(request, id):
    if request.user.is_merchant:
        merchant = request.user
        if request.method == "POST":
            name = request.POST['name6']
            limit = request.POST['limit']
            start = request.POST['start_time']
            end = request.POST['end_time']
            enrolled = float(request.POST['enrolled'])
            active = request.POST['active1']
            course_taken = request.POST['course']
            course = Course.objects.get(name=course_taken)
            faculty_taken = request.POST['faculty']
            faculty = CoachingFacultyMember.objects.get(name=faculty_taken)
            batch = Batch.objects.filter(id=id).update(name=name, student_limit=limit, start_time=start, end_time=end, students_enrolled=enrolled,
            course=course, teacher=faculty)
            batch = Batch.objects.get(id=id)
            print(active)
            if active == "off":
                batch.is_active = False
            elif active == "on":
                batch.is_active = True
            batch.save()
            return redirect('update_page')
    return render(request, 'signup.html')


@login_required(login_url='index')
def update_faculty(request, id):
    if request.user.is_merchant:
        if request.method == "POST":
            name = request.POST['name5']
            age = request.POST['age']
            specialization = request.POST['specialization']
            description = request.POST['description5']
            try:
                faculty_image = request.FILES['pic']
            except:
                faculty_image = None
            faculty = CoachingFacultyMember.objects.filter(id=id).update(name=name, age=age, specialization=specialization, meta_description=description)
            faculty = CoachingFacultyMember.objects.get(id=id)
            if faculty_image:
                faculty.faculty_image = faculty_image
            faculty.save()
            return redirect('update_page')
    return render(request, 'signup.html')

@login_required(login_url='index')
def update_geolocation(request, id):
    if request.user.is_merchant:
        if request.method == "POST":
            merchant = request.user
            geolocation = Geolocation.objects.get(id=id)
            address_id = request.POST['address']
            address = Address.objects.get(id=address_id)
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']
            geolocation.address = address
            geolocation.lat = latitude
            geolocation.lng = longitude
            geolocation.save()
            return redirect('update_page')
    return render(request, 'signup.html')