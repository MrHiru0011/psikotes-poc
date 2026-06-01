from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import random
import os

app = Flask(__name__)
CORS(app)

# ===== QUESTION TEMPLATES (Akan di-generate dinamis) =====

PERSONALITY_TEMPLATES = [
    {
        "question_pattern": "Saat ada konflik dengan rekan kerja, saya biasanya...",
        "options": [
            {"text": "Langsung menghadapi dan diskusi tuntas", "score": 3, "trait": "assertive"},
            {"text": "Menunggu waktu yang tepat untuk bicara", "score": 2, "trait": "diplomatic"},
            {"text": "Menghindari agar situasi tidak memburuk", "score": 1, "trait": "avoidant"}
        ]
    },
    {
        "question_pattern": "Dalam pekerjaan tim, peran saya adalah...",
        "options": [
            {"text": "Memimpin dan mengambil inisiatif", "score": 3, "trait": "leader"},
            {"text": "Berkontribusi sesuai kebutuhan", "score": 2, "trait": "balanced"},
            {"text": "Mengikuti arahan dan menjalankan task", "score": 1, "trait": "follower"}
        ]
    },
    {
        "question_pattern": "Ketika target penjualan tidak tercapai, saya merasa...",
        "options": [
            {"text": "Sangat tertekan dan butuh motivasi", "score": 1, "trait": "anxious"},
            {"text": "Normal, analisis error dan benahi", "score": 3, "trait": "resilient"},
            {"text": "Sedikit frustasi tapi tetap fokus", "score": 2, "trait": "moderate"}
        ]
    },
    {
        "question_pattern": "Interaksi dengan pelanggan yang sulit, saya...",
        "options": [
            {"text": "Tetap sabar dan cari solusi terbaik", "score": 3, "trait": "empathetic"},
            {"text": "Cukup profesional menangani", "score": 2, "trait": "professional"},
            {"text": "Jadi kesal dan ingin cepat selesai", "score": 1, "trait": "impatient"}
        ]
    },
    {
        "question_pattern": "Saya lebih suka bekerja pada...",
        "options": [
            {"text": "Pekerjaan yang dinamis dan berubah-ubah", "score": 3, "trait": "adaptable"},
            {"text": "Pekerjaan dengan struktur jelas", "score": 2, "trait": "structured"},
            {"text": "Rutin dan dapat diprediksi", "score": 1, "trait": "routine"}
        ]
    },
    {
        "question_pattern": "Saat deadline mendesak, saya cenderung...",
        "options": [
            {"text": "Bekerja lebih cepat dan tetap fokus", "score": 3, "trait": "resilient"},
            {"text": "Sedikit stress tapi bisa handle", "score": 2, "trait": "moderate"},
            {"text": "Panik dan kurang produktif", "score": 1, "trait": "anxious"}
        ]
    },
    {
        "question_pattern": "Jika ada ide baru dari rekan kerja, saya...",
        "options": [
            {"text": "Langsung support dan implementasi", "score": 3, "trait": "adaptable"},
            {"text": "Pertimbang dulu sebelum keputusan", "score": 2, "trait": "balanced"},
            {"text": "Lebih suka cara yang sudah terbukti", "score": 1, "trait": "routine"}
        ]
    },
    {
        "question_pattern": "Dalam memberikan feedback negatif, saya...",
        "options": [
            {"text": "Langsung, jelas, dan konstruktif", "score": 3, "trait": "assertive"},
            {"text": "Diplomatis dan perhatikan perasaan", "score": 2, "trait": "diplomatic"},
            {"text": "Cenderung hindari agar tak tersinggung", "score": 1, "trait": "avoidant"}
        ]
    },
    {
        "question_pattern": "Ketika ada perubahan di tempat kerja, saya...",
        "options": [
            {"text": "Embrace dan cari peluang baru", "score": 3, "trait": "adaptable"},
            {"text": "Adjust tapi butuh waktu", "score": 2, "trait": "moderate"},
            {"text": "Merasa tidak nyaman dengan perubahan", "score": 1, "trait": "routine"}
        ]
    },
    {
        "question_pattern": "Kesuksesan tim lebih penting daripada...",
        "options": [
            {"text": "Ya, tim duluan", "score": 3, "trait": "empathetic"},
            {"text": "Tergantung situasinya", "score": 2, "trait": "balanced"},
            {"text": "Prioritas pribadi juga penting", "score": 1, "trait": "leader"}
        ]
    }
]

