from django.db import models
from django.utils.text import slugify


# Create your models here.
CATEGORY_CHOICES = [
    ('laptop', 'Laptop'),
    ('desktop', 'Desktop'),
    ('tablet', 'Tablet'),
    ('smartphone', 'Smartphone'),
    ('accessory', 'Accessory'),
]

OS_CHOICES = [
    ('windows', 'Windows'),
    ('macos', 'macOS'),
    ('linux', 'Linux'),
    ('android', 'Android'),
    ('chromeos', 'ChromeOS'),
    ('ios', 'iOS'),
    ('other', 'Other'),
]

class Image(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, help_text="Associated product")
    image = models.ImageField(upload_to='products/', help_text="Image file")
    alt_text = models.CharField(max_length=200, blank=True, help_text="Alternative text for the image")
    is_main = models.BooleanField(default=False, help_text="Is this the main image?")
    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'
        ordering = ['-is_main','id']
    
    def __str__(self):
        return f"Image for {self.product.name} - {self.alt_text or 'No Alt Text'}"

class Product(models.Model):
    # Core Details
    name = models.CharField(max_length=300, help_text="Full product name (e.g., 'Dell XPS 13 2021')")
    brand = models.CharField(max_length=200, help_text="Brand name (e.g., 'Dell', 'Apple')")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='laptop', help_text="Product category")
    # Pricing & Description
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in rupees (e.g., 99999.99)")
    short_description = models.TextField(help_text="A concise summary for the list view")
    long_description = models.TextField(blank=True, null= True, help_text="Detailed product description")
    # Specification Details ( for details page)
    processor = models.CharField(max_length=200, blank=True, help_text="Processor details (e.g., 'Intel i7-1165G7')")
    ram_gb = models.CharField(max_length=100, blank=True, help_text="RAM size (e.g., '16GB')")
    storage = models.CharField(max_length=200, blank=True, help_text="Storage details (e.g., '512GB SSD')")
    display = models.CharField(max_length=200, blank=True, help_text="Display details (e.g., '13.3 inch FHD')")
    os = models.CharField(max_length=50, choices=OS_CHOICES, default='windows', help_text="Operating System")
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Weight in kilograms (e.g., 1.2)")
    # Images (Using placeholder URL fields for simplicity)
    main_image = models.ImageField(upload_to='products/', help_text="Main product image URL")
    # Additional images can be added as needed
    images = models.ManyToManyField(Image, blank=True, related_name='products', help_text="Additional product images")
    
    slug = models.SlugField(max_length=200, unique=True, blank= True, help_text="Unique URL-friendly identifier (e.g., 'dell-xps-13-2021')")
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

class Contacts(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact : {self.name} - {self.subject}"
    
class Order(models.Model):
    # Customer Information
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    # Shipping Address
    street_address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    # Order Details
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"
    
from django.contrib import admin

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'os')
    search_fields = ('name', 'brand', 'category', 'os')
    list_filter = ('category', 'os', 'brand')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'submitted_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('submitted_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'product', 'total_price', 'order_date')
    search_fields = ('full_name', 'email', 'product__name')
    list_filter = ('order_date', 'product__category')

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'alt_text', 'is_main')
    search_fields = ('product__name', 'alt_text')
    list_filter = ('is_main',)
    
