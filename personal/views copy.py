from django.shortcuts import render, get_object_or_404, redirect
from personal.models import Matrix,MatrixGroup
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages



# Create your views here.

def index(request):
    
    # If user is authenticated, show views
    if request.user.is_authenticated:
        # Get URL parameters
        category = request.GET.get('category','0') # Category to filter for in the view (if != 0)
        dimensions = request.GET.get('dimensions','0') # Dimension to set in the view (if > 0)
        matrix_input = request.GET.get('matrix_input','0') # Whether to show or not the matrix table
        
        # Get list of matrices to show in view, based on parameters above
        if int(dimensions) < 1:
            # If to show all dimensions and categories, get all matrices
            if category == '0':
                matrix_list = Matrix.objects.all()
            # If to show all dimensions but a specific category, get all matrices in that category
            else:
                matrix_list = MatrixGroup.objects.get(category_name=category).matrices.all()
        else:
            # If to show a specific dimension and all categories, get all matrices with a specific dimension
            if category == '0':
                matrix_list = Matrix.objects.filter(dimension=int(dimensions))
            # If to show a specific dimension and category, get all matrices in that category with that specific dimension
            else:
                matrix_list = MatrixGroup.objects.get(category_name=category).matrices.all().filter(dimension=int(dimensions))
        
        # Get list of all categories to show in view
        category_list = MatrixGroup.objects.exclude(category_name="all")


        
        # Actions based on form request (when user submits a form by clicking one of the buttons)
        if request.method == 'POST':
            
            # If request is to save the matrix
            if 'Save' in request.POST:
                # Get matrix attributes: name, value, dimension and categories that it's a member of
                name = request.POST.get('namefield')
                value = request.POST.get('input_matrix')
                categories = request.POST.get('selected_categories'); categories = categories.split(",")
                dim = request.POST.get('matrix_dimensions')

                # Try to create a new matrix
                try:
                    new_matrix = Matrix.objects.create(matrix_name=name,matrix_value=value, dimension = int(dim))
                    
                    # For each category in the list of categories the matrix is to be a member of, add the matrix to that category's matrices attribute
                    for cat in categories:
                        try:
                            cat_group = MatrixGroup.objects.get(category_name=cat)
                            cat_group.matrices.add(new_matrix)
                            cat_group.save()
                        except:
                            pass
                        
                # If matrix already exists, replace existing matrix
                except:                
                    matrix_instance = Matrix.objects.get(matrix_name=name)
                    matrix_instance.matrix_value = value
                    matrix_instance.dimension = int(dim)
                    matrix_instance.save() # Save modified matrix
                    
                    # For each category in the list of categories the matrix is to be a member of, add the matrix to that category's matrices attribute
                    for cat in categories:
                        try:
                            cat_group = MatrixGroup.objects.get(category_name=cat)
                            cat_group.matrices.add(matrix_instance)
                            cat_group.save()
                        except:
                            pass
                        
                    transaction.commit() # Commit transaction to ensure modified matrix is indeed updated


                return render(request,
                    'personal/home.html', {'matrix': value, # Matrix value to load (ensure view remains the same)
                                           'matrix_list': matrix_list, 
                                           'dimensions': -1, # Dimensions to show
                                           'matrix_input': matrix_input, # Whether to show matrix table or not
                                           'category_list':category_list # List of categories to show in view
                                          }
                )

            
            # If request is to load a matrix
            elif 'Load' in request.POST:
                name = request.POST.get('selected_matrix_name')
                matrix_instance = Matrix.objects.get(matrix_name=name)

                return render(request, 'personal/home.html', {'matrix': matrix_instance.matrix_value,
                                                              'matrix_list': matrix_list,
                                                              'dimensions': -1,
                                                              'matrix_input': matrix_input,
                                                              'category_list':category_list
                                                             }
                             )
            
            
            # If request is to create a new category
            elif 'CreateCategory' in request.POST:
                new_category = request.POST.get('categoryfield')
                MatrixGroup.objects.create(category_name=new_category)
                value = request.POST.get('input_matrix') # Get current matrix being drawn, so view can remain the same after submitting request
                
                return render(request,
                    'personal/home.html', {'matrix': value,
                                           'matrix_list':matrix_list,
                                           'dimensions': -1,
                                           'matrix_input': matrix_input,
                                           'category_list':category_list
                                          }
                )

        # Otherwise, just load the default view
        else:
            return render(request, 'personal/home.html',
                          {'matrix': '[[0,0,0],[0,0,0],[0,0,0]]', # matrix placeholder
                           'matrix_list': matrix_list,
                           'dimensions': dimensions,
                           'matrix_input': matrix_input,
                           'category_list':category_list
                          }
                         )

    # If user is not authenticated, redirect to login page
    else:
        return redirect("personal:login")
    
    
    
# Registration view
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New account created: {username}")
            login(request, user)
            return redirect("personal:index")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

            return render(request = request,
                          template_name = "personal/register.html",
                          context={"form":form})

    form = UserCreationForm
    return render(request = request,
                  template_name = "personal/register.html",
                  context={"form":form})


# Logout view
def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("personal:login")




# Login view
def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect('/')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request = request,
                    template_name = "personal/login.html",
                    context={"form":form})