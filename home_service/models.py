from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class City(models.Model):
    city = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.city

class Status(models.Model):
    status = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.status

class ID_Card(models.Model):
    card = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.card

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    contact = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=100, null=True)
    image = models.FileField(null=True)

    def __str__(self):
        return self.user.first_name

class Service_Man(models.Model):
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    contact = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=100, null=True)
    doj = models.DateField(null=True)
    dob = models.DateField(null=True)
    id_type = models.CharField(max_length=100, null=True)
    service_name = models.CharField(max_length=100, null=True)
    experience = models.CharField(max_length=100, null=True)
    id_card = models.FileField(null=True)
    image = models.FileField(null=True)
    price=models.IntegerField(default=500)

    def __str__(self):
        return self.user.first_name


class Service_Category(models.Model):
    category = models.CharField(max_length=30, null=True)
    desc = models.CharField(max_length=100, null=True)
    image = models.FileField(null=True)
    total=models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.category

class Service(models.Model):
    categorys = models.ForeignKey(Service_Category,on_delete=models.CASCADE,null=True)
    service = models.ForeignKey(Service_Man, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.category.category

class Contact(models.Model):
    status = models.ForeignKey(Status,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=100, null=True)
    message1 = models.CharField(max_length=200, null=True)
    email = models.EmailField(null=True)
    def __str__(self):
        return self.name

class Total_Man(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.service.user.first_name


class Order(models.Model):
    report_status = models.CharField(max_length=100, null=True)
    status = models.ForeignKey(Status,on_delete=models.CASCADE,null=True)
    service = models.ForeignKey(Service_Man, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    book_date = models.DateField(null=True)
    book_days = models.CharField(max_length=100, null=True)
    book_hours = models.CharField(max_length=100, null=True)
    price=models.IntegerField(null=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True)
    razorpay_order_id = models.CharField(max_length=100, null=True)
    razorpay_signature = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.service.user.first_name+" "+self.customer.user.first_name


from django.db import models
from django.contrib.auth.models import User

class WebsiteReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user who submits the review
    rating = models.PositiveIntegerField(default=1)  # Rating between 1-5
    comment = models.TextField(blank=True, null=True)  # Optional review text
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of the review

    def __str__(self):
        return f"{self.user.username} - {self.rating}⭐"

    @classmethod
    def get_average_rating(cls):
        avg = cls.objects.aggregate(models.Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0  # Get average rating with 1 decimal place

