function api(path, opts) {
    return fetch(path, {
        headers: { 'Content-Type': 'application/json' },
        ...opts
    }).then(r => r.ok ? r.json() : Promise.reject(r));
}

document.addEventListener('DOMContentLoaded', () => {
    const bodyId = document.body.id;
    if (bodyId === 'objects-list') initList('objects');
    if (bodyId === 'containers-list') initList('containers');
    if (bodyId === 'object-detail') initDetail('objects');
    if (bodyId === 'container-detail') initDetail('containers');
});

function initList(type) {
    const listEl = document.getElementById('items');
    const searchEl = document.getElementById('search');
    const addBtn = document.getElementById('add');

    function load(q = '') {
        api(`/api/${type}?q=${encodeURIComponent(q)}`)
            .then(data => {
                listEl.innerHTML = '';
                data.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = item.name;
                    li.onclick = () => window.location = `${type.slice(0, -1)}_detail.html?id=${item.id}`;
                    listEl.appendChild(li);
                });
            });
    }

    searchEl.oninput = () => load(searchEl.value);
    addBtn.onclick = () => window.location = `${type.slice(0, -1)}_detail.html`;
    load();
}

function initDetail(type) {
    const form = document.getElementById('item-form');
    const params = new URLSearchParams(location.search);
    const id = params.get('id');
    if (id) {
        api(`/api/${type}/${id}`).then(data => {
            Object.entries(data).forEach(([k, v]) => {
                form.elements[k]?.value = v;
            });
        });
    }

    form.onsubmit = e => {
        e.preventDefault();
        const data = {};
        Array.from(form.elements).forEach(el => {
            if (el.name) data[el.name] = el.value;
        });
        const op = id ? api(`/api/${type}/${id}`, { method: 'PUT', body: JSON.stringify(data) })
            : api(`/api/${type}`, { method: 'POST', body: JSON.stringify(data) });
        op.then(() => window.location = `${type}_list.html`);
    };
}