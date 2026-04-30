const PORT = 5500;

const MODEL_SERVER_URL = "http://localhost:8000/predict";
const http = require('http');
const url  = require('url');

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin',  '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.method !== 'POST' || url.parse(req.url).pathname !== '/analyze') {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Endpoint tidak ditemukan. Gunakan POST /analyze' }));
    return;
  }

  let body = '';
  req.on('data', chunk => { body += chunk.toString(); });

  req.on('end', () => {
    let parsedBody;
    try {
      parsedBody = JSON.parse(body);
    } catch (e) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Body harus berupa JSON yang valid.' }));
      return;
    }

    if (!parsedBody.inputs) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Field "inputs" wajib ada di dalam body.' }));
      return;
    }

    const bodyString = JSON.stringify(parsedBody);

    console.log('\n─────────────────────────────────────────');
    console.log(`[${new Date().toLocaleTimeString()}] Request dari browser`);
    console.log('→ Meneruskan ke model server lokal...');

    console.log('\n══════════ FULL BODY DIKIRIM KE MODEL ══════════');
    console.log('JD:\n',           parsedBody.inputs?.jd         || '(kosong)');
    console.log('\nREQ:\n',        parsedBody.inputs?.req         || '(kosong)');
    console.log('\nPROFILE_TEXT:\n', parsedBody.inputs?.profile_text || '(kosong)');
    console.log('\nPROFILE (structured):\n', JSON.stringify(parsedBody.inputs?.profile, null, 2));
    console.log('═════════════════════════════════════════════════\n');

    const modelUrl = new url.URL(MODEL_SERVER_URL);
    const options  = {
      hostname: modelUrl.hostname,
      port:     modelUrl.port || 8000,
      path:     modelUrl.pathname,
      method:   'POST',
      headers: {
        'Content-Type':   'application/json',
        'Content-Length': Buffer.byteLength(bodyString),
      },
    };

    const modelReq = http.request(options, (modelRes) => {
      let responseData = '';
      modelRes.on('data', chunk => { responseData += chunk; });

      modelRes.on('end', () => {
        console.log(`← Response dari model: HTTP ${modelRes.statusCode}`);

        res.writeHead(modelRes.statusCode, {
          'Content-Type':                'application/json',
          'Access-Control-Allow-Origin': '*',
        });
        res.end(responseData);

        if (modelRes.statusCode === 200) {
          console.log('✅ Berhasil — response dikirim ke browser');
        } else {
          console.log(`⚠️  Error ${modelRes.statusCode}: ${responseData.slice(0, 120)}`);
        }
      });
    });

    modelReq.on('error', (err) => {
      console.error('❌ Gagal terhubung ke model server:', err.message);
      console.error('   Pastikan model_server.py sudah dijalankan: python model_server.py');
      res.writeHead(502, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        error: `Proxy gagal menghubungi model server: ${err.message}`,
        hint:  'Pastikan model_server.py sudah berjalan di port 8000.'
      }));
    });

    modelReq.write(bodyString);
    modelReq.end();
  });
});

server.listen(PORT, () => {
  console.log('╔════════════════════════════════════════════════╗');
  console.log('║         FitScore Proxy — AKTIF ✅              ║');
  console.log('╠════════════════════════════════════════════════╣');
  console.log(`║  Port proxy   : http://localhost:${PORT}        ║`);
  console.log(`║  Model server : ${MODEL_SERVER_URL}  ║`);
  console.log(`║  Endpoint     : POST /analyze                  ║`);
  console.log('╠════════════════════════════════════════════════╣');
  console.log('║  Pastikan model_server.py sudah jalan dulu!    ║');
  console.log('║  Untuk berhenti: tekan Ctrl+C                  ║');
  console.log('╚════════════════════════════════════════════════╝');
});

process.on('SIGINT', () => {
  console.log('\n\nProxy dihentikan. Sampai jumpa! 👋');
  process.exit(0);
});