REASONING_TEMPLATES = [
    {
        "question": "Jika penjualan bulan ini naik 20%, dan bulan depan naik 15%, berapa total kenaikan penjualan?",
        "options": [
            {"text": "35%", "correct": False, "explanation": "Kenaikan persentase tidak bisa dijumlahkan langsung"},
            {"text": "32%", "correct": True, "explanation": "Perhitungan berlapis: 20% dari X = 1.2X, lalu 15% dari 1.2X = 1.38X"},
            {"text": "38%", "correct": False, "explanation": "Hampir, tapi hitung ulang"},
            {"text": "25%", "correct": False, "explanation": "Rata-rata bukan solusi"}
        ]
    },
    {
        "question": "Kolaborasi kerja: A bekerja 5 jam, B bekerja 3 jam, A lebih produktif 2x dari B. Siapa kontribusi lebih besar?",
        "options": [
            {"text": "A (5×2 = 10 unit)", "correct": True, "explanation": "A: 5 jam × 2 = 10 unit, B: 3 jam × 1 = 3 unit"},
            {"text": "B (lebih efisien)", "correct": False},
            {"text": "Sama (total 8 jam kerja)", "correct": False},
            {"text": "Tergantung jenis pekerjaan", "correct": False}
        ]
    },
    {
        "question": "Pola angka: 2, 5, 10, 17, ?, 37",
        "options": [
            {"text": "24", "correct": False},
            {"text": "26", "correct": True, "explanation": "Pola beda: +3, +5, +7, +9, +11"},
            {"text": "28", "correct": False},
            {"text": "20", "correct": False}
        ]
    },
    {
        "question": "Jika setiap hari melayani 30 pelanggan, 85% puas. Berapa pelanggan tidak puas per hari?",
        "options": [
            {"text": "4.5 orang", "correct": True, "explanation": "15% × 30 = 4.5 pelanggan"},
            {"text": "5 orang", "correct": False},
            {"text": "25.5 orang", "correct": False},
            {"text": "15 orang", "correct": False}
        ]
    },
    {
        "question": "Urutan logis: Gaji → Kinerja → Target → ?",
        "options": [
            {"text": "Bonus", "correct": True, "explanation": "Bonus hasil dari pencapaian target"},
            {"text": "Cuti", "correct": False},
            {"text": "Promosi", "correct": False},
            {"text": "Disiplin", "correct": False}
        ]
    },
    {
        "question": "Jika Anda melayani 40 customer per hari, 70% satisfied. Minggu depan target naik 10%, berapa customer harusnya satisfied?",
        "options": [
            {"text": "30.8 orang", "correct": True, "explanation": "44 customer × 70% = 30.8"},
            {"text": "28 orang", "correct": False},
            {"text": "32 orang", "correct": False},
            {"text": "35 orang", "correct": False}
        ]
    },
    {
        "question": "Pola: 3, 7, 15, 31, ?",
        "options": [
            {"text": "63", "correct": True, "explanation": "Pola: ×2+1 setiap step. 3×2+1=7, 7×2+1=15, 15×2+1=31, 31×2+1=63"},
            {"text": "47", "correct": False},
            {"text": "55", "correct": False},
            {"text": "48", "correct": False}
        ]
    },
    {
        "question": "Jika Anda bisa clear 50 task per bulan, dan efisiensi naik 25%, berapa task seharusnya?",
        "options": [
            {"text": "62.5 task", "correct": True, "explanation": "50 × 1.25 = 62.5"},
            {"text": "62 task", "correct": False},
            {"text": "75 task", "correct": False},
            {"text": "50 task", "correct": False}
        ]
    },
    {
        "question": "Sequence logic: Senin → Selasa → Rabu → ?",
        "options": [
            {"text": "Kamis", "correct": True, "explanation": "Hari berurutan"},
            {"text": "Jum'at", "correct": False},
            {"text": "Sabtu", "correct": False},
            {"text": "Minggu", "correct": False}
        ]
    },
    {
        "question": "Jika budget Rp 1 juta, dan 40% untuk opex, 30% untuk inventory, sisanya untuk bonus staff. Berapa bonus?",
        "options": [
            {"text": "Rp 300 ribu", "correct": True, "explanation": "100% - 40% - 30% = 30%. 30% × 1 juta = 300 ribu"},
            {"text": "Rp 400 ribu", "correct": False},
            {"text": "Rp 700 ribu", "correct": False},
            {"text": "Rp 600 ribu", "correct": False}
        ]
    }
]

