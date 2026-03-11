SELECT
city,
AVG(temperature) as avg_temp
FROM weather_data
GROUP BY city