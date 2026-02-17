const API_BASE_URL = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', () => {
    console.log("EduTrack Elite Initializing...");

    try {
        initializeSystem();
        initTabNavigation();
        bindAttendanceEvents();
        bindMarksEvents();
        bindExcelEvents();
        initDashboardAnimations();
    } catch (error) {
        console.error("Critical Initialization Error:", error);
    }
});

function initializeSystem() {
    refreshDashboard();
    loadAttendanceTable();
    updateSystemDate();
    populateMarksDropdown();
    loadWhatsAppLogs();
}

function bindAttendanceEvents() {
    const markBtn = document.getElementById('mark-attendance-btn');
    const modal = document.getElementById('attendance-modal');
    const closeBtn = document.querySelector('.close');
    const saveBtn = document.getElementById('save-attendance-btn');

    if (markBtn) markBtn.onclick = () => modal.style.display = 'block';
    if (closeBtn) closeBtn.onclick = () => modal.style.display = 'none';
    window.onclick = (e) => { if (e.target == modal) modal.style.display = 'none'; };

    // Toggle reason field
    const statusRadios = document.getElementsByName('status');
    statusRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            document.getElementById('reason-field').style.display =
                radio.value === 'Absent' ? 'block' : 'none';
        });
    });

    if (saveBtn) {
        saveBtn.onclick = () => {
            const sid = document.getElementById('modal-student-select').value;
            const status = document.querySelector('input[name="status"]:checked').value;

            // Find and update the local record
            const record = attendanceData.find(r => r.id === sid);
            if (record) {
                record.status = status;
                loadAttendanceTable(); // Refresh table

                // JARVIS Simulation
                saveBtn.innerHTML = "⌛ Syncing...";
                saveBtn.disabled = true;

                setTimeout(() => {
                    alert(`🚀 JARVIS: Attendance for ${record.name} updated to ${status}. parent notified.`);
                    saveBtn.innerHTML = "Save & Notify Parent";
                    saveBtn.disabled = false;
                    modal.style.display = 'none';
                    refreshDashboard();
                }, 1000);
            }
        };
    }
}

function initDashboardAnimations() {
    // Animate analytics bars on load
    const bars = document.querySelectorAll('.bar-fill');
    bars.forEach(bar => {
        const targetHeight = bar.style.height;
        bar.style.height = '0';
        setTimeout(() => {
            bar.style.height = targetHeight;
        }, 300);
    });
}

function initTabNavigation() {
    const navItems = document.querySelectorAll('.sidebar nav li');
    const tabPanes = document.querySelectorAll('.tab-pane');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabId = item.getAttribute('data-tab');
            if (!tabId) return;

            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            tabPanes.forEach(pane => {
                pane.classList.remove('active');
                if (pane.id === `${tabId}-tab`) {
                    pane.classList.add('active');
                }
            });

            if (tabId === 'dashboard') refreshDashboard();
            if (tabId === 'marks') updateMessagePreview();
        });
    });
}

/**
 * Marks & Notification Preview Logic
 */
/**
 * Marks & Notification Preview Logic
 */
function bindMarksEvents() {
    const saveMarksBtn = document.getElementById('save-marks-btn');
    const previewBtn = document.getElementById('preview-msg-btn');
    const inputs = ['marks-student-select', 'marks-subject', 'marks-exam', 'marks-value'];

    // Update preview on any input change
    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        ['input', 'change', 'keyup'].forEach(evt => {
            el.addEventListener(evt, updateMessagePreview);
        });
    });

    if (previewBtn) {
        previewBtn.onclick = () => {
            updateMessagePreview();
            const bubble = document.querySelector('.whatsapp-bubble');
            bubble.style.transform = 'scale(1.02)';
            setTimeout(() => bubble.style.transform = 'scale(1)', 200);
        };
    }

    if (saveMarksBtn) {
        saveMarksBtn.onclick = async () => {
            const studentId = document.getElementById('marks-student-select').value;
            if (!studentId || studentId.includes("Select")) {
                alert("JARVIS: Please select a valid student record first.");
                document.getElementById('marks-student-select').focus();
                return;
            }

            // Verify if all data is present
            const subject = document.getElementById('marks-subject').value;
            const marks = document.getElementById('marks-value').value;
            if (!subject || !marks) {
                alert("JARVIS: Subject and Performance Score are required for dispatch.");
                return;
            }

            // Simulation of JARVIS sending
            saveMarksBtn.innerHTML = "📡 JARVIS: Protocol Active...";
            saveMarksBtn.disabled = true;

            setTimeout(() => {
                alert(`🚀 PROTOCOL SUCCESS: Official mark statement for Student ${studentId} dispatched to registered parent.\n\nStatus: Delivered ✓✓`);
                saveMarksBtn.innerHTML = "🚀 Send to Parent via JARVIS";
                saveMarksBtn.disabled = false;

                // Track in logs (simulated)
                console.log(`Dispatched: ${studentId} | ${subject} | ${marks}`);
                refreshDashboard();
            }, 1200);
        };
    }
}

