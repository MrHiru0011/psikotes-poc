from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

QUESTIONS = {
    "personality": [
        {
            "id": 1,
            "question": "Saat ada konflik dengan rekan kerja, saya biasanya...",
            "options": [
                {"text": "Langsung menghadapi dan diskusi tuntas", "score": 3, "trait": "assertive"},
                {"text": "Menunggu waktu yang tepat untuk bicara", "score": 2, "trait": "diplomatic"},
                {"text": "Menghindari agar situasi tidak memburuk", "score": 1, "trait": "avoidant"}
            ]
        },
        {
            "id": 2,
            "question": "Dalam pekerjaan tim, peran saya adalah...",
            "options": [
                {"text": "Memimpin dan mengambil inisiatif", "score": 3, "trait": "leader"},
                {"text": "Berkontribusi sesuai kebutuhan", "score": 2, "trait": "balanced"},
                {"text": "Mengikuti arahan dan menjalankan task", "score": 1, "trait": "follower"}
            ]
        },
        {
            "id": 3,
            "question": "Ketika target penjualan tidak tercapai, saya merasa...",
            "options": [
                {"text": "Sangat tertekan dan butuh motivasi", "score": 1, "trait": "anxious"},
                {"text": "Normal, analisis error dan benahi", "score": 3, "trait": "resilient"},
                {"text": "Sedikit frustasi tapi tetap fokus", "score": 2, "trait": "moderate"}
            ]
        },
        {
            "id": 4,
            "question": "Interaksi dengan pelanggan yang sulit, saya...",
            "options": [
                {"text": "Tetap sabar dan cari solusi terbaik", "score": 3, "trait": "empathetic"},
                {"text": "Cukup profesional menangani", "score": 2, "trait": "professional"},
                {"text": "Jadi kesal dan ingin cepat selesai", "score": 1, "trait": "impatient"}
            ]
        },
        {
            "id": 5,
            "question": "Saya lebih suka bekerja pada...",
            "options": [
                {"text": "Pekerjaan yang dinamis dan berubah-ubah", "score": 3, "trait": "adaptable"},
                {"text": "Pekerjaan dengan struktur jelas", "score": 2, "trait": "structured"},
                {"text": "Rutin dan dapat diprediksi", "score": 1, "trait": "routine"}
            ]
        }
    ],
    "reasoning": [
        {
            "id": 6,
            "question": "Jika penjualan bulan ini naik 20%, dan bulan depan naik 15%, berapa total kenaikan penjualan?",
            "options": [
                {"text": "35%", "correct": False, "explanation": "Kenaikan persentase tidak bisa dijumlahkan langsung"},
                {"text": "32%", "correct": True, "explanation": "Benar! Perhitungan berlapis"},
                {"text": "38%", "correct": False, "explanation": "Hampir, tapi hitung ulang"},
                {"text": "25%", "correct": False, "explanation": "Rata-rata bukan solusi"}
            ]
        },
        {
            "id": 7,
            "question": "Kolaborasi kerja: A bekerja 5 jam, B bekerja 3 jam, A lebih produktif 2x dari B. Siapa kontribusi lebih besar?",
            "options": [
                {"text": "A (5×2 = 10 unit)", "correct": True, "explanation": "Benar!"},
                {"text": "B (lebih efisien)", "correct": False},
                {"text": "Sama (total 8 jam kerja)", "correct": False},
                {"text": "Tergantung jenis pekerjaan", "correct": False}
            ]
        },
        {
            "id": 8,
            "question": "Pola angka: 2, 5, 10, 17, ?, 37",
            "options": [
                {"text": "24", "correct": False},
                {"text": "26", "correct": True, "explanation": "Benar! Pola +3, +5, +7, +9, +11"},
                {"text": "28", "correct": False},
                {"text": "20", "correct": False}
            ]
        },
        {
            "id": 9,
            "question": "Jika setiap hari Anda melayani 30 pelanggan, 85% puas. Berapa pelanggan tidak puas per hari?",
            "options": [
                {"text": "4.5 orang", "correct": True, "explanation": "15% × 30 = 4.5"},
                {"text": "5 orang", "correct": False},
                {"text": "25.5 orang", "correct": False},
                {"text": "15 orang", "correct": False}
            ]
        },
        {
            "id": 10,
            "question": "Urutan logis: Gaji → Kinerja → Target → ?",
            "options": [
                {"text": "Bonus", "correct": True, "explanation": "Benar!"},
                {"text": "Cuti", "correct": False},
                {"text": "Promosi", "correct": False},
                {"text": "Disiplin", "correct": False}
            ]
        }
    ],
    "spatial": [
        {
            "id": 11,
            "question": "Jika kotak di-rotasi 90° searah jarum jam, sisi mana yang menghadap atas?",
            "options": [
                {"text": "Sisi depan", "correct": False},
                {"text": "Sisi belakang", "correct": True},
                {"text": "Sisi samping", "correct": False},
                {"text": "Sisi bawah", "correct": False}
            ]
        },
        {
            "id": 12,
            "question": "Pattern: █ ▲ ● — ▲ ● █ — ● █ ▲ — ?",
            "options": [
                {"text": "█ ▲ ●", "correct": True, "explanation": "Pola berulang setiap 3"},
                {"text": "▲ ● █", "correct": False},
                {"text": "● █ ▲", "correct": False},
                {"text": "█ ● ▲", "correct": False}
            ]
        }
    ]
}

