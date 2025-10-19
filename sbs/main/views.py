from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Q
from .models import Product, Order
from .forms import ContactForm, CheckoutForm
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string

# def seed_initial_data():
#     """Seeds the database with mock data if it's empty."""
#     if Product.objects.count() == 0:
#         Product.objects.bulk_create([
#             Product(
#                 name="Dell XPS 13 (2024 Model)", 
#                 brand="dell", 
#                 category="laptop", 
#                 price=95000.00,
#                 short_description="The pinnacle of ultra-portable computing. Features the latest Intel Core i7, stunning edge-to-edge OLED display, and all-day battery life.",
#                 long_description="A premium device with a machined aluminum body, exceptional build quality, and a fantastic keyboard. Ideal for executives and students who value portability and power. Includes Windows Hello face recognition and a Thunderbolt 4 port.",
#                 processor="14th Gen Intel Core i7 (Latest)",
#                 ram_gb=16, 
#                 storage="512GB NVMe SSD", 
#                 display='13.4" OLED InfinityEdge (500-nit)',
#                 os="windows", 
#                 weight_kg=1.17
#             ),
#             Product(
#                 name="MacBook Pro 14 (M3 Max)", 
#                 brand="apple", 
#                 category="laptop", 
#                 price=215000.00,
#                 short_description="Unrivaled performance for professionals. M3 Max chip, 36GB RAM, and ProMotion display.",
#                 long_description="The most powerful laptop Apple has ever made. Designed for video editors, 3D artists, and developers. Features three Thunderbolt 4 ports, HDMI, and an SDXC card slot. Silent operation even under heavy load.",
#                 processor="Apple M3 Max (16-core CPU)",
#                 ram_gb=36, 
#                 storage="1TB NVMe SSD", 
#                 display='14.2" Liquid Retina XDR',
#                 os="macos", 
#                 weight_kg=1.6
#             ),
#             Product(
#                 name="HP Envy Desktop TE02", 
#                 brand="hp", 
#                 category="desktop", 
#                 price=75000.00,
#                 short_description="Powerful tower PC for creators and gamers. 13th Gen i5 and RTX 4060.",
#                 long_description="A versatile desktop that handles both professional creative suites and modern gaming titles with ease. Tool-less entry design for easy upgrades. Comes with a powerful 600W power supply.",
#                 processor="13th Gen Intel Core i5",
#                 ram_gb=32, 
#                 storage="1TB SSD + 2TB HDD", 
#                 display='N/A',
#                 os="windows", 
#                 weight_kg=6.5
#             ),
#             Product(
#                 name="Wireless Mechanical Keyboard", 
#                 brand="logitech", 
#                 category="accessory", 
#                 price=8500.00,
#                 short_description="High-performance keyboard with tactile switches and long battery life.",
#                 long_description="Connects via Bluetooth or 2.4GHz wireless dongle. Features customizable RGB lighting and PBT keycaps for durability. Available in linear, tactile, and clicky switch options.",
#                 processor="N/A",
#                 ram_gb=0, 
#                 storage="N/A", 
#                 display='N/A',
#                 os="none", 
#                 weight_kg=0.8
#             ),
#         ], ignore_conflicts=True)

def device_list(request):
    """
    Handles the main shop page with filtering logic (index.html).
    If no devices are found after filtering, it falls back to showing all devices 
    in the selected categories (or all devices if no categories were selected).
    """
    # seed_initial_data() # Ensure some data exists for demonstration

    devices = Product.objects.all()
    q_filters = Q()
    fallback_message = None
    
    # ----------------------------------------------------
    # 1. Capture ALL Filters
    # ----------------------------------------------------

    # Category Filter
    selected_categories = request.GET.getlist('category')
    if selected_categories:
        q_filters &= Q(category__in=selected_categories)

    # Brand Filter
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        q_filters &= Q(brand__in=selected_brands)

    # OS Filter
    selected_os = request.GET.getlist('os')
    if selected_os:
        q_filters &= Q(os__in=selected_os)

    # RAM Filter
    current_min_ram = request.GET.get('ram', 'all')
    try:
        min_ram_gb = int(current_min_ram)
        q_filters &= Q(ram_gb__gte=min_ram_gb)
    except ValueError:
        pass 

    # Price Filter
    current_min_price = request.GET.get('min_price', '10000')
    try:
        min_price = float(current_min_ram)
        q_filters &= Q(price__gte=min_price)
    except ValueError:
        pass

    # ----------------------------------------------------
    # 2. Apply Filters and Check for Results
    # ----------------------------------------------------
    devices = devices.filter(q_filters)

    # ----------------------------------------------------
    # 3. Fallback Logic
    # ----------------------------------------------------
    if not devices:        
        fallback_q_filters = Q()
        
        if selected_categories:
            # Fallback 1: Show all items in the selected categories, ignoring all other criteria
            fallback_q_filters &= Q(category__in=selected_categories)
            devices = Product.objects.filter(fallback_q_filters)
            
            if devices:
                fallback_message = f"No results found for your filters. Showing all products in the selected categories: {', '.join(selected_categories).upper()}."
            
        if not devices:
            devices = Product.objects.all()
            fallback_message = "No products matched your exact search criteria. Showing all products available in the store."


    context = {
        'devices': devices,
        'fallback_message': fallback_message,
        'selected_categories': selected_categories,
        'selected_brands': selected_brands,
        'selected_os': selected_os,
        'current_min_ram': current_min_ram,
        'current_min_price': current_min_price,
    }
    return render(request, 'main/index.html', context)

