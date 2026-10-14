from decimal import Decimal

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from companies.models import Company
from finance.models import FinanceRecord


@login_required
@user_passes_test(lambda user: user.is_staff)
def finance_dashboard(request):
    """Показывает финансовые показатели транспортных компаний."""
    companies = Company.objects.all().order_by("id")
    records = FinanceRecord.objects.select_related(
        "order",
        "order__company",
        "order__vehicle",
    )

    company_id = request.GET.get("company", "")

    if company_id.isdigit():
        records = records.filter(order__company_id=int(company_id))
    else:
        company_id = ""

    rows = []
    total_revenue = Decimal("0.00")
    total_fuel = Decimal("0.00")
    total_additional = Decimal("0.00")
    total_salary = Decimal("0.00")
    total_expenses = Decimal("0.00")
    total_profit = Decimal("0.00")

    for record in records:
        revenue = record.calculate_revenue()
        fuel_cost = record.calculate_fuel_cost()
        additional = record.additional_expenses
        salary = record.driver_salary
        expenses = record.calculate_total_expenses()
        profit = record.calculate_profit()

        rows.append({
            "record": record,
            "company": record.order.company,
            "revenue": revenue,
            "fuel_cost": fuel_cost,
            "additional": additional,
            "salary": salary,
            "expenses": expenses,
            "profit": profit,
        })

        total_revenue += revenue
        total_fuel += fuel_cost
        total_additional += additional
        total_salary += salary
        total_expenses += expenses
        total_profit += profit

    context = {
        "companies": companies,
        "rows": rows,
        "selected_company": company_id,
        "record_count": len(rows),
        "total_revenue": total_revenue,
        "total_fuel": total_fuel,
        "total_additional": total_additional,
        "total_salary": total_salary,
        "total_expenses": total_expenses,
        "total_profit": total_profit,
    }

    return render(
        request,
        "analytics/finance_dashboard.html",
        context,
    )