def calculate_personality_score(answers):
    traits = {}
    for answer in answers:
        q_id = answer['question_id']
        for q in QUESTIONS['personality']:
            if q['id'] == q_id:
                for opt in q['options']:
                    if opt['text'] == answer['selected']:
                        trait = opt.get('trait', 'unknown')
                        traits[trait] = traits.get(trait, 0) + opt['score']
    return traits

def calculate_reasoning_score(answers):
    correct = 0
    reasoning_answers = [a for a in answers if a['section'] == 'reasoning']
    for answer in reasoning_answers:
        q_id = answer['question_id']
        for q in QUESTIONS['reasoning']:
            if q['id'] == q_id:
                for opt in q['options']:
                    if opt['text'] == answer['selected']:
                        if opt.get('correct', False):
                            correct += 1
    total = len(reasoning_answers)
    percentage = (correct / total * 100) if total > 0 else 0
    return {"correct": correct, "total": total, "percentage": percentage}

def generate_report(personality, reasoning):
    report = {
        "personality_analysis": {},
        "reasoning_analysis": {},
        "overall_fit": ""
    }
    
    if personality.get('assertive', 0) > 8:
        report['personality_analysis']['leadership'] = "Tinggi - Cocok untuk posisi yang butuh leadership"
    else:
        report['personality_analysis']['leadership'] = "Sedang - Bisa develop lebih lanjut"
    
    if personality.get('resilient', 0) > 8:
        report['personality_analysis']['stress_handling'] = "Baik - Tahan pressure kerja"
    else:
        report['personality_analysis']['stress_handling'] = "Perlu improvement - Training resiliensi disarankan"
    
    reasoning_pct = reasoning['percentage']
    if reasoning_pct >= 80:
        report['reasoning_analysis']['analytical'] = "Excellent - Analisis logis sangat baik"
    elif reasoning_pct >= 60:
        report['reasoning_analysis']['analytical'] = "Good - Cukup mampu problem solving"
    else:
        report['reasoning_analysis']['analytical'] = "Needs improvement - Focus pada logical reasoning"
    
    if reasoning_pct >= 70 and personality.get('assertive', 0) > 6:
        report['overall_fit'] = "✅ COCOK untuk posisi Sales/Supervisor"
    elif reasoning_pct >= 60:
        report['overall_fit'] = "⚠️ CUKUP - Bisa diterima dengan training"
    else:
        report['overall_fit'] = "❌ PERLU IMPROVEMENT - Rekomendasi follow-up assessment"
    
    return report

@app.route('/api/questions', methods=['GET'])
def get_questions():
    return jsonify(QUESTIONS)

@app.route('/api/submit', methods=['POST'])
def submit_test():
    data = request.json
    answers = data.get('answers', [])
    
    personality_answers = [a for a in answers if a['section'] == 'personality']
    reasoning_answers = [a for a in answers if a['section'] == 'reasoning']
    
    personality_score = calculate_personality_score(personality_answers)
    reasoning_score = calculate_reasoning_score(reasoning_answers)
    report = generate_report(personality_score, reasoning_score)
    
    return jsonify({
        "status": "success",
        "personality_score": personality_score,
        "reasoning_score": reasoning_score,
        "report": report,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
