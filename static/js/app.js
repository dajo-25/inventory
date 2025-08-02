let currentView = 'objects';
let editingId = null;

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('btn-toggle').addEventListener('click', toggleView);
    document.getElementById('btn-add').addEventListener('click', () => openForm());
    document.getElementById('search').addEventListener('input', loadList);
    document.getElementById('submit').addEventListener('click', submitForm);
    document.getElementById('delete').addEventListener('click', () => {
        if (editingId && confirm('¿Eliminar elemento?')) {
            api(`${currentView}/${editingId}`, 'DELETE')
                .then(() => { closeForm(); loadList(); })
                .catch(console.error);
        }
    });
    document.getElementById('close').addEventListener('click', closeForm);
    loadList();
});

function toggleView() {
    currentView = currentView === 'objects' ? 'containers' : 'objects';
    document.getElementById('btn-toggle').textContent =
        currentView === 'objects' ? 'Ver Contenedores' : 'Ver Objetos';
    document.getElementById('title').textContent =
        currentView === 'objects' ? 'Objetos' : 'Contenedores';
    loadList();
}

function api(path, method = 'GET', body) {
    return fetch(`/api/${path}`, {
        method,
        headers: body ? { 'Content-Type': 'application/json' } : {},
        body: body ? JSON.stringify(body) : null
    }).then(res => {
        if (!res.ok && res.status !== 204) throw new Error('API error');
        return res.status === 204 ? null : res.json();
    });
}

function loadList() {
    const q = document.getElementById('search').value;
    api(`\${currentView}?q=\${encodeURIComponent(q)}`)
        .then(items => renderList(items))
        .catch(console.error);
}

function renderList(items) {
    const listEl = document.getElementById('list');
    listEl.innerHTML = '';
    items.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item.nombre;
        li.onclick = () => openForm(item.id);
        listEl.appendChild(li);
    });
}

function openForm(id) {
    editingId = id;
    const form = document.getElementById('form');
    form.style.display = 'block';
    if (id) {
        api(`${currentView}/${id}`)
            .then(data => fillForm(data))
            .catch(console.error);
    } else {
        fillForm({ nombre: '', descripcion: '', cantidad: 1, categoria: '', subcategoria: '', almacenado_en: '' });
    }
}

function fillForm(data) {
    document.getElementById('nombre').value = data.nombre || '';
    document.getElementById('descripcion').value = data.descripcion || '';
    document.getElementById('cantidad').value = data.cantidad || '';
    document.getElementById('categoria').value = data.categoria || '';
    document.getElementById('subcategoria').value = data.subcategoria || '';
    document.getElementById('almacenado_en').value = data.almacenado_en || '';
    document.getElementById('submit').textContent = editingId ? 'Actualizar' : 'Crear';
    document.getElementById('delete').style.display = editingId ? 'inline-block' : 'none';
}

function closeForm() {
    document.getElementById('form').style.display = 'none';
    editingId = null;
}

function submitForm() {
    const data = {
        nombre: document.getElementById('nombre').value,
        descripcion: document.getElementById('descripcion').value,
        cantidad: currentView === 'objects' ? parseInt(document.getElementById('cantidad').value) || 1 : undefined,
        categoria: document.getElementById('categoria').value,
        subcategoria: document.getElementById('subcategoria').value,
        almacenado_en: document.getElementById('almacenado_en').value
    };
    if (currentView === 'containers') {
        delete data.cantidad;
        delete data.categoria;
        delete data.subcategoria;
        delete data.almacenado_en;
    }
    const endpoint = currentView;
    const action = editingId ? api(`${endpoint}/${editingId}`, 'PUT', data) : api(endpoint, 'POST', data);
    action.then(() => { closeForm(); loadList(); }).catch(console.error);
}