SPATIAL_TEMPLATES = [
    {
        "question": "Jika kotak di-rotasi 90° searah jarum jam, sisi mana yang menghadap atas?",
        "options": [
            {"text": "Sisi depan", "correct": False},
            {"text": "Sisi belakang", "correct": True},
            {"text": "Sisi samping", "correct": False},
            {"text": "Sisi bawah", "correct": False}
        ]
    },
    {
        "question": "Pattern: █ ▲ ● — ▲ ● █ — ● █ ▲ — ?",
        "options": [
            {"text": "█ ▲ ●", "correct": True, "explanation": "Pola berulang setiap 3"},
            {"text": "▲ ● █", "correct": False},
            {"text": "● █ ▲", "correct": False},
            {"text": "█ ● ▲", "correct": False}
        ]
    },
    {
        "question": "Jika segitiga diputar 180°, posisinya jadi?",
        "options": [
            {"text": "Terbalik (titik di bawah)", "correct": True},
            {"text": "Sama seperti awal", "correct": False},
            {"text": "Miring ke kanan", "correct": False},
            {"text": "Hilang", "correct": False}
        ]
    },
    {
        "question": "Pattern visual: ◆ ◆ ◇ — ◆ ◇ ◆ — ◇ ◆ ◆ — ?",
        "options": [
            {"text": "◆ ◆ ◇", "correct": True, "explanation": "Pola berulang"},
            {"text": "◇ ◇ ◆", "correct": False},
            {"text": "◆ ◇ ◇", "correct": False},
            {"text": "◇ ◆ ◇", "correct": False}
        ]
    }
]

# ===== GENERATOR FUNCTION =====

def generate_test_questions(test_id=None):
    """Generate random set of questions untuk setiap test"""
    
    questions = {
        "personality": [],
        "reasoning": [],
        "spatial": []
    }
    
    # Personality: random 5 dari 10
    personality_sample = random.sample(PERSONALITY_TEMPLATES, 5)
    for idx, template in enumerate(personality_sample, 1):
        questions["personality"].append({
            "id": idx,
            "question": template["question_pattern"],
            "options": template["options"]
        })
    
    # Reasoning: random 5 dari 10
    reasoning_sample = random.sample(REASONING_TEMPLATES, 5)
    for idx, template in enumerate(reasoning_sample, 6):  # ID start from 6
        questions["reasoning"].append({
            "id": idx,
            "question": template["question"],
            "options": template["options"]
        })
    
    # Spatial: random 2 dari 4
    spatial_sample = random.sample(SPATIAL_TEMPLATES, 2)
    for idx, template in enumerate(spatial_sample, 11):  # ID start from 11
        questions["spatial"].append({
            "id": idx,
            "question": template["question"],
            "options": template["options"]
        })
    
    return questions

# ===== SCORING FUNCTIONS =====

def calculate_personality_score(questions, answers):
    traits = {}
    for answer in answers:
        q_id = answer['question_id']
        # Find question in all sections
        for q in questions["personality"]:
            if q['id'] == q_id:
                for opt in q['options']:
                    if opt['text'] == answer['selected']:
                        trait = opt.get('trait', 'unknown')
                        traits[trait] = traits.get(trait, 0) + opt['score']
    return traits

def calculate_reasoning_score(questions, answers):
    correct = 0
    reasoning_answers = [a for a in answers if a['section'] == 'reasoning']
    for answer in reasoning_answers:
        q_id = answer['question_id']
        for q in questions["reasoning"]:
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

# ===== ROUTES =====

# Store current test questions (session-based)
current_test = {}

@app.route('/api/start-test', methods=['POST'])
def start_test():
    """Generate fresh set of questions untuk test baru"""
    global current_test
    
    test_id = random.randint(1000, 9999)
    questions = generate_test_questions(test_id)
    current_test[test_id] = questions
    
    return jsonify({
        "status": "success",
        "test_id": test_id,
        "questions": questions,
        "message": "Test baru berhasil di-generate! Soal-soalnya berbeda dari sebelumnya 🎉"
    })

@app.route('/api/get-questions/<test_id>', methods=['GET'])
def get_questions(test_id):
    """Get questions untuk test yang sedang berjalan"""
    if test_id in current_test:
        return jsonify(current_test[test_id])
    else:
        return jsonify({"error": "Test ID tidak ditemukan"}), 404

@app.route('/api/submit', methods=['POST'])
def submit_test():
    """Submit jawaban dan dapatkan hasil"""
    data = request.json
    test_id = data.get('test_id')
    answers = data.get('answers', [])
    
    if test_id not in current_test:
        return jsonify({"error": "Test ID invalid"}), 400
    
    questions = current_test[test_id]
    
    personality_answers = [a for a in answers if a['section'] == 'personality']
    reasoning_answers = [a for a in answers if a['section'] == 'reasoning']
    
    personality_score = calculate_personality_score(questions, personality_answers)
    reasoning_score = calculate_reasoning_score(questions, reasoning_answers)
    report = generate_report(personality_score, reasoning_score)
    
    # Clean up
    del current_test[test_id]
    
    return jsonify({
        "status": "success",
        "test_id": test_id,
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
