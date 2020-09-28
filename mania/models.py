from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_merchant(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_staff = False
        user.is_superuser = False
        user.is_student = False
        user.is_active = False
        user.is_merchant = True
        user.save(using=self._db)
        return user

    def create_student(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_staff = False
        user.is_superuser = False
        user.is_merchant = False
        user.is_student = True
        user.is_active = False
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    name = models.CharField(max_length=255, blank=True, null=True)
    registered_date = models.DateTimeField(blank=True, null=True, default=timezone.now)
    email = models.EmailField(max_length=250, unique=True, db_index=True)
    username = models.CharField(max_length=250)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_merchant = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']
    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

import uuid
from django.db import models

class Merchant_Details(models.Model):
    Stream_CHOICES = (
        ('Science', 'Science'),
        ('Commerce', 'Commerce'),
        ('Arts', 'Arts'),
        ('Music', 'Music'),
        ('Dance', 'Dance'),
        ('Sports', 'Sports'),
    )
    id = models.AutoField(primary_key=True)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    merchant = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=250,blank=False,null=False)
    last_name = models.CharField(max_length=250,blank=False,null=False)
    organization = models.CharField(max_length=250,blank=False,null=False)
    email = models.CharField(max_length=250,blank=False,null=False)
    mobile = models.CharField(max_length=250,blank=False,null=False)
    stream = models.CharField(max_length=250,blank=False,null=False,
                                    verbose_name='coaching_stream',choices=Stream_CHOICES, default=None
                                        )
    def __str__(self):
        return self.first_name + " " + self.last_name
    

class Coaching(models.Model):
    id = models.AutoField(primary_key=True)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    merchant = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=250,unique=True,blank=False,null=False)
    description = models.TextField(blank=False,null=False)
    logo = models.ImageField(upload_to='logos/',blank=True , null=True)
    logo_link = models.URLField()

    def __str__(self):
        return self.name


class Branch(models.Model):
    Type_CHOICES = (
        ('Main', 'Main'),
        ('Sub', 'Sub')
    )

    id = models.AutoField(primary_key=True)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=250,blank=False,null=False,verbose_name='coaching_branch_name')
    coaching = models.ForeignKey(Coaching, related_name = 'branches',on_delete=models.CASCADE)
    branch_type = models.CharField(max_length=250,blank=False,null=False,
                                    verbose_name='coaching_branch',choices=Type_CHOICES, default="Main"
                                        )
    
    def __str__(self):
        return self.name

class Address(models.Model):
    id = models.AutoField(primary_key=True)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    branch = models.OneToOneField(Branch,related_name='address_of',on_delete=models.CASCADE)
    line1 = models.CharField(max_length=250,blank=False,null=False)
    city = models.CharField(max_length=250,blank=True,null=True)
    apartment = models.CharField(max_length=250,blank=True,null=True)
    building = models.CharField(max_length=250,blank=True,null=True)
    landmark = models.CharField(max_length=250,blank=True,null=True)
    district = models.CharField(max_length=250,blank=False,null=False,default=None)
    state = models.CharField(max_length=250,blank=False,null=False,default=None)
    pincode = models.CharField(max_length=250,blank=False,null=False,default=None)

    def __str__(self):
        return  self.apartment + ", " +  self.building + ", "  + self.line1 + ", " + self.city 

    

class Geolocation(models.Model):
    id = models.AutoField(primary_key=True)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    address = models.OneToOneField(Address,related_name='location_of',on_delete=models.CASCADE)
    lat = models.DecimalField(decimal_places=2,max_digits=10,null=False,default=None)
    lng = models.DecimalField(decimal_places=2,max_digits=10,null=False,default=None)

    def __str__(self):
        return str(self.address)

class Course(models.Model):

    Stream_CHOICES = (
        ('Science', 'Science'),
        ('Commerce', 'Commerce'),
        ('Arts', 'Arts'),
        ('Music', 'Music'),
        ('Dance', 'Dance'),
        ('Sports', 'Sports'),
    )
    id = models.AutoField(primary_key=True)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=250,blank=False,null=False,verbose_name='branch_course_name')
    coaching = models.ForeignKey(Coaching,on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch,related_name='courses_of',on_delete=models.CASCADE)
    description = models.TextField(blank=True,null=True)
    start_date = models.DateField(editable=True)
    end_date   = models.DateField(editable=True)
    syllabus   = models.FileField(blank=True , null=True)
    fees       = models.DecimalField(blank=False,null=False,max_digits=10,decimal_places=2,default=None)
    currency   = models.CharField(max_length=30,blank=True,null=False,default="INR")
    is_active = models.BooleanField(default=False)
    stream = models.CharField(max_length=250,blank=False,null=False,
                                    verbose_name='coaching_stream',choices=Stream_CHOICES, default=None
                                        )

    def __str__(self):
        return self.name


