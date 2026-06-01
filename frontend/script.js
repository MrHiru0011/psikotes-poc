// URL Backend (ganti nanti saat deploy)
const API_URL = 'http://localhost:5000';

let QUESTIONS = {};

async function loadQuestions() {
    try {
        const response = await fetch(`${API_URL}/api/questions`);
        if (!response.ok) throw new Error('Backend tidak respond');
        QUESTIONS = await response.json();
        renderQuestions();
        updateProgress();
    } catch (err) {
        console.error('Error:', err);
        alert('⚠️ Tidak bisa load soal. Pastikan backend sudah jalan!');
    }
}

function renderQuestions() {
    renderSection('personality', 'personality-questions');
    renderSection('reasoning', 'reasoning-questions');
    renderSection('spatial', 'spatial-questions');
}

function renderSection(section, containerId) {
    const container = document.getElementById(containerId);
    const questions = QUESTIONS[section] || [];
    
    container.innerHTML = '';
    questions.forEach(q => {
        const html = `
            <div class="question-block">
                <div class="question-text">Q${q.id}. ${q.question}</div>
                <div class="options">
                    ${q.options.map((opt, idx) => `
                        <label>
                            <input type="radio" name="q${q.id}" value="${opt.text}" required onchange="updateProgress()">
                            <span>${opt.text}</span>
                        </label>
                    `).join('')}
                </div>
            </div>
        `;
        container.innerHTML += html;
    });
}

function updateProgress() {
    const form = document.getElementById('testForm');
    const totalQuestions = Object.values(QUESTIONS).flat().length;
    const answered = form.querySelectorAll('input[type="radio"]:checked').length;
    const percentage = (answered / totalQuestions) * 100;
    document.querySelector('.progress-bar').style.width = percentage + '%';
}

document.getElementById('testForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const answers = [];

    Object.keys(QUESTIONS).forEach(section => {
        (QUESTIONS[section] || []).forEach(q => {
            const answer = formData.get(`q${q.id}`);
            if (answer) {
                answers.push({
                    question_id: q.id,
                    section: section,
                    selected: answer
                });
            }
        });
    });

    const totalQuestions = Object.values(QUESTIONS).flat().length;
    if (answers.length < totalQuestions) {
        alert('⚠️ Semua soal harus dijawab, dit!');
        return;
    }

    document.getElementById('loading').style.display = 'block';

    try {
        const response = await fetch(`${API_URL}/api/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers })
        });

        if (!response.ok) throw new Error('Submit gagal');
        const result = await response.json();
        displayResult(result);
    } catch (err) {
        alert('❌ Error: ' + err.message);
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
});

function displayResult(result) {
    const resultDiv = document.getElementById('result');
    const contentDiv = document.getElementById('result-content');
    
    let html = `
        <div class="result-card">
            <h3>📊 Skor Penalaran</h3>
            <p><strong>Benar:</strong> ${result.reasoning_score.correct}/${result.reasoning_score.total}</p>
            <p><strong>Persentase:</strong> ${result.reasoning_score.percentage.toFixed(1)}%</p>
            <p>${result.report.reasoning_analysis.analytical}</p>
        </div>

        <div class="result-card">
            <h3>🧠 Analisis Kepribadian</h3>
            <p><strong>Leadership:</strong> ${result.report.personality_analysis.leadership}</p>
            <p><strong>Stress Handling:</strong> ${result.report.personality_analysis.stress_handling}</p>
        </div>

        <div class="overall">
            ${result.report.overall_fit}
        </div>

        <div class="result-card" style="margin-top: 15px; border-left-color: #999;">
            <p><small>⏰ Test selesai: ${new Date(result.timestamp).toLocaleString('id-ID')}</small></p>
        </div>
    `;

    contentDiv.innerHTML = html;
    resultDiv.classList.add('show');
    setTimeout(() => {
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// Load questions saat page load
loadQuestions();