def device_detail(request, slug):
    """View to display detailed information about a specific product."""
    # seed_initial_data()
    product = get_object_or_404(Product, slug=slug)

    image_urls = []

    if product.main_image:
        image_urls.append(product.main_image.url)

    additional_images = product.images.all()
    for img in additional_images:
        if img.image and img.image.url not in image_urls:
            image_urls.append(img.image.url)

    context = {
        'product': product,
        'image_urls': image_urls,
    }
    return render(request, 'main/detail.html', context)

def checkout(request, slug):
    """View to handle the checkout process for a product."""
    # seed_initial_data()
    product = get_object_or_404(Product, slug=slug)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone_number=form.cleaned_data['phone_number'],
                street_address=form.cleaned_data['street_address'],
                city=form.cleaned_data['city'],
                pincode=form.cleaned_data['pincode'],
                product=product,
                total_price=product.price,
            )
            messages.success(request, f'Your order for {product.name} has been placed successfully! We will contact you soon.')
            # Sending emails
            try:
                # Email to Customer
                text_content = f"Order Request for {product.name} has been placed successfully. Order ID : {order.id}"
                html_content = render_to_string("main/customer_order_email.html", {
                    'customer_name': order.full_name,
                    'product_name': product.name, 
                    'price': f"{product.price:,.2f}",
                    'order_id': order.id,
                    'street_address': order.street_address,
                    'city': order.city,
                    'pincode': order.pincode,
                    'phone_number': order.phone_number,
                    'email': order.email,
                })
                msg = EmailMultiAlternatives(
                    "Order Confirmation - SBS Electronics",
                    text_content,
                    settings.EMAIL_HOST_USER,
                    [order.email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                # Email to Store Owner
                text_content = f"New Order Placed: {product.name} (Order ID : {order.id})"
                html_content = render_to_string("main/owner_order_email.html", {
                    'order_id': order.id,
                    'product_name': product.name, 
                    'price': f"{product.price:,.2f}",
                    'customer_name': order.full_name,
                    'customer_email': order.email,
                    'customer_phone': order.phone_number,
                    'street_address': order.street_address,
                    'city': order.city,
                    'pincode': order.pincode,
                    'order_date': order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
                })
                msg = EmailMultiAlternatives(
                    f"New Order Placed - Order ID: {order.id}",
                    text_content,
                    settings.EMAIL_HOST_USER,
                    [settings.DEFAULT_FROM_EMAIL, settings.EMAIL_HOST_USER],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except Exception as e:
                print(e)
                messages.error(request, 'There was an issue sending the confirmation email. Please contact support.')

            return redirect('main:device_list')  
    else:
        form = CheckoutForm()

    context = {
        'product': product,
        'form': form,
    }
    return render(request, 'main/checkout.html', context)

def about(request):
    """View to display the About page."""
    return render(request, 'main/about.html')

def contact(request):
    """View to handle the Contact Us page."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()

            # Email to the Owner
            text_content = "New Contact Form Submission"
            html_content = render_to_string("main/contact_email.html", {
                'name' : form.cleaned_data['name'],
                'email' : form.cleaned_data['email'],
                'subject' : form.cleaned_data['subject'],
                'message' : form.cleaned_data['message'],
            })
            msg = EmailMultiAlternatives(
                "New Contact Form Submission - SBS Electronics",
                text_content,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],  # Send to store owner's email
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            messages.success(request, 'Thank you for reaching out to us! We will get back to you shortly.')
            return redirect('main:contact')
    else:
        form = ContactForm()

    context = {
        'form': form,
    }
    return render(request, 'main/contact.html', context)           
    

