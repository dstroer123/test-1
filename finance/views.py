from decimal import Decimal

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from companies.models import Company
from .models import DriverSalary


@login_required
@user_passes_test(lambda user: user.is_staff)
def driver_salary_dashboard(request):
    """Показывает начисления и выплаты водителям."""
    companies = Company.objects.all().order_by("id")
    salaries = DriverSalary.objects.select_related(
        "driver",
        "driver__company",
        "order",
    )

    company_id = request.GET.get("company", "")

    if company_id.isdigit():
        salaries = salaries.filter(
            driver__company_id=int(company_id)
        )
    else:
        company_id = ""

    rows = []
    total_amount = Decimal("0.00")
    total_paid = Decimal("0.00")
    total_remaining = Decimal("0.00")

    for salary in salaries:
        remaining = salary.remaining_amount

        rows.append({
            "salary": salary,
            "company": salary.driver.company,
            "remaining": remaining,
        })

        total_amount += salary.amount
        total_paid += salary.paid_amount
        total_remaining += remaining

    context = {
        "companies": companies,
        "rows": rows,
        "selected_company": company_id,
        "record_count": len(rows),
        "total_amount": total_amount,
        "total_paid": total_paid,
        "total_remaining": total_remaining,
    }

    return render(
        request,
        "finance/driver_salary_dashboard.html",
        context,
    )
