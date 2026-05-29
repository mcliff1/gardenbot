/* Gardenbot – Yards page JavaScript */

let currentYardId = null;
let fabricCanvas = null;

// Scale: pixels per foot
const SCALE = 8;

// Colors for area types
const AREA_COLORS = {
    flower_bed: '#ff9ff3',
    shrub_bed: '#2ed573',
    tree_area: '#1e8449',
    garden: '#f39c12',
    lawn: '#7dcea0',
    rock_gravel: '#bdc3c7',
    patio: '#d4a574',
    walkway: '#95a5a6',
    driveway: '#7f8c8d',
    water_feature: '#74b9ff',
    utility: '#fdcb6e',
    other: '#dfe6e9',
};

const STRUCTURE_COLOR = '#5a6c7d';

// --- Page Load ---
document.addEventListener('DOMContentLoaded', loadYards);

async function loadYards() {
    const container = document.getElementById('yard-list');
    try {
        const resp = await fetch('/yards/');
        const yards = await resp.json();
        if (yards.length === 0) {
            container.innerHTML = '<p class="loading">No yards defined yet. Create one to get started!</p>';
            return;
        }
        container.innerHTML = yards.map(yard => `
            <div class="card" onclick="openYard('${yard.id}')">
                <h3>${escapeHtml(yard.name)}</h3>
                <p>${yard.origin_description || 'No origin set'} · ${yard.areas.length} area(s) · ${yard.structures.length} structure(s)</p>
            </div>
        `).join('');
    } catch (e) {
        container.innerHTML = '<p class="loading">Error loading yards.</p>';
    }
}

// --- Create Yard ---
function showCreateForm() {
    document.getElementById('create-form').style.display = 'block';
}

function hideCreateForm() {
    document.getElementById('create-form').style.display = 'none';
}

async function createYard(event) {
    event.preventDefault();
    const name = document.getElementById('yard-name').value;
    const origin = document.getElementById('yard-origin').value;
    const width = parseFloat(document.getElementById('yard-width').value);
    const depth = parseFloat(document.getElementById('yard-depth').value);

    const boundary = [
        { x: 0, y: 0 },
        { x: width, y: 0 },
        { x: width, y: depth },
        { x: 0, y: depth },
    ];

    const resp = await fetch('/yards/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, boundary, origin_description: origin }),
    });

    if (resp.ok) {
        hideCreateForm();
        document.getElementById('yard-form').reset();
        loadYards();
    } else {
        alert('Error creating yard');
    }
}

// --- Yard Detail ---
async function openYard(yardId) {
    currentYardId = yardId;
    document.getElementById('yard-list').style.display = 'none';
    document.getElementById('create-form').style.display = 'none';
    document.querySelector('.page-header').style.display = 'none';
    document.getElementById('yard-detail').style.display = 'block';

    const resp = await fetch(`/yards/${yardId}`);
    const yard = await resp.json();

    document.getElementById('yard-detail-name').textContent = yard.name;
    document.getElementById('yard-detail-origin').textContent = yard.origin_description || 'No origin';
    document.getElementById('yard-detail-areas').textContent = `${yard.areas.length} area(s)`;
    document.getElementById('yard-detail-structures').textContent = `${yard.structures.length} structure(s)`;

    renderCanvas(yard);
    renderPanels(yard);
    loadProposals(yardId);
}

function closeDetail() {
    document.getElementById('yard-detail').style.display = 'none';
    document.getElementById('yard-list').style.display = 'flex';
    document.querySelector('.page-header').style.display = 'flex';
    currentYardId = null;
    if (fabricCanvas) {
        fabricCanvas.dispose();
        fabricCanvas = null;
    }
    loadYards();
}

