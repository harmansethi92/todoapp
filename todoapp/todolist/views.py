from django.shortcuts import render,redirect

from .models import TodoList

def index(request):
    todos = TodoList.objects.all()
    if request.method == "POST":
        if "taskAdd" in request.POST:
            title = request.POST["description"]
            date = str(request.POST["date"])
            content = title + " -- " + date + " "
            Todo = TodoList(title=title, content=content, due_date=date)
            Todo.save()
            return redirect("/")
        if "taskDelete" in request.POST:
            checkedlist = request.POST["checkedbox"]
            for todo_id in checkedlist:
                todo = TodoList.objects.get(id=int(todo_id))
                todo.delete()
    return render(request, "index.html", {"todos": todos})
