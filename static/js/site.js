// Auto-dismiss toasts
document.addEventListener('DOMContentLoaded', function () {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(function (t) {
        setTimeout(function () {
            t.style.opacity = '0';
            t.style.transition = 'opacity 0.5s';
            setTimeout(function () { t.remove(); }, 500);
        }, 4000);
    });
});

// Chart.js defaults
if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = "'DM Sans', sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#8492a6';
    Chart.defaults.plugins.legend.labels.boxWidth = 12;
}

function formatCurrency(val) {
    return '₹' + Number(val).toLocaleString('en-IN', { minimumFractionDigits: 0 });
}
