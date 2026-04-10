const apiBase = '../app/api.php';

function makeTitleInputs() {
  const grid = document.getElementById('titles-grid');
  for (let i = 1; i <= 10; i++) {
    const input = document.createElement('input');
    input.placeholder = `Judul ${i}`;
    input.id = `title-${i}`;
    grid.appendChild(input);
  }
}

function collectTitles() {
  const values = [];
  for (let i = 1; i <= 10; i++) {
    values.push(document.getElementById(`title-${i}`).value.trim());
  }
  return values;
}

async function callApi(action, method = 'GET', body = null) {
  const options = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) options.body = JSON.stringify(body);
  const res = await fetch(`${apiBase}?action=${action}`, options);
  const data = await res.json();
  if (!res.ok) throw new Error(data.message || 'API error');
  return data;
}

function setStatus(text) {
  document.getElementById('statusBox').textContent = text;
}

function renderHistory(history) {
  const box = document.getElementById('historyBox');
  if (!history || history.length === 0) {
    box.textContent = 'Belum ada data.';
    return;
  }

  box.innerHTML = history.map((run) => {
    const errors = (run.errors || []).length;
    return `
      <div class="history-item">
        <strong>${run.run_id}</strong><br>
        Status: ${run.status}<br>
        Timestamp: ${run.started_at}<br>
        Error count: ${errors}
      </div>
    `;
  }).join('');
}

async function refreshStatus() {
  try {
    const data = await callApi('status');
    renderHistory(data.history);
    if (data.latest_run) {
      setStatus(JSON.stringify(data.latest_run, null, 2));
    }
  } catch (err) {
    setStatus(err.message);
  }
}

document.getElementById('saveBtn').addEventListener('click', async () => {
  try {
    const titles = collectTitles();
    const data = await callApi('save_titles', 'POST', { titles });
    setStatus(JSON.stringify(data, null, 2));
  } catch (err) {
    setStatus(`Gagal simpan judul: ${err.message}`);
  }
});

document.getElementById('generateBtn').addEventListener('click', async () => {
  try {
    setStatus('Menjalankan automation... mohon tunggu.');
    const data = await callApi('start_generate', 'POST', {});
    setStatus(JSON.stringify(data, null, 2));
    await refreshStatus();
  } catch (err) {
    setStatus(`Generate error: ${err.message}`);
  }
});

document.getElementById('viewResultBtn').addEventListener('click', async () => {
  try {
    const data = await callApi('view_result');
    document.getElementById('resultBox').textContent = data.content || '(kosong)';
  } catch (err) {
    document.getElementById('resultBox').textContent = `Gagal ambil hasil: ${err.message}`;
  }
});

document.getElementById('downloadTxtBtn').addEventListener('click', () => {
  window.location.href = `${apiBase}?action=download_output&format=txt`;
});

document.getElementById('downloadHtmlBtn').addEventListener('click', () => {
  window.location.href = `${apiBase}?action=download_output&format=html`;
});

makeTitleInputs();
refreshStatus();
