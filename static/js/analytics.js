// Analytics Charts using Chart.js

document.addEventListener('DOMContentLoaded', async () => {
    const trendCanvas = document.getElementById('trendChart');
    const priorityCanvas = document.getElementById('priorityChart');
    const habitCanvas = document.getElementById('habitChart');

    if (!trendCanvas && !priorityCanvas && !habitCanvas) return;

    try {
        const res = await fetch('/api/analytics-data/');
        if (!res.ok) return;
        const data = await res.json();

        const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
        const textColor = isDark ? '#cbd5e1' : '#475569';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)';

        // 1. Productivity Trend Chart
        if (trendCanvas && data.trend) {
            new Chart(trendCanvas, {
                type: 'line',
                data: {
                    labels: data.trend.labels,
                    datasets: [
                        {
                            label: 'Completed Tasks',
                            data: data.trend.completed,
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            fill: true,
                            tension: 0.35,
                            pointRadius: 4,
                            pointBackgroundColor: '#10b981',
                        },
                        {
                            label: 'Created Tasks',
                            data: data.trend.created,
                            borderColor: '#6366f1',
                            backgroundColor: 'transparent',
                            borderDash: [5, 5],
                            tension: 0.35,
                            pointRadius: 3,
                            pointBackgroundColor: '#6366f1',
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: textColor, font: { family: 'Inter' } }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: textColor },
                            grid: { color: gridColor }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0,
                                color: textColor
                            },
                            grid: { color: gridColor }
                        }
                    }
                }
            });
        }

        // 2. Priority Doughnut Chart
        if (priorityCanvas && data.priority) {
            new Chart(priorityCanvas, {
                type: 'doughnut',
                data: {
                    labels: data.priority.labels,
                    datasets: [{
                        data: data.priority.counts,
                        backgroundColor: [
                            '#94a3b8', // Low - Gray
                            '#38bdf8', // Medium - Info Blue
                            '#fbbf24', // High - Warning Amber
                            '#ef4444', // Urgent - Red
                        ],
                        borderWidth: 2,
                        borderColor: isDark ? '#111827' : '#ffffff',
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: textColor, font: { family: 'Inter' } }
                        }
                    },
                    cutout: '68%'
                }
            });
        }

        // 3. Habit Consistency Bar Chart
        if (habitCanvas && data.habits && data.habits.names.length > 0) {
            new Chart(habitCanvas, {
                type: 'bar',
                data: {
                    labels: data.habits.names,
                    datasets: [{
                        label: '30-Day Completion Rate (%)',
                        data: data.habits.rates,
                        backgroundColor: data.habits.colors,
                        borderRadius: 6,
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            min: 0,
                            max: 100,
                            ticks: {
                                callback: (v) => v + '%',
                                color: textColor
                            },
                            grid: { color: gridColor }
                        },
                        y: {
                            ticks: { color: textColor },
                            grid: { display: false }
                        }
                    }
                }
            });
        }
    } catch (e) {
        console.error('Error loading analytics:', e);
    }
});
