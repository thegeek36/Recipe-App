from django.shortcuts import render
from .models import* 
from django.db.models import Avg
from django.contrib import messages
from django.contrib.auth import authenticate, login , logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    queryset = Recipe.objects.all()[:4]
    context = {'recipes': queryset}
    return render(request,"index.html",context)

@login_required
def add_recipe(request):
    if request.method == 'POST':
        data = request.POST
        recipe_name = data.get('recipe_name')
        recipe_description = data.get('recipe_description')
        recipe_ingridents = data.get('recipe_ingridents')
        instructions = data.get('instructions')
        cooking_time = data.get('cooking_time')
        recipe_image = request.FILES.get('recipe_image')

        Recipe.objects.create(
            user = request.user,
            recipe_image = recipe_image,
            recipe_name = recipe_name,
            recipe_ingridents = recipe_ingridents ,
            recipe_description = recipe_description,
            instructions = instructions,
            cooking_time = cooking_time,

        )
        return redirect('/addrecipe')
    return render(request,"addrecipe.html")

def viewrecipe(request):
    queryset = Recipe.objects.order_by('-created_at')
    context = {'recipes': queryset}
    return render(request,"view.html",context)

@login_required
def delete_recipe(request,id):
    queryset = Recipe.objects.get(id=id)
    queryset.delete() 
    return redirect('/viewrecipe')

@login_required  
def update_recipe(request,id):
    queryset = Recipe.objects.get(id=id)
    if request.method == 'POST':
        data = request.POST
        recipe_name = data.get('recipe_name')
        recipe_description = data.get('recipe_description')
        recipe_ingridents = data.get('recipe_ingridents')
        instructions = data.get('instructions')
        cooking_time = data.get('cooking_time')
        recipe_image = request.FILES.get('recipe_image')  

        queryset.recipe_name = recipe_name
        queryset.recipe_description = recipe_description
        queryset.recipe_ingridents = recipe_ingridents
        queryset.instructions = instructions
        queryset.cooking_time  = cooking_time

        if recipe_image:
            queryset.recipe_image = recipe_image

        queryset.save()
        return redirect('/viewrecipe/')
    context = {'recipe':queryset}
    return render(request,"update_recipe.html",context)


def recipe_detail(request,id):
    queryset = Recipe.objects.get(id=id)
    ingredients = queryset.recipe_ingridents.split('\n')
    instructions = queryset.instructions.split('.')

    if request.method == 'POST':
        if request.user.is_authenticated:
            # Rating
            score = request.POST.get('score')
            existing_rating = Rating.objects.filter(user=request.user, recipe_name=queryset).first()
            if score is not None:
                if existing_rating is not None:
                    # Update the existing rating
                    score = int(score)
                    existing_rating.score = score
                    existing_rating.save()
                else:
                    score = int(score)
                    rating = Rating(user=request.user, recipe_name=queryset, score=score)
                    rating.save()
            # Comment
            content = request.POST.get('content')
            if content:
                comment = Comment(user=request.user, recipe_name=queryset, content=content)
                comment.save()
        else:
            messages.error(request,'Please Login to Rate or Comment.')
        return redirect("recipe_detail",id=id)
    
    comments = Comment.objects.filter(recipe_name=queryset).order_by('-created_at')
    average_rating = Rating.objects.filter(recipe_name=queryset).aggregate(Avg('score'))['score__avg']
    context = {'recipes': queryset,
               'ingredients':ingredients,
               'instructions':instructions,
               'average_rating':average_rating,
               'comments': comments}
    
    return render(request,"recipedetail.html",context)


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not User.objects.filter(username = username).exists():
            messages.error(request, 'Invalid username')
            return redirect('/login_page')
        
        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, 'Invalid Password')
            return redirect('/login_page/')
        else:
            login(request,user)
            return redirect('/viewrecipe/')
        
    return render(request,"login_page.html")

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.filter(username=username)
        if user.exists():
            messages.info(request, 'Username already exists')
            return redirect('/register')
        user = User.objects.create(first_name=first_name,
                                   last_name=last_name,
                                   email=email,
                                   username=username)
        user.set_password(password)
        user.save()
        messages.success(request,'Account Created Successfully')
        return redirect('/register/')
    
    return render(request,"register.html")

@login_required
def log_out(request):
    logout(request)  # Logs out the user
    return redirect('/login_page')  # Redirects to the desired URL after logout (replace 'home' with the appropriate URL name)

def search(request):
    queryset = Recipe.objects.order_by('-created_at')
    if request.GET.get('search'):
        queryset = queryset.filter(recipe_name__icontains=request.GET.get('search'))
    context = {'recipes': queryset}
    return render(request,"search.html",context)

@login_required
def profile(request,id):
    try:
        queryset = User.objects.get(id=id)
        user_recipes = Recipe.objects.filter(user=queryset)
        recipe_count = user_recipes.count()
        recipe = Recipe.objects.filter(user=queryset)
        userdetails = UserProfile.objects.get(user=queryset)
        context = {'user': queryset,'recipes': recipe,'userdetails':userdetails,'recipe_count':recipe_count}
        return render(request,"profile.html",context)
    except UserProfile.DoesNotExist:
        return redirect("/create_profile/")
    
def create_profile(request):
    queryset = User.objects.get(username = request.user.username)
    if request.method == 'POST':
        bio = request.POST.get('bio')
        dob = request.POST.get('dob')
        profile_pic = request.FILES.get('profile_pic')
        profile = UserProfile.objects.create(user = queryset,
                                        profile_pic = profile_pic,
                                         bio = bio,
                                         dob = dob)
        messages.success(request,'Profile Created Successfully')
        profile.save()
        return redirect('profile',id=request.user.id)
    return render(request,"create_prrofile.html")

def update_profile(request,id):
    queryset = UserProfile.objects.get(id=id)
    if request.method == 'POST':
        data = request.POST
        bio = data.get('bio')
        dob = data.get('dob')
        profile_pic = request.FILES.get('profile_pic')  
        queryset.dob = dob
        queryset.bio = bio
        if profile_pic:
            queryset.profile_pic = profile_pic
        queryset.save()
        print("User Id",request.user.id)
        return redirect('profile',id=request.user.id)
    context = {'userprofile':queryset}
    return render(request,"updateprofile.html",context)
# Create your views here.
