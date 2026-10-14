
{% extends "base.html" %}

{% block content %}
<div class="container py-4">
    <h1 class="mb-4">Финансовая аналитика</h1>

    <form method="get" class="card card-body mb-4">
        <label for="company" class="form-label">
            Транспортная компания
        </label>

        <div class="d-flex gap-2">
            <select
                name="company"
                id="company"
                class="form-select"
            >
                <option value="">Все компании</option>

                {% for company in companies %}
                    <option
                        value="{{ company.id }}"
                        {% if selected_company == company.id|stringformat:"s" %}
                            selected
                        {% endif %}
                    >
                        {{ company }}
                    </option>
                {% endfor %}
            </select>

            <button class="btn btn-primary" type="submit">
                Применить
            </button>

            <a
                href="{% url 'finance_dashboard' %}"
                class="btn btn-outline-secondary"
            >
                Сбросить
            </a>
        </div>
    </form>

    <div class="row g-3 mb-4">
        <div class="col-md-4">
            <div class="card h-100">
                <div class="card-body">
                    <h6 class="text-muted">Выручка</h6>
                    <h3>{{ total_revenue|floatformat:2 }} ₸</h3>
                </div>
            </div>
        </div>

        <div class="col-md-4">
            <div class="card h-100">
                <div class="card-body">
                    <h6 class="text-muted">Общие расходы</h6>
                    <h3>{{ total_expenses|floatformat:2 }} ₸</h3>
                </div>
            </div>
        </div>

        <div class="col-md-4">
            <div class="card h-100">
                <div class="card-body">
                    <h6 class="text-muted">Прибыль</h6>
                    <h3>{{ total_profit|floatformat:2 }} ₸</h3>
                </div>
            </div>
        </div>
    </div>

    <div class="card mb-4">
        <div class="card-body">
            <h5>Структура расходов</h5>
            <p>
                Топливо:
                <strong>{{ total_fuel|floatformat:2 }} ₸</strong>
            </p>
            <p>
                Дополнительные расходы:
                <strong>{{ total_additional|floatformat:2 }} ₸</strong>
            </p>
            <p class="mb-0">
                Оплата водителям:
                <strong>{{ total_salary|floatformat:2 }} ₸</strong>
            </p>
        </div>
    </div>

    <h4 class="mb-3">
        Финансовые записи
        <span class="badge text-bg-secondary">
            {{ record_count }}
        </span>
    </h4>

    <div class="table-responsive">
        <table class="table table-striped table-bordered align-middle">
            <thead class="table-dark">
                <tr>
                    <th>Заказ</th>
                    <th>Компания</th>
                    <th>Маршрут</th>
                    <th>Выручка</th>
                    <th>Топливо</th>
                    <th>Зарплата</th>
                    <th>Расходы</th>
                    <th>Прибыль</th>
                </tr>
            </thead>

            <tbody>
                {% for row in rows %}
                    <tr>
                        <td>#{{ row.record.order_id }}</td>
                        <td>{{ row.company }}</td>
                        <td>
                            {{ row.record.order.origin }}
                            →
                            {{ row.record.order.destination }}
                        </td>
                        <td>{{ row.revenue|floatformat:2 }} ₸</td>
                        <td>{{ row.fuel_cost|floatformat:2 }} ₸</td>
                        <td>{{ row.salary|floatformat:2 }} ₸</td>
                        <td>{{ row.expenses|floatformat:2 }} ₸</td>
                        <td>
                            <strong>{{ row.profit|floatformat:2 }} ₸</strong>
                        </td>
                    </tr>
                {% empty %}
                    <tr>
                        <td colspan="8" class="text-center py-4">
                            Финансовых записей пока нет.
                        </td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
