/**
 * PetCare+ Dashboard Charts Engine (Chart.js)
 */

document.addEventListener('DOMContentLoaded', function() {
    // 1. Category Distribution Chart (Doughnut)
    const categoryCanvas = document.getElementById('categoryChart');
    if (categoryCanvas && window.categoryChartData) {
        const ctx = categoryCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: window.categoryChartData.labels,
                datasets: [{
                    data: window.categoryChartData.data,
                    backgroundColor: [
                        '#10b981', // Vaccination
                        '#f59e0b', // Deworming
                        '#0d9488', // Medication
                        '#3b82f6', // Grooming
                        '#ef4444'  // Vet Visit
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { family: 'Inter', size: 12 },
                            padding: 16
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }

    // 2. Status Chart (Bar / Doughnut)
    const statusCanvas = document.getElementById('statusChart');
    if (statusCanvas && window.statusChartData) {
        const ctx = statusCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Completed Care', 'Pending Care', 'Overdue Care'],
                datasets: [{
                    label: 'Tasks',
                    data: [
                        window.statusChartData.completed,
                        window.statusChartData.pending,
                        window.statusChartData.overdue
                    ],
                    backgroundColor: [
                        '#10b981',
                        '#3b82f6',
                        '#ef4444'
                    ],
                    borderRadius: 8,
                    barThickness: 32
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });
    }
});
