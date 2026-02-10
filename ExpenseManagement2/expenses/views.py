from unicodedata import category

import form
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from expenses.forms import ExpenseForm
from expenses.models import Expense
import datetime



@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect("expense_list")
    else:
        form = ExpenseForm()

    return render(request, "expenses/add_expense.html", {"form": form})

@login_required
def update_expense(request, id):
    expense = get_object_or_404(Expense, id = id, user = request.user)
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect("expense_list")
    else:
        form = ExpenseForm(instance=expense)
        return render(request, "expenses/add_expense.html", {"form": form})

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by("-date")
    # category = request.GET.get("category")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    # if category:
    #     expenses = expenses.filter(category=category)
    if start_date and end_date:
        expenses = expenses.filter(date__range=[start_date, end_date])

    total = expenses.aggregate(Sum("amount"))["amount__sum"] or 0
    context = {"expenses": expenses, "total": total, "start_date": start_date, "end_date": end_date}
    return render(request, "expenses/expense_list.html", context)

@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    if request.method == "POST":
        expense.delete()
        return redirect("expense_list")
    return render(request, "expenses/delete_confirm.html", {"expense": expense})
