from django.shortcuts import render

def addRevenueOrExpenseView(request):
    return render(request, 'revenuesAndExpenses/AddRevenueOrExpensePage.html')