from django.shortcuts import render,redirect, HttpResponseRedirect
from django.views import View
from .models import Customer, Product,Cart, OrderPlaced
from .forms import CustomerRegistration, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.

class ProductView(View):
    def get(self, request):
        totalitem = 0
        Laptop = Product.objects.filter(category = 'L')
        MobilePhone = Product.objects.filter(category = 'P')
        Headphone = Product.objects.filter(category = 'H')
        if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'Shop/home.html', {'Laptop':Laptop, 'MobilePhone':MobilePhone, 'Headphone': Headphone, 'totalitem':totalitem})



class ProductDetailView(View):
  def get(self,request, pk):
    
    product = Product.objects.get(pk=pk)
    
    return render(request, 'Shop/productdetail.html',{'product': product})


class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        return render(request, 'Shop/productdetail.html', {'product':product, 'item_already_in_cart':item_already_in_cart})



@login_required
def add_to_cart(request):
 user = request.user
 product_id = request.GET.get('prod_id')
 product = Product.objects.get(id=product_id)
 Cart(user=user, product=product).save()
 return redirect('/cart')

@login_required
def show_cart(request):
   if request.user.is_authenticated:
      user= request.user
      amount=0.0
      shipping_amount=100
      total_amount = 0.0
      cart_product=[p for p in Cart.objects.all() if p.user==user]
      if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
            totalamount = amount+shipping_amount
        cart = Cart.objects.filter(user=user)
        return render(request, 'Shop/addtocart.html', {'carts':cart, 'amount':amount, 'totalamount':totalamount})
      else:
         return render(request, 'Shop/emptycart.html')



def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity +=1
        c.save()
        amount = 0.0
        shipping_amount = 100.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        data={
            'quantity': c.quantity,
            'amount' : amount,
            'totalamount' : amount + shipping_amount
        }

        return JsonResponse(data)
    

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -=1
        c.save()
        amount = 0.0
        shipping_amount = 100.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        data={
            'quantity': c.quantity,
            'amount' : amount,
            'totalamount' : amount + shipping_amount
        }

        return JsonResponse(data)
    

#Remove cart
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 100.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        data={
            'amount' : amount,
            'totalamount' : amount + shipping_amount
        }

        return JsonResponse(data)


#Search
def search(request):
    if request.method == 'GET':
        query = request.GET.get('quary')
        if query:
            product = Product.objects.filter(title__icontains=query)
            if product:
                return render(request, 'Shop/search.html', {'product': product})
            else:
               return render(request, 'Shop/emptysearch.html')
        else:
           #print('Not availbale in the cart')
           return render(request, 'Shop/emptysearch.html')
           


@login_required
def buy_now(request):
 user = request.user
 product_id= request.GET.get('prod_id')
 product = Product.objects.get(id=product_id)
 Cart(user=user,product=product).save()
 return redirect('/checkout')
 

#Profile
@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'Shop/profile.html', {'form':form, 'active':'btn-primary'})
    
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            division = form.cleaned_data['division']
            district = form.cleaned_data['district']
            thana = form.cleaned_data['thana']
            villorroad = form.cleaned_data['villorroad']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr,name=name, division=division,district=district, thana=thana, villorroad=villorroad, zipcode=zipcode)
            reg.save()
            messages.success(request, 'Congratulations! Profile Updated Successfully')
        return render(request, 'Shop/profile.html', {'form':form, 'active':'btn-primary'})

@login_required
def address(request):
    totalitem = 0
    add = Customer.objects.filter(user = request.user)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'Shop/address.html', {'add':add, 'active':'btn-primary', 'totalitem':totalitem})


@login_required
def orders(request):
 op = OrderPlaced.objects.filter(user=request.user)
 return render(request, 'Shop/orders.html',{'order_placed':op})



def Laptop(request, data =None):
    if data == None:
        Laptop = Product.objects.filter(category = 'L')
    elif data == 'HP' or data == 'Dell':
        Laptop = Product.objects.filter(category='L').filter(brand=data)
    elif data == 'below':
        Laptop = Product.objects.filter(category='L').filter(discounted_price__lt=50000)
    elif data == 'above':
        Laptop = Product.objects.filter(category='L').filter(discounted_price__gt=50000)
    return render(request, 'Shop/Laptop.html', {'Laptop':Laptop})



def MobilePhone(request, data =None):
    if data == None:
        MobilePhone = Product.objects.filter(category = 'P')
    elif data == 'Apple' or data == 'Samsung':
        MobilePhone = Product.objects.filter(category='P').filter(brand=data)
    elif data == 'below':
        MobilePhone = Product.objects.filter(category='P').filter(discounted_price__lt=50000)
    elif data == 'above':
        MobilePhone = Product.objects.filter(category='P').filter(discounted_price__gt=50000)
    return render(request, 'Shop/MobilePhone.html', {'MobilePhone':MobilePhone})





class CustomerRegistrationView(View):
    def get(self,request):
      form = CustomerRegistration()
      return render(request, 'Shop/customerregistration.html', {'form':form})

    def post(self,request):
      form = CustomerRegistration(request.POST)
      if form.is_valid():
         messages.success(request, "Successfully registration done")
         form.save()
      return render(request, 'Shop/customerregistration.html', {'form':form})


@login_required
def checkout(request):
 user = request.user
 add = Customer.objects.filter(user=user)
 cart_items = Cart.objects.filter(user=user)
 amount = 0.0
 shipping_amount = 100.0
 cart_product = [p for p in Cart.objects.all() if p.user == request.user]
 if cart_product:
    for p in cart_product:
        tempamount = (p.quantity * p.product.discounted_price)
        amount += tempamount
    totalamount = amount +shipping_amount
    return render(request, 'Shop/checkout.html', {'add':add, 'totalamount':totalamount,'cart_items':cart_items })
 else:
    return HttpResponseRedirect('/')
 
 


#payment_done
@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')

    if custid:
        try:
            customer = Customer.objects.get(id=custid) 
        except Customer.DoesNotExist:
            return HttpResponse("Invalid customer ID", status=400)

        cart = Cart.objects.filter(user=user)
        for c in cart:
            OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
            c.delete()

        return redirect("orders")
    else:
        return HttpResponse("Please select a customer to process the payment and address.", status=400)
    



#def combo(request):
   #return render (request, 'Shop/combo.html')  

class Combo(View):
    def get(self, request):
        totalitem = 0
        Keyboard = Product.objects.filter(category = 'K')
        if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'Shop/combo.html', {'Keyboard':Keyboard, 'totalitem':totalitem})   