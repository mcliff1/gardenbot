/* Gardenbot – Plants page JavaScript */

document.addEventListener('DOMContentLoaded', loadPlants);

let allPlants = [];

async function loadPlants() {
    const container = document.getElementById('plant-list');
    try {
        const resp = await fetch('/plants/');
        allPlants = await resp.json();
        renderPlants(allPlants);
    } catch (e) {
        container.innerHTML = '<p class="loading">Error loading plants.</p>';
    }
}

function renderPlants(plants) {
    const container = document.getElementById('plant-list');
    if (plants.length === 0) {
        container.innerHTML = '<p class="loading">No plants in database yet. Add one to get started!</p>';
        return;
    }
    container.innerHTML = plants.map(plant => `
        <div class="card">
            <h3>${escapeHtml(plant.common_name)}</h3>
            <p>
                ${plant.botanical_name ? `<em>${escapeHtml(plant.botanical_name)}</em> · ` : ''}
                ${plant.perennial ? 'Perennial' : 'Annual'}
                ${plant.bloom_time ? ` · Blooms: ${escapeHtml(plant.bloom_time)}` : ''}
                ${plant.color ? ` · ${escapeHtml(plant.color)}` : ''}
                ${plant.mature_size_ft ? ` · ${plant.mature_size_ft}ft mature` : ''}
            </p>
            ${plant.care_notes ? `<p style="font-size:0.85rem; color: var(--color-text-muted)">${escapeHtml(plant.care_notes)}</p>` : ''}
        </div>
    `).join('');
}

function searchPlants(query) {
    if (!query.trim()) {
        renderPlants(allPlants);
        return;
    }
    const q = query.toLowerCase();
    const filtered = allPlants.filter(p =>
        p.common_name.toLowerCase().includes(q) ||
        p.botanical_name.toLowerCase().includes(q) ||
        p.color.toLowerCase().includes(q)
    );
    renderPlants(filtered);
}

// --- Create Plant ---
function showCreatePlant() {
    document.getElementById('create-plant-form').style.display = 'block';
}

function hideCreatePlant() {
    document.getElementById('create-plant-form').style.display = 'none';
}

async function createPlant(event) {
    event.preventDefault();
    const body = {
        common_name: document.getElementById('plant-common').value,
        botanical_name: document.getElementById('plant-botanical').value,
        perennial: document.getElementById('plant-type').value === 'true',
        bloom_time: document.getElementById('plant-bloom').value,
        mature_size_ft: parseFloat(document.getElementById('plant-size').value) || null,
        color: document.getElementById('plant-color').value,
        care_notes: document.getElementById('plant-care').value,
    };

    const resp = await fetch('/plants/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });

    if (resp.ok) {
        hideCreatePlant();
        document.getElementById('plant-form').reset();
        loadPlants();
    } else {
        alert('Error adding plant');
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
