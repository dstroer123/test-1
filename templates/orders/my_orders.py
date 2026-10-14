<p>
    Расстояние: {{ order.distance_km|default:"Не рассчитано" }} км
</p>

<p>
    Время в пути: {{ order.estimated_time_hours|default:"Не рассчитано" }} ч
</p>

<p>
    Машина:
    {% if order.vehicle %}
        {{ order.vehicle.brand }} {{ order.vehicle.model }}
        ({{ order.vehicle.plate_number }})
    {% else %}
        Пока не назначена
    {% endif %}
</p>