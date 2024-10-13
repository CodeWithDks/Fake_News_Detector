document.addEventListener('DOMContentLoaded', () => {
    const newsText = document.getElementById('news-text');
    const predictBtn = document.getElementById('predict-btn');
    const result = document.getElementById('result');
    const predictionText = document.getElementById('prediction-text');
    const confidenceBar = document.getElementById('confidence-bar');
    const confidenceText = document.getElementById('confidence-text');
    const explanationText = document.getElementById('explanation-text');
    const loading = document.getElementById('loading');
    const stats = document.getElementById('stats');
    const statsChart = document.getElementById('stats-chart');

    let chart = null;

    predictBtn.addEventListener('click', async () => {
        const text = newsText.value.trim();
        if (text === '') {
            alert('Please enter some text to analyze.');
            return;
        }

        result.classList.add('hidden');
        stats.classList.add('hidden');
        loading.classList.remove('hidden');

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text }),
            });

            const data = await response.json();
            
            loading.classList.add('hidden');
            result.classList.remove('hidden');
            stats.classList.remove('hidden');

            // Update result card
            const resultCard = result.querySelector('.result-card');
            resultCard.className = `result-card ${data.prediction}`;
            predictionText.textContent = `This news is likely ${data.prediction.toUpperCase()}`;
            confidenceBar.style.width = `${data.confidence}%`;
            confidenceText.textContent = `Confidence: ${data.confidence.toFixed(2)}%`;

            // Update explanation
            if (data.prediction === 'real') {
                explanationText.textContent = 'This article appears to contain characteristics of legitimate news. However, always cross-reference with other reliable sources.';
            } else {
                explanationText.textContent = 'This article shows signs of being potentially misleading or false. Be cautious and verify the information from trusted sources.';
            }

            // Update stats chart
            updateStatsChart(data.real_count, data.fake_count);

        } catch (error) {
            console.error('Error:', error);
            loading.classList.add('hidden');
            alert('An error occurred while processing your request. Please try again.');
        }
    });

    function updateStatsChart(realCount, fakeCount) {
        if (chart) {
            chart.destroy();
        }

        chart = new Chart(statsChart, {
            type: 'doughnut',
            data: {
                labels: ['Real', 'Fake'],
                datasets: [{
                    data: [realCount, fakeCount],
                    backgroundColor: ['#2ecc71', '#e74c3c'],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Your Prediction History'
                    }
                }
            }
        });
    }
});