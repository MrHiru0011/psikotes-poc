// URL Backend
const API_URL = 'http://localhost:5000'; // Ganti saat deploy

let QUESTIONS = {};
let CURRENT_TEST_ID = null;

// ===== START NEW TEST =====
async function startNewTest() {
    try {
        document.getElementById('loading').style.display = 'block';
        
        const response = await fetch(`${API_URL}/api/start-test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) throw new Error('Start test gagal');
        
        const data = await response.json();
        CURRENT_TEST_ID = data.test_id;
        QUESTIONS = data.questions;
        
        console.log('✅ Test baru dimulai! ID:', CURRENT_TEST_ID);
        
        // Clear form dan render questions baru
        document.getElementById('testForm').reset();
        renderQuestions();
        
        // Hide result, show form
        document.getElementById('result').classList.remove('show');
        document.getElementById('testForm').style.display = 'block';
        
        updateProgress();
        
        // Scroll ke atas
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        // Show success message
        showNotification('🎉 ' + data.message, 'success');
        
    } catch (err) {
        console.error('Error:', err);
        showNotification('❌ ' + err.message, 'error');
    } finally {
        document.getElementById('loading').style.display = 'none';
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

// ===== FORM SUBMISSION =====
document.getElementById('testForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!CURRENT_TEST_ID) {
        alert('⚠️ Test belum di-start! Tap "Mulai Test Baru" dulu.');
        return;
    }
    
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
            body: JSON.stringify({ 
                test_id: CURRENT_TEST_ID,
                answers: answers 
            })
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
            <p><small>Test ID: ${result.test_id}</small></p>
        </div>

        <div class="button-group" style="margin-top: 20px;">
            <button type="button" class="btn-submit" onclick="startNewTest()" style="background: linear-gradient(135deg, #667eea, #764ba2); border: none; color: white;">
                🔄 Mulai Test Baru (Soal Berbeda!)
            </button>
        </div>
    `;

    contentDiv.innerHTML = html;
    resultDiv.classList.add('show');
    document.getElementById('testForm').style.display = 'none';
    
    setTimeout(() => {
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

function showNotification(message, type) {
    const notif = document.createElement('div');
    notif.textContent = message;
    notif.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#10b981' : '#ef4444'};
        color: white;
        border-radius: 8px;
        z-index: 1000;
        animation: slideInRight 0.3s ease;
    `;
    document.body.appendChild(notif);
    setTimeout(() => notif.remove(), 3000);
}

// Initial page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ Frontend ready. Tap "Mulai Test Baru" untuk start!');
});
