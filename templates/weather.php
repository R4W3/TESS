<?php
echo "<div hx-get="/weather_call" hx-trigger="every 120s delay:1s" hx-swap="outerHTML" id="ar_weather">{{ l.7 }}&nbsp;{{ temp }}° C.</div>