{% macro badge(estado) -%}
{%- set clases = {'disponible':'verde','habilitado':'verde','devuelto':'verde','prestado':'ambar','activo':'azul','fuera de servicio':'rojo','inhabilitado':'rojo','con retraso':'rojo'} -%}
<span class="etiqueta {{ clases.get(estado, 'gris') }}">{{ estado|capitalize }}</span>
{%- endmacro %}
