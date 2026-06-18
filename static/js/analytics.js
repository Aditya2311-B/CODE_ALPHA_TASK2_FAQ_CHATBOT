// Read the color theme to customize Chart.js fonts and lines
const isDarkMode = document.documentElement.classList.contains('dark');
const chartTextColor = isDarkMode ? '#94a3b8' : '#64748b'; // slate-400 vs slate-500
const chartGridColor = isDarkMode ? 'rgba(51, 65, 85, 0.3)' : 'rgba(226, 232, 240, 0.8)'; // slate-700 vs slate-200

// Initialize charts if data exists
document.addEventListener("DOMContentLoaded", () => {
    initDailyChatsChart();
    initTopicsChart();
    initMostAskedChart();
});

/**
 * Line Chart: Chats / Queries Per Day (Last 7 Days)
 */
function initDailyChatsChart() {
    const ctx = document.getElementById('dailyChatsChart');
    if (!ctx) return;
    
    // Sort and extract labels and values
    const data = statsData.daily_chats || [];
    const labels = data.map(item => {
        // Format YYYY-MM-DD to Month Day (e.g. Jun 15)
        const d = new Date(item.date);
        return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
    });
    const counts = data.map(item => item.count);

    // Create a smooth brand gradient fill
    const canvasCtx = ctx.getContext('2d');
    const gradient = canvasCtx.createLinearGradient(0, 0, 0, 200);
    gradient.addColorStop(0, 'rgba(139, 92, 246, 0.3)');  // brand-500 with transparency
    gradient.addColorStop(1, 'rgba(139, 92, 246, 0.0)');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Queries',
                data: counts,
                borderColor: '#8b5cf6',
                borderWidth: 2.5,
                backgroundColor: gradient,
                fill: true,
                tension: 0.35,
                pointBackgroundColor: '#8b5cf6',
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: chartGridColor },
                    ticks: { color: chartTextColor, font: { family: 'Inter', size: 10 } }
                },
                y: {
                    grid: { color: chartGridColor },
                    ticks: { 
                        color: chartTextColor, 
                        font: { family: 'Inter', size: 10 },
                        precision: 0
                    },
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Doughnut Chart: Top Categories matched
 */
function initTopicsChart() {
    const ctx = document.getElementById('topicsChart');
    if (!ctx) return;

    const data = statsData.top_topics || [];
    
    if (data.length === 0) {
        // Fallback placeholder text if no matching topics yet
        ctx.parentElement.innerHTML = `<p class="text-xs text-slate-400 font-medium">No trending topics logged yet.</p>`;
        return;
    }

    const labels = data.map(item => item.category);
    const counts = data.map(item => item.count);

    const colors = [
        '#8b5cf6', // Violet
        '#6366f1', // Indigo
        '#3b82f6', // Blue
        '#10b981', // Emerald
        '#f59e0b', // Amber
        '#ec4899', // Pink
        '#ef4444', // Red
        '#14b8a6', // Teal
        '#64748b'  // Slate
    ];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: isDarkMode ? 2 : 1,
                borderColor: isDarkMode ? '#0c1220' : '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: chartTextColor,
                        boxWidth: 10,
                        padding: 15,
                        font: { family: 'Inter', size: 9, weight: '500' }
                    }
                }
            },
            cutout: '65%'
        }
    });
}

/**
 * Horizontal Bar Chart: Most Asked FAQs (Top 5)
 */
function initMostAskedChart() {
    const ctx = document.getElementById('mostAskedChart');
    if (!ctx) return;

    const data = statsData.most_asked || [];

    if (data.length === 0) {
        ctx.parentElement.innerHTML = `<div class="h-full flex items-center justify-center text-xs text-slate-400 font-medium">No trending questions logged yet.</div>`;
        return;
    }

    // Shorten long questions for visual fit
    const labels = data.map(item => {
        const q = item.question;
        return q.length > 55 ? q.substring(0, 52) + "..." : q;
    });
    const counts = data.map(item => item.count);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: 'rgba(99, 102, 241, 0.85)', // Indigo-500
                hoverBackgroundColor: '#6366f1',
                borderRadius: 6,
                barThickness: 15
            }]
        },
        options: {
            indexAxis: 'y', // Horizontal bars
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: chartGridColor },
                    ticks: { 
                        color: chartTextColor, 
                        font: { family: 'Inter', size: 10 },
                        precision: 0 
                    },
                    beginAtZero: true
                },
                y: {
                    grid: { display: false },
                    ticks: { 
                        color: chartTextColor, 
                        font: { family: 'Inter', size: 9, weight: '500' }
                    }
                }
            }
        }
    });
}
