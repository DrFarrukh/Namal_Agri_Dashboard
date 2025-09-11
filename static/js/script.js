document.addEventListener('DOMContentLoaded', () => {
    const charts = {};

    const chartConfigs = {
        'temp-humidity-chart': {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    { label: 'Air Temperature (°C)', data: [], borderColor: 'crimson', fill: false },
                    { label: 'Air Humidity (%)', data: [], borderColor: 'skyblue', fill: false },
                    { label: 'Soil Temperature (°C)', data: [], borderColor: 'red', fill: false },
                    { label: 'Soil Humidity (%)', data: [], borderColor: 'purple', fill: false },
                ]
            },
            options: { responsive: true, plugins: { title: { display: true, text: 'Temperature & Humidity' } } }
        },
        'soil-nutrients-chart': {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    { label: 'Nitrogen (mg/kg)', data: [], borderColor: 'green', fill: false },
                    { label: 'Phosphorus (mg/kg)', data: [], borderColor: 'orange', fill: false },
                    { label: 'Potassium (mg/kg)', data: [], borderColor: 'brown', fill: false },
                ]
            },
            options: { responsive: true, plugins: { title: { display: true, text: 'Soil Nutrients' } } }
        },
        'soil-moisture-chart': {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    { label: 'Soil Moisture (%)', data: [], borderColor: 'blue', fill: false },
                ]
            },
            options: { responsive: true, plugins: { title: { display: true, text: 'Soil Moisture' } } }
        },
        'soil-ph-chart': {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    { label: 'Soil pH', data: [], borderColor: 'darkgreen', fill: false },
                ]
            },
            options: { responsive: true, plugins: { title: { display: true, text: 'Soil pH' } } }
        }
    };

    function createChart(id, config) {
        const ctx = document.getElementById(id).getContext('2d');
        charts[id] = new Chart(ctx, config);
    }

    function updateLatestData(latest) {
        const container = document.getElementById('latest-data');
        container.innerHTML = '';
        const parameters = [
            'soil_moisture', 'soil_nitrogen', 'soil_phosphorus', 'soil_potassium',
            'soil_temperature', 'soil_humidity', 'soil_ph', 'air_temperature', 'air_humidity'
        ];
        parameters.forEach(param => {
            const card = document.createElement('div');
            card.className = 'sensor-card';
            card.innerHTML = `<h3>${param.replace(/_/g, ' ')}</h3><p class="value">${latest[param]}</p>`;
            container.appendChild(card);
        });
    }

    function updateCharts(data) {
        const labels = data.map(d => new Date(d.timestamp * 1000).toLocaleTimeString());

        Object.keys(charts).forEach(chartId => {
            const chart = charts[chartId];
            chart.data.labels = labels;
            chart.data.datasets.forEach(dataset => {
                const param = dataset.label.split(' ')[0].toLowerCase() + '_' + dataset.label.split(' ')[1].toLowerCase().replace('(%', '').replace(')','').replace('(°c)','');
                dataset.data = data.map(d => d[param]);
            });
            chart.update();
        });
    }

    async function fetchData() {
        try {
            const response = await fetch('/data');
            const data = await response.json();
            if (data && data.length > 0) {
                const latest = data[data.length - 1];
                updateLatestData(latest);
                updateCharts(data);
            }
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    // Initial setup
    Object.keys(chartConfigs).forEach(id => createChart(id, chartConfigs[id]));
    fetchData();
    setInterval(fetchData, 5000); // Refresh every 5 seconds
});
