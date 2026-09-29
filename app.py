'''
October Fest & Halloween Party - Web App Online con Flask & SQLite3
File: app.py
'''

import sqlite3
import random
import os
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

DB_FILE = "october_party.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            adults INTEGER NOT NULL,
            kids INTEGER NOT NULL,
            total_price REAL NOT NULL,
            privacy_consent INTEGER DEFAULT 1,
            status TEXT DEFAULT 'confirmed',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('admin_pin', '1234')")
    conn.commit()
    conn.close()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>October Fest & Halloween Party</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-slate-900 text-slate-100 font-sans min-h-screen flex flex-col justify-between">

    <div>
        <nav class="bg-slate-950/80 border-b border-slate-800 p-4 sticky top-0 z-50 backdrop-blur-md">
            <div class="max-w-5xl mx-auto flex justify-between items-center">
                <div class="flex items-center gap-2 font-bold text-orange-500">
                    <i class="fa-solid fa-beer-mug-empty text-xl"></i>
                    <span>October & Halloween Party</span>
                </div>
                <button onclick="toggleAdminView()" class="bg-amber-600/20 hover:bg-amber-600/30 text-amber-400 border border-amber-500/30 text-xs font-bold px-3 py-2 rounded-lg transition flex items-center gap-2">
                    <i class="fa-solid fa-user-shield"></i>
                    <span id="navAdminBtnText">Area Gestione Organizzatore</span>
                </button>
            </div>
        </nav>

        <header class="bg-gradient-to-r from-orange-600 via-amber-600 to-amber-700 text-white p-6 text-center shadow-2xl relative overflow-hidden">
            <div class="max-w-4xl mx-auto relative z-10">
                <span class="bg-amber-900/80 text-amber-200 text-xs uppercase px-3 py-1 rounded-full font-bold tracking-widest border border-amber-500/30">Festa Ibrida per Tutta la Famiglia</span>
                <h1 class="text-3xl md:text-5xl font-black mt-2 tracking-tight drop-shadow-md">OCTOBER FEST & HALLOWEEN PARTY 🍻🎃</h1>
                <p class="mt-2 text-amber-100 font-medium text-sm md:text-base">Divertimento per Adulti e Bambini con Animazione per Tutti!</p>
            </div>
        </header>

        <!-- VISTA PARTECIPANTI -->
        <main id="userSection" class="max-w-4xl mx-auto p-4 md:p-6 grid md:grid-cols-2 gap-6 transition-all duration-300">
            <div class="bg-slate-800/90 border border-slate-700 rounded-2xl p-6 shadow-xl">
                <h2 class="text-2xl font-bold text-orange-400 mb-4 flex items-center gap-2">
                    <i class="fa-solid fa-ticket"></i> Prenota Ora
                </h2>
                
                <form id="bookingForm" onsubmit="submitBooking(event)" class="space-y-4">
                    <div>
                        <label class="block text-xs uppercase text-slate-400 mb-1 font-semibold">Nome e Cognome *</label>
                        <input type="text" id="name" required class="w-full bg-slate-700/80 border border-slate-600 rounded-lg p-2.5 text-white focus:outline-none focus:border-orange-500" placeholder="Mario Rossi">
                    </div>
                    
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-xs uppercase text-slate-400 mb-1 font-semibold">Email *</label>
                            <input type="email" id="email" required class="w-full bg-slate-700/80 border border-slate-600 rounded-lg p-2.5 text-white focus:outline-none focus:border-orange-500" placeholder="mario@email.it">
                        </div>
                        <div>
                            <label class="block text-xs uppercase text-slate-400 mb-1 font-semibold">Telefono *</label>
                            <input type="tel" id="phone" required class="w-full bg-slate-700/80 border border-slate-600 rounded-lg p-2.5 text-white focus:outline-none focus:border-orange-500" placeholder="3331234567">
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3 bg-slate-900/50 p-3 rounded-xl border border-slate-700">
                        <div>
                            <label class="block text-xs text-slate-300 mb-1">Adulti (€10)</label>
                            <input type="number" id="adults" min="1" value="1" onchange="calcTotal()" class="w-full bg-slate-700 border border-slate-600 rounded-lg p-2 text-center text-xl font-bold text-orange-400">
                        </div>
                        <div>
                            <label class="block text-xs text-slate-300 mb-1">Bambini (€5)</label>
                            <input type="number" id="kids" min="0" value="0" onchange="calcTotal()" class="w-full bg-slate-700 border border-slate-600 rounded-lg p-2 text-center text-xl font-bold text-amber-400">
                        </div>
                    </div>

                    <div class="flex justify-between items-center text-sm font-semibold py-1">
                        <span class="text-slate-400">Totale Stimato:</span>
                        <span id="totalDisplay" class="text-2xl font-black text-amber-400">€10.00</span>
                    </div>

                    <div class="bg-slate-900/80 p-3 rounded-lg border border-slate-700 text-xs text-slate-300 space-y-2">
                        <label class="flex items-start gap-2 cursor-pointer">
                            <input type="checkbox" id="privacyConsent" required class="mt-0.5 rounded border-slate-600 text-orange-500 focus:ring-0">
                            <span>Accetto il trattamento dei dati personali (GDPR) per l'evento.</span>
                        </label>
                    </div>

                    <button type="submit" class="w-full bg-orange-600 hover:bg-orange-500 text-white font-bold py-3 px-4 rounded-xl shadow-lg transition duration-200">
                        CONFERMA E GENERA QR CODE
                    </button>
                </form>
            </div>

            <!-- TICKET DISPLAY -->
            <div class="bg-slate-800/90 border border-slate-700 rounded-2xl p-6 shadow-xl flex flex-col justify-center items-center text-center">
                <div id="qrPlaceholder">
                    <i class="fa-solid fa-qrcode text-6xl text-slate-600 mb-3"></i>
                    <h3 class="text-lg font-bold text-slate-400">Nessun Pass Generato</h3>
                    <p class="text-xs text-slate-500 mt-1 max-w-xs">Compila il modulo per generare il pass con QR Code di registrazione automatica.</p>
                </div>

                <div id="ticketSuccess" class="hidden space-y-4">
                    <div class="inline-block bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-3 py-1 rounded-full text-xs font-semibold">
                        ✓ Prenotazione Riuscita!
                    </div>
                    <div class="bg-white p-4 rounded-xl inline-block shadow-lg" id="qrcode"></div>
                    <div>
                        <h4 id="ticketId" class="text-xl font-mono font-bold text-orange-400"></h4>
                        <p id="ticketDetails" class="text-sm text-slate-300 mt-1"></p>
                        <p class="text-xs text-emerald-400 font-semibold mt-2">Inquadra questo QR Code con uno smartphone per effettuare il Check-in nel database!</p>
                    </div>
                </div>
            </div>
        </main>

        <!-- VISTA ADMIN -->
        <section id="adminSection" class="max-w-4xl mx-auto p-4 md:p-6 hidden transition-all duration-300">
            <div class="bg-slate-800 border border-amber-500/30 rounded-2xl p-6 shadow-2xl">
                <div class="flex justify-between items-center mb-6 border-b border-slate-700 pb-4">
                    <h2 class="text-2xl font-bold text-amber-400 flex items-center gap-2">
                        <i class="fa-solid fa-user-shield"></i> Area Gestione Prenotazioni
                    </h2>
                    <button onclick="toggleAdminView()" class="text-xs bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded-lg text-slate-300">
                        ← Torna al Form
                    </button>
                </div>

                <div id="pinBox" class="space-y-4 max-w-xs mx-auto text-center py-8">
                    <div class="w-12 h-12 bg-amber-500/10 text-amber-400 rounded-full flex items-center justify-center mx-auto text-xl border border-amber-500/20">
                        <i class="fa-solid fa-lock"></i>
                    </div>
                    <p class="text-sm text-slate-300 font-semibold">Inserisci PIN Organizzatore (Default: 1234):</p>
                    <input type="password" id="adminPin" class="w-full bg-slate-700 border border-slate-600 rounded-lg p-2.5 text-center text-2xl tracking-widest text-white focus:outline-none focus:border-amber-500" placeholder="****">
                    <button onclick="verifyAdminPin()" class="w-full bg-amber-600 hover:bg-amber-500 text-white font-bold py-2.5 rounded-lg transition">
                        Sblocca Pannello
                    </button>
                </div>

                <div id="adminContent" class="hidden space-y-6">
                    <div class="space-y-3">
                        <div class="flex justify-between items-center">
                            <span class="text-sm font-semibold text-slate-300">Totale Prenotati: <b id="countTotal" class="text-orange-400">0</b></span>
                            <button onclick="loadAdminBookings()" class="bg-slate-700 hover:bg-slate-600 text-xs px-3 py-1.5 rounded-lg text-white font-semibold">
                                <i class="fa-solid fa-rotate"></i> Aggiorna
                            </button>
                        </div>

                        <div class="overflow-x-auto rounded-xl border border-slate-700">
                            <table class="w-full text-left text-xs text-slate-300 border-collapse">
                                <thead>
                                    <tr class="bg-slate-900 text-orange-400 uppercase border-b border-slate-700">
                                        <th class="p-3">ID</th>
                                        <th class="p-3">Nome</th>
                                        <th class="p-3">Contatti</th>
                                        <th class="p-3 text-center">Adulti/Bambini</th>
                                        <th class="p-3">Totale</th>
                                        <th class="p-3 text-center">Stato</th>
                                        <th class="p-3 text-center">Azioni</th>
                                    </tr>
                                </thead>
                                <tbody id="adminTableBody"></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </div>

    <footer class="text-center py-4 text-xs text-slate-600 border-t border-slate-800">
        October Fest & Halloween Party Management System
    </footer>

    <script>
        let currentAdminPin = "";
        let isAdminLoggedIn = false;

        function calcTotal() {
            const adults = parseInt(document.getElementById('adults').value) || 0;
            const kids = parseInt(document.getElementById('kids').value) || 0;
            const total = (adults * 10) + (kids * 5);
            document.getElementById('totalDisplay').innerText = `€${total.toFixed(2)}`;
        }

        async function submitBooking(e) {
            e.preventDefault();
            const payload = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                phone: document.getElementById('phone').value,
                adults: parseInt(document.getElementById('adults').value),
                kids: parseInt(document.getElementById('kids').value),
                privacy_consent: document.getElementById('privacyConsent').checked ? 1 : 0
            };

            try {
                const res = await fetch('/api/bookings', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                
                const data = await res.json();
                if(data.success) {
                    document.getElementById('qrPlaceholder').classList.add('hidden');
                    document.getElementById('ticketSuccess').classList.remove('hidden');
                    document.getElementById('ticketId').innerText = data.booking_id;
                    document.getElementById('ticketDetails').innerText = `${payload.name} (${payload.adults}A + ${payload.kids}B) - €${data.total_price.toFixed(2)}`;
                    
                    document.getElementById('qrcode').innerHTML = '';
                    
                    // Genera QR Code basato sull'URL online del server
                    const checkinUrl = `${window.location.origin}/scan/${data.booking_id}`;
                    new QRCode(document.getElementById('qrcode'), {
                        text: checkinUrl,
                        width: 150,
                        height: 150
                    });
                } else {
                    alert('Errore: ' + (data.error || 'Impossibile salvare la prenotazione'));
                }
            } catch(err) {
                alert('Errore di connessione al server.');
            }
        }

        function toggleAdminView() {
            const userSec = document.getElementById('userSection');
            const adminSec = document.getElementById('adminSection');
            const navBtnText = document.getElementById('navAdminBtnText');

            if (adminSec.classList.contains('hidden')) {
                userSec.classList.add('hidden');
                adminSec.classList.remove('hidden');
                navBtnText.innerText = "Torna alle Prenotazioni";
                if (isAdminLoggedIn) loadAdminBookings();
            } else {
                adminSec.classList.add('hidden');
                userSec.classList.remove('hidden');
                navBtnText.innerText = "Area Gestione Organizzatore";
            }
        }

        async function verifyAdminPin() {
            const pin = document.getElementById('adminPin').value;
            const res = await fetch('/api/admin/verify-pin', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({pin})
            });
            const data = await res.json();
            if(data.valid) {
                currentAdminPin = pin;
                isAdminLoggedIn = true;
                document.getElementById('pinBox').classList.add('hidden');
                document.getElementById('adminContent').classList.remove('hidden');
                loadAdminBookings();
            } else {
                alert('PIN Errato!');
            }
        }

        async function loadAdminBookings() {
            const res = await fetch('/api/bookings');
            const bookings = await res.json();
            document.getElementById('countTotal').innerText = bookings.length;
            
            const tbody = document.getElementById('adminTableBody');
            if(bookings.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="p-4 text-center text-slate-500">Nessuna prenotazione presente.</td></tr>`;
                return;
            }

            tbody.innerHTML = bookings.map(b => `
                <tr class="border-b border-slate-700/50 hover:bg-slate-700/30">
                    <td class="p-3 font-mono text-orange-400 font-bold">${b.id}</td>
                    <td class="p-3 font-semibold">${b.name}</td>
                    <td class="p-3">${b.email}<br><span class="text-slate-400">${b.phone}</span></td>
                    <td class="p-3 text-center">${b.adults}A / ${b.kids}B</td>
                    <td class="p-3 font-bold text-amber-400">€${b.total_price.toFixed(2)}</td>
                    <td class="p-3 text-center">
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${b.status === 'checked_in' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'}">
                            ${b.status === 'checked_in' ? 'PRESENTE (CHECK-IN)' : 'CONFERMATO'}
                        </span>
                    </td>
                    <td class="p-3 text-center space-x-1">
                        <button onclick="toggleCheckin('${b.id}')" class="bg-slate-700 hover:bg-slate-600 px-2.5 py-1 rounded text-white text-[10px] font-semibold">
                            Cambia Stato
                        </button>
                        <button onclick="deleteBooking('${b.id}')" class="bg-red-600/80 hover:bg-red-600 px-2.5 py-1 rounded text-white text-[10px] font-semibold">
                            Elimina
                        </button>
                    </td>
                </tr>
            `).join('');
        }

        async function toggleCheckin(id) {
            await fetch(`/api/bookings/${id}/checkin`, {method: 'POST'});
            loadAdminBookings();
        }

        async function deleteBooking(id) {
            if(!confirm(`Eliminare la prenotazione ${id}?`)) return;
            await fetch(`/api/bookings/${id}`, { method: 'DELETE' });
            loadAdminBookings();
        }
    </script>
</body>
</html>
"""

SCAN_RESULT_TEMPLATE = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Check-in Effettuato</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen flex items-center justify-center p-4">
    <div class="bg-slate-800 border border-slate-700 p-6 rounded-2xl max-w-sm w-full text-center shadow-2xl space-y-4">
        <div class="w-16 h-16 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center mx-auto text-3xl border border-emerald-500/30">
            <i class="fa-solid fa-check"></i>
        </div>
        <h1 class="text-2xl font-bold text-emerald-400">Check-in Registrato!</h1>
        <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-700 text-left space-y-2 text-sm">
            <p><span class="text-slate-400">Codice:</span> <b class="text-orange-400 font-mono">{{ booking.id }}</b></p>
            <p><span class="text-slate-400">Nome:</span> <b>{{ booking.name }}</b></p>
            <p><span class="text-slate-400">Partecipanti:</span> <b>{{ booking.adults }} Adulti, {{ booking.kids }} Bambini</b></p>
            <p><span class="text-slate-400">Stato DB:</span> <span class="text-emerald-400 font-bold uppercase">PRESENTE (CHECKED_IN)</span></p>
        </div>
        <p class="text-xs text-slate-400">La prenotazione è stata aggiornata con successo nel database.</p>
        <a href="/" class="inline-block w-full bg-slate-700 hover:bg-slate-600 text-white font-bold py-2.5 rounded-lg text-sm transition">Torna alla Home</a>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan/<booking_id>')
def scan_qr_checkin(booking_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET status = 'checked_in' WHERE id = ?", (booking_id,))
    conn.commit()
    cursor.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
    booking = cursor.fetchone()
    conn.close()
    if not booking:
        return "Prenotazione non trovata", 404
    return render_template_string(SCAN_RESULT_TEMPLATE, booking=booking)

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.json
    if not data.get('privacy_consent'):
        return jsonify({"error": "Consenso privacy obbligatorio"}), 400

    booking_id = f"OCT-{random.randint(1000, 9999)}"
    adults = int(data.get('adults', 1))
    kids = int(data.get('kids', 0))
    total_price = (adults * 10.0) + (kids * 5.0)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bookings (id, name, email, phone, adults, kids, total_price, privacy_consent, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
    ''', (booking_id, data.get('name'), data.get('email'), data.get('phone'), adults, kids, total_price, data.get('notes', '')))
    conn.commit()
    conn.close()
    
    return jsonify({
        "success": True,
        "booking_id": booking_id,
        "total_price": total_price
    }), 201

@app.route('/api/bookings/<booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/bookings/<booking_id>/checkin', methods=['POST'])
def toggle_checkin(booking_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM bookings WHERE id = ?", (booking_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Non trovato"}), 404
        
    new_status = 'checked_in' if row[0] != 'checked_in' else 'confirmed'
    cursor.execute("UPDATE bookings SET status = ? WHERE id = ?", (new_status, booking_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "new_status": new_status})

@app.route('/api/admin/verify-pin', methods=['POST'])
def verify_pin():
    pin_input = request.json.get('pin')
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'admin_pin'")
    saved_pin = cursor.fetchone()[0]
    conn.close()
    return jsonify({"valid": pin_input == saved_pin})

init_db()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)