class CoachingFacultyMember(models.Model):
    id = models.AutoField(primary_key=True)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    coaching = models.ForeignKey(Coaching,related_name="faculty_of",on_delete=models.CASCADE)
    name = models.CharField(max_length=250,blank=False,null=False)
    age  = models.PositiveIntegerField()
    specialization = models.CharField(max_length=250,blank=False,null=False)
    meta_description = models.TextField(blank=True,null=True)
    faculty_image = models.ImageField(upload_to='faculties/',blank=True , null=True)
    faculty_image_link = models.URLField()

    def __str__(self):
        return self.name

class Batch(models.Model):
    id = models.AutoField(primary_key=True)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=250,blank=False,null=False,verbose_name='course_batch_name')
    course = models.ForeignKey(Course,related_name='batches_of',on_delete=models.CASCADE)
    teacher = models.ForeignKey(CoachingFacultyMember,related_name='teaches',on_delete=models.CASCADE,null=False,blank=False)
    start_time = models.CharField(max_length=20, default=None)
    end_time = models.CharField(max_length=20, default=None)
    student_limit = models.PositiveIntegerField(blank=True,null=True)
    students_enrolled = models.PositiveIntegerField(blank=True,null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class CoachingReview(models.Model):
    id = models.AutoField(primary_key=True)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    coaching = models.ForeignKey(Coaching,related_name='reviews_of',on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    description = models.CharField(max_length=250,blank=True,null=True)


class CoachingMetaData(models.Model):
    id = models.AutoField(primary_key=True)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    coaching = models.ForeignKey(Coaching,related_name="metadata_of",on_delete=models.CASCADE)
    contact = models.CharField(blank=False,default=None, max_length=20)
    help_contact =models.CharField(blank=True,default=None, max_length=20)
    owner_name = models.CharField(max_length=250,blank=True,null=True)
    owner_description = models.TextField(blank=True,null=True)
    owner_image = models.ImageField(upload_to='owners/',blank=True , null=True)
    owner_image_link = models.URLField(blank=True,null=True,default=None)
    established_on = models.DateField()

    def __str__(self):
        return self.coaching.name

class BankAccountDetails(models.Model):
    id = models.AutoField(primary_key=True)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    coaching = models.OneToOneField(Coaching, on_delete=models.CASCADE)
    account_no = models.CharField(max_length=30, default=None)
    ifsc_code = models.CharField(max_length=20, default=None)
    bank_name = models.CharField(max_length=50, default=None)
    account_holder = models.CharField(max_length=100, default=None)
    adhar_card = models.FileField(upload_to="adhar_cards/", blank=True , null=True)
    pan_card = models.FileField(upload_to="pan_cards/", blank=True , null=True)
    mobile_no = models.CharField(max_length=20, default=None)

    def __str__(self):
        return self.coaching.name

class Registration(models.Model):
    id = models.AutoField(primary_key=True)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Offer(models.Model):
    id = models.AutoField(primary_key=True)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, default=None)
    description = models.CharField(max_length=200, default=None)
    coaching = models.ForeignKey(Coaching, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class Discount(models.Model):
    id = models.AutoField(primary_key=True)
    coaching = models.ForeignKey(Coaching, on_delete=models.CASCADE)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    disc_code = models.CharField(max_length=20, default=None)
    description = models.CharField(max_length=200, default=None)
    disc_percent = models.IntegerField(default=None)
    
    def __str__(self):
        return self.disc_code

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    review = models.CharField(max_length=200, default=None)
    rating = models.IntegerField(default=None)
    coaching = models.ForeignKey(Coaching, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review_time = models.DateTimeField(auto_now=False)

    def __str__(self):
        return self.coaching.name + " - Review By : " + self.user.username

class Message(models.Model):
    id = models.AutoField(primary_key=True)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    message = models.CharField(max_length=200, default=None)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_receiver")
    timestamp = models.DateTimeField(auto_now=False)

    def __str__(self):
        return str(self.sender) + " - Message : " + self.message