// --- Canvas Rendering ---
function renderCanvas(yard) {
    const canvasEl = document.getElementById('yard-canvas');

    // Calculate canvas size from boundary
    let maxX = 0, maxY = 0;
    yard.boundary.forEach(pt => {
        if (pt.x > maxX) maxX = pt.x;
        if (pt.y > maxY) maxY = pt.y;
    });

    const width = maxX * SCALE + 40;
    const height = maxY * SCALE + 40;
    canvasEl.width = width;
    canvasEl.height = height;

    if (fabricCanvas) fabricCanvas.dispose();
    fabricCanvas = new fabric.Canvas('yard-canvas', {
        selection: false,
        backgroundColor: '#f0f7f0',
    });
    fabricCanvas.setWidth(width);
    fabricCanvas.setHeight(height);

    // Draw boundary
    const boundaryPoints = yard.boundary.map(pt => ({
        x: pt.x * SCALE + 20,
        y: pt.y * SCALE + 20,
    }));
    const boundaryPoly = new fabric.Polygon(boundaryPoints, {
        fill: 'rgba(255,255,255,0.3)',
        stroke: '#333',
        strokeWidth: 2,
        selectable: false,
        evented: false,
    });
    fabricCanvas.add(boundaryPoly);

    // Draw areas
    yard.areas.forEach(area => {
        const points = area.shape.map(pt => ({
            x: pt.x * SCALE + 20,
            y: pt.y * SCALE + 20,
        }));
        const color = AREA_COLORS[area.type] || AREA_COLORS.other;
        const poly = new fabric.Polygon(points, {
            fill: color + '80',
            stroke: color,
            strokeWidth: 1.5,
            selectable: false,
            evented: true,
        });
        // Tooltip on hover
        poly.on('mouseover', () => {
            poly.set('strokeWidth', 3);
            fabricCanvas.renderAll();
        });
        poly.on('mouseout', () => {
            poly.set('strokeWidth', 1.5);
            fabricCanvas.renderAll();
        });
        fabricCanvas.add(poly);

        // Label
        const center = getPolygonCenter(points);
        const label = new fabric.Text(area.name, {
            left: center.x,
            top: center.y,
            fontSize: 11,
            fill: '#333',
            originX: 'center',
            originY: 'center',
            selectable: false,
            evented: false,
        });
        fabricCanvas.add(label);
    });

    // Draw structures
    yard.structures.forEach(structure => {
        const points = structure.footprint.map(pt => ({
            x: pt.x * SCALE + 20,
            y: pt.y * SCALE + 20,
        }));
        const poly = new fabric.Polygon(points, {
            fill: STRUCTURE_COLOR + '60',
            stroke: STRUCTURE_COLOR,
            strokeWidth: 2,
            selectable: false,
            evented: true,
        });
        fabricCanvas.add(poly);

        const center = getPolygonCenter(points);
        const label = new fabric.Text(structure.name, {
            left: center.x,
            top: center.y,
            fontSize: 11,
            fill: '#fff',
            fontWeight: 'bold',
            originX: 'center',
            originY: 'center',
            selectable: false,
            evented: false,
        });
        fabricCanvas.add(label);
    });

    fabricCanvas.renderAll();
}

function getPolygonCenter(points) {
    const n = points.length;
    const sum = points.reduce((acc, pt) => ({ x: acc.x + pt.x, y: acc.y + pt.y }), { x: 0, y: 0 });
    return { x: sum.x / n, y: sum.y / n };
}

// --- Panels ---
function renderPanels(yard) {
    const areasEl = document.getElementById('areas-list');
    const structsEl = document.getElementById('structures-list');

    areasEl.innerHTML = yard.areas.length === 0
        ? '<p class="loading">No areas defined</p>'
        : yard.areas.map(a => `
            <div class="panel-item">
                <strong>${escapeHtml(a.name)}</strong>
                <span class="badge badge-muted">${a.type}</span>
                ${a.sun_exposure ? `<span class="badge">${a.sun_exposure}</span>` : ''}
            </div>
        `).join('');

    structsEl.innerHTML = yard.structures.length === 0
        ? '<p class="loading">No structures defined</p>'
        : yard.structures.map(s => `
            <div class="panel-item">
                <strong>${escapeHtml(s.name)}</strong>
                <span class="badge badge-muted">${s.type}</span>
            </div>
        `).join('');
}

// --- Proposals ---
async function loadProposals(yardId) {
    const el = document.getElementById('proposals-list');
    try {
        const resp = await fetch(`/yards/${yardId}/proposals/`);
        const proposals = await resp.json();
        el.innerHTML = proposals.length === 0
            ? '<p class="loading">No proposals yet</p>'
            : proposals.map(p => `
                <div class="panel-item">
                    <strong>${escapeHtml(p.name)}</strong>
                    <span class="badge">${p.state}</span>
                </div>
            `).join('');
    } catch {
        el.innerHTML = '<p class="loading">Error loading proposals</p>';
    }
}

async function createProposal() {
    if (!currentYardId) return;
    const name = prompt('Proposal name:');
    if (!name) return;

    const resp = await fetch(`/yards/${currentYardId}/proposals/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
    });

    if (resp.ok) {
        loadProposals(currentYardId);
    }
}

// --- Utilities ---
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