function updateMessagePreview() {
    const previewBox = document.getElementById('whatsapp-preview-text');
    const timeBox = document.getElementById('bubble-time');
    const studentSelect = document.getElementById('marks-student-select');

    const studentName = studentSelect.options[studentSelect.selectedIndex]?.text.split(' - ')[1] || "Student";
    const subject = document.getElementById('marks-subject').value || "[Subject]";
    const exam = document.getElementById('marks-exam').value || "[Exam Type]";
    const marks = document.getElementById('marks-value').value || "--";

    const msg = `Dear Parent,\n\nThis is an official update from *EduTrack Elite*.\n\nYour ward *${studentName}* has secured *${marks}/100* in the *${exam}* assessment for the subject *${subject}*.\n\nPlease log in to the portal for a detailed performance report.\n\nRegards,\n*Administrator, EduTrack*`;

    previewBox.innerText = msg;

    // Update bubble time to current time
    const now = new Date();
    timeBox.innerText = now.getHours().toString().padStart(2, '0') + ":" + now.getMinutes().toString().padStart(2, '0');
}

/**
 * Excel Smart-Mapping Integration
 */
function bindExcelEvents() {
    const importBtn = document.getElementById('import-excel-btn');
    const fileInput = document.getElementById('excel-file-input');

    if (importBtn && fileInput) {
        console.log("JARVIS: Excel System Initialized.");
        importBtn.onclick = () => fileInput.click();

        fileInput.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;

            console.log(`JARVIS: File detected: ${file.name}`);
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const data = new Uint8Array(event.target.result);
                    if (typeof XLSX === 'undefined') {
                        throw new Error("Excel Library (SheetJS) not detected. Please refresh the page.");
                    }

                    const workbook = XLSX.read(data, { type: 'array' });
                    const sheetData = XLSX.utils.sheet_to_json(workbook.Sheets[workbook.SheetNames[0]]);

                    if (sheetData.length > 0) {
                        console.log(`JARVIS: Identified ${sheetData.length} records in Excel.`);
                        const count = processImportedData(sheetData);
                        updateMessagePreview();
                        alert(`EduTrack: Successfully processed ${sheetData.length} student records from sheet.`);
                    } else {
                        alert("JARVIS: The imported Excel sheet appears to be empty.");
                    }
                } catch (err) {
                    console.error("Excel Engine Error:", err);
                    alert("Excel Engine Error: " + err.message);
                }
                fileInput.value = ''; // Reset
            };
            reader.readAsArrayBuffer(file);
        };
    } else {
        console.error("JARVIS: Excel UI elements not found.");
    }
}

let bulkData = [];

