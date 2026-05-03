// UHR Frontend Logic - Phase 9

document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-links li');
    const views = document.querySelectorAll('.view');

    // Simple View Router
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const targetView = link.getAttribute('data-view');
            
            // Update Active Link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Switch Visibility
            views.forEach(view => {
                view.classList.remove('active');
                if (view.id === `${targetView}-view`) {
                    view.classList.add('active');
                }
            });

            // Simulate Data Load for certain views
            if (targetView === 'ingest') {
                renderIngestView();
            }
        });
    });
});

function renderIngestView() {
    const container = document.getElementById('view-container');
    // For simplicity, we just inject HTML here in the prototype
    const html = `
        <section id="ingest-view" class="view active fade-in">
            <h1>Unified Data Ingestion</h1>
            <p style="color: var(--text-dim); margin-bottom: 2rem;">Upload legacy hospital data (CSV/HL7) to normalize and push to FHIR R4.</p>
            
            <div class="drop-zone" id="drop-zone">
                <i data-lucide="upload-cloud" style="width: 48px; height: 48px; color: var(--primary); margin-bottom: 1rem;"></i>
                <p>Drag and drop your clinical data here</p>
                <span>Supported: .csv, .hl7, .json</span>
                <input type="file" id="file-input" hidden>
                <button class="btn-primary" style="margin-top: 1.5rem;" onclick="document.getElementById('file-input').click()">Browse Files</button>
            </div>

            <div id="upload-status" style="margin-top: 2rem;"></div>
        </section>
    `;
    
    // Check if view already exists or replace
    const existing = document.getElementById('ingest-view');
    if (!existing) {
        container.insertAdjacentHTML('beforeend', html);
        lucide.createIcons();
    }
}

// Simulated API Calls
async function loginDoctor(username, password) {
    try {
        const response = await fetch('/token', {
            method: 'POST',
            body: new URLSearchParams({ username, password })
        });
        return await response.json();
    } catch (e) {
        console.error("Login failed", e);
    }
}