function processImportedData(dataArray) {
    bulkData = [];
    const bulkBody = document.getElementById('bulk-marks-body');
    const bulkSection = document.getElementById('bulk-preview-section');
    bulkBody.innerHTML = '';

    let totalMapped = 0;

    const mappings = {
        studentId: ["id", "reg", "roll", "student", "number", "uid"],
        subject: ["sub", "course", "paper", "subject name"],
        marks: ["mark", "score", "value", "attained", "total"],
        examType: ["exam", "test", "assessment", "category"]
    };

    const smartFind = (dataRow, keys, purpose) => {
        const foundKey = Object.keys(dataRow).find(key =>
            keys.some(k => key.toLowerCase().includes(k.toLowerCase()))
        );
        if (foundKey) {
            console.log(`JARVIS: Mapped "${foundKey}" to "${purpose}"`);
            return dataRow[foundKey];
        }
        return null;
    };

    // Process all rows from Excel
    dataArray.forEach((row, index) => {
        let sid = smartFind(row, mappings.studentId, "Student ID");
        const sub = smartFind(row, mappings.subject, "Subject");
        const exam = smartFind(row, mappings.examType, "Exam");
        const val = smartFind(row, mappings.marks, "Score");

        // Fallback: If no sid found but we have data, use the first column
        if (!sid && Object.keys(row).length > 0) {
            sid = row[Object.keys(row)[0]];
            console.log(`JARVIS: No Student ID header found. Falling back to first column: "${Object.keys(row)[0]}"`);
        }

        if (sid) {
            const record = { sid, sub, exam, val, status: 'Pending' };
            bulkData.push(record);

            // Pre-fill the first record into the main form
            if (index === 0) {
                const sel = document.getElementById('marks-student-select');
                let exists = false;
                for (let i = 0; i < sel.options.length; i++) {
                    if (sel.options[i].value == sid) {
                        sel.selectedIndex = i;
                        exists = true;
                        break;
                    }
                }
                if (!exists) {
                    const o = document.createElement('option');
                    o.value = sid;
                    o.textContent = `${sid} - Imported Record`;
                    sel.appendChild(o);
                    sel.value = sid;
                }
                if (sub) document.getElementById('marks-subject').value = sub;
                if (exam) document.getElementById('marks-exam').value = exam;
                if (val) document.getElementById('marks-value').value = val;
                totalMapped = 4; // Approx
            }

            // Add to Bulk Table
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${sid}</td>
                <td>${sub || '-'}</td>
                <td>${exam || '-'}</td>
                <td>${val || '-'}</td>
                <td><span class="badge" style="background: rgba(255,255,255,0.1)">Ready</span></td>
            `;
            bulkBody.appendChild(tr);
        }
    });

    if (bulkData.length > 0) {
        bulkSection.style.display = 'block';
        bindBatchEvents();
    }

    return totalMapped;
}

function bindBatchEvents() {
    const dispatchAllBtn = document.getElementById('dispatch-all-btn');
    if (!dispatchAllBtn) return;

    dispatchAllBtn.onclick = async () => {
        if (!confirm(`JARVIS: Proceed with batch dispatch of ${bulkData.length} records?`)) return;

        dispatchAllBtn.disabled = true;
        dispatchAllBtn.innerHTML = "📡 Batch Processing...";

        const rows = document.querySelectorAll('#bulk-marks-body tr');

        for (let i = 0; i < bulkData.length; i++) {
            const row = rows[i];
            const statusCell = row.cells[4];
            statusCell.innerHTML = '<span class="badge" style="color: var(--warning)">Sending...</span>';

            // Simulating API call for each (in real app, use a batch endpoint)
            await new Promise(r => setTimeout(r, 600));

            statusCell.innerHTML = '<span class="badge present">Sent</span>';
            row.style.background = 'rgba(34, 197, 94, 0.05)';
        }

        alert(`🚀 BATCH DISPATCH COMPLETE: All ${bulkData.length} records processed by JARVIS Protocol.`);
        dispatchAllBtn.innerHTML = "✅ Batch Dispatched";
        refreshDashboard();
    };
}

/**
 * Dashboard & Tables
 */
async function refreshDashboard() {
    // Elite scale simulation
    document.getElementById('total-students').textContent = '1,240';
    document.getElementById('avg-attendance-pct').textContent = '94.2%';
    document.getElementById('low-att-count').textContent = '12';
    document.getElementById('pending-alerts').textContent = '8';

    // Re-trigger bar animations
    const bars = document.querySelectorAll('.bar-fill');
    bars.forEach(bar => {
        const h = bar.style.height;
        bar.style.height = '0';
        setTimeout(() => bar.style.height = h, 100);
    });
}

let attendanceData = [
    { id: "2024CS001", name: "ARUN KUMAR", status: "Present" },
    { id: "2024CS002", name: "DEEPA S", status: "Present" },
    { id: "2024EC045", name: "JOHN DOE", status: "Absent" }
];

async function loadAttendanceTable() {
    const body = document.getElementById('attendance-table-body');
    if (!body) return;

    body.innerHTML = attendanceData.map(record => `
        <tr data-sid="${record.id}">
            <td>${record.id}</td>
            <td>${record.name}</td>
            <td><span class="badge ${record.status.toLowerCase()}">${record.status}</span></td>
            <td><button class="btn-text edit-attn-btn">Edit</button></td>
        </tr>
    `).join('');

    // Bind Edit Buttons
    document.querySelectorAll('.edit-attn-btn').forEach((btn, index) => {
        btn.onclick = () => {
            const record = attendanceData[index];
            const modal = document.getElementById('attendance-modal');
            const sel = document.getElementById('modal-student-select');

            sel.value = record.id;
            // Set radio button status
            document.querySelector(`input[name="status"][value="${record.status}"]`).checked = true;
            document.getElementById('reason-field').style.display = (record.status === 'Absent' ? 'block' : 'none');

            modal.style.display = 'block';
        };
    });
}

function updateSystemDate() {
    const d = document.getElementById('current-date');
    if (d) d.textContent = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
}

async function populateMarksDropdown() {
    const marksSel = document.getElementById('marks-student-select');
    const modalSel = document.getElementById('modal-student-select');
    const students = [
        { id: "2024CS001", name: "ARUN KUMAR" },
        { id: "2024CS002", name: "DEEPA S" },
        { id: "2024EC045", name: "JOHN DOE" }
    ];

    const options = `
        <option value="">Select Student...</option>
        ${students.map(s => `<option value="${s.id}">${s.id} - ${s.name}</option>`).join('')}
    `;

    if (marksSel) marksSel.innerHTML = options;
    if (modalSel) modalSel.innerHTML = options;
}

function loadWhatsAppLogs() {
    const body = document.querySelector('#notifications-tab .data-table tbody');
    if (!body) return;
    body.innerHTML = `
        <tr><td>Today, 10:15</td><td>ARUN'S PARENT</td><td>INTERNAL-1</td><td><span class="badge present">DELIVERED</span></td></tr>
        <tr><td>Today, 11:30</td><td>JOHN'S PARENT</td><td>ABSENCE</td><td><span class="badge present">READ</span></td></tr>
        <tr><td>Yesterday</td><td>DEEPA'S PARENT</td><td>UNIT TEST</td><td><span class="badge present">SENT</span></td></tr>
    `;
}
