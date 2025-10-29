const express = require('express');
const WebSocket = require('ws');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 4321;
const JWT_SECRET = 'oranolio-secret-key-2024';

// Middleware
app.use(cors());
app.use(express.json());

// Database setup
const db = new sqlite3.Database(':memory:'); // Using in-memory database for simplicity

// Initialize database tables
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    type TEXT,
    external_ip TEXT,
    internal_ip TEXT,
    computer TEXT,
    user TEXT,
    os TEXT,
    process TEXT,
    last_seen DATETIME,
    status TEXT
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS listeners (
    name TEXT PRIMARY KEY,
    type TEXT,
    protocol TEXT,
    host TEXT,
    port INTEGER,
    status TEXT
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    agent_id TEXT,
    command TEXT,
    status TEXT,
    output TEXT,
    created_at DATETIME
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS downloads (
    id TEXT PRIMARY KEY,
    filename TEXT,
    size INTEGER,
    agent_id TEXT,
    status TEXT,
    content BLOB
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS screenshots (
    id TEXT PRIMARY KEY,
    agent_id TEXT,
    content BLOB,
    timestamp DATETIME
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS credentials (
    id TEXT PRIMARY KEY,
    username TEXT,
    password TEXT,
    domain TEXT,
    type TEXT,
    host TEXT
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS targets (
    id TEXT PRIMARY KEY,
    computer TEXT,
    domain TEXT,
    address TEXT,
    os TEXT,
    alive BOOLEAN
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS tunnels (
    id TEXT PRIMARY KEY,
    type TEXT,
    local_host TEXT,
    local_port INTEGER,
    remote_host TEXT,
    remote_port INTEGER,
    status TEXT
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS chat_messages (
    id TEXT PRIMARY KEY,
    username TEXT,
    content TEXT,
    type TEXT,
    timestamp DATETIME
  )`);

  // Insert default listener
  db.run(`INSERT OR IGNORE INTO listeners (name, type, protocol, host, port, status) 
          VALUES ('default-http', 'beacon_http', 'http', '0.0.0.0', 8080, 'active')`);
});

// WebSocket server
const wss = new WebSocket.Server({ port: 8080 });
const clients = new Set();

wss.on('connection', (ws) => {
  clients.add(ws);
  console.log('WebSocket client connected');

  // Send initial data
  sendInitialData(ws);

  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      handleWebSocketMessage(ws, data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  });

  ws.on('close', () => {
    clients.delete(ws);
    console.log('WebSocket client disconnected');
  });
});

function sendInitialData(ws) {
  const data = {
    type: 'sync_data',
    agents: [],
    listeners: [],
    tasks: [],
    downloads: [],
    screenshots: [],
    credentials: [],
    targets: [],
    tunnels: [],
    chat: []
  };

  // Get all data from database
  db.all('SELECT * FROM agents', (err, rows) => {
    if (!err) data.agents = rows;
  });

  db.all('SELECT * FROM listeners', (err, rows) => {
    if (!err) data.listeners = rows;
  });

  db.all('SELECT * FROM tasks', (err, rows) => {
    if (!err) data.tasks = rows;
  });

  db.all('SELECT * FROM downloads', (err, rows) => {
    if (!err) data.downloads = rows;
  });

  db.all('SELECT * FROM screenshots', (err, rows) => {
    if (!err) data.screenshots = rows;
  });

  db.all('SELECT * FROM credentials', (err, rows) => {
    if (!err) data.credentials = rows;
  });

  db.all('SELECT * FROM targets', (err, rows) => {
    if (!err) data.targets = rows;
  });

  db.all('SELECT * FROM tunnels', (err, rows) => {
    if (!err) data.tunnels = rows;
  });

  db.all('SELECT * FROM chat_messages ORDER BY timestamp DESC LIMIT 100', (err, rows) => {
    if (!err) data.chat = rows;
    ws.send(JSON.stringify(data));
  });
}

function handleWebSocketMessage(ws, data) {
  switch (data.type) {
    case 'auth':
      ws.send(JSON.stringify({ type: 'auth_success' }));
      break;
    case 'sync_request':
      sendInitialData(ws);
      break;
    case 'chat_send':
      const message = {
        id: Date.now().toString(),
        username: 'admin',
        content: data.message,
        type: 'user',
        timestamp: new Date().toISOString()
      };
      
      db.run('INSERT INTO chat_messages (id, username, content, type, timestamp) VALUES (?, ?, ?, ?, ?)',
        [message.id, message.username, message.content, message.type, message.timestamp]);
      
      broadcastMessage({
        type: 'chat_message',
        message: message
      });
      break;
  }
}

function broadcastMessage(message) {
  clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(message));
    }
  });
}

// API Routes
app.post('/endpoint/login', (req, res) => {
  const { username, password } = req.body;
  
  if (username === 'admin' && password === 'Oranolio2024!Secure') {
    const token = jwt.sign(
      { username: username },
      JWT_SECRET,
      { expiresIn: '24h' }
    );
    
    res.json({ token, user: username });
  } else {
    res.status(401).json({ error: 'Invalid credentials' });
  }
});

app.post('/endpoint/refresh', (req, res) => {
  res.json({ message: 'Token refreshed' });
});

app.get('/endpoint/agents', (req, res) => {
  db.all('SELECT * FROM agents', (err, rows) => {
    if (err) {
      res.status(500).json({ error: 'Database error' });
    } else {
      res.json(rows);
    }
  });
});

app.post('/endpoint/agents', (req, res) => {
  const agent = {
    id: Date.now().toString(),
    ...req.body,
    last_seen: new Date().toISOString(),
    status: 'active'
  };
  
  db.run('INSERT INTO agents (id, type, external_ip, internal_ip, computer, user, os, process, last_seen, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
    [agent.id, agent.type, agent.external_ip, agent.internal_ip, agent.computer, agent.user, agent.os, agent.process, agent.last_seen, agent.status],
    function(err) {
      if (err) {
        res.status(500).json({ error: 'Database error' });
      } else {
        broadcastMessage({
          type: 'agent_new',
          agent: agent
        });
        res.status(201).json(agent);
      }
    });
});

app.delete('/endpoint/agents/:id', (req, res) => {
  const id = req.params.id;
  
  db.run('DELETE FROM agents WHERE id = ?', [id], function(err) {
    if (err) {
      res.status(500).json({ error: 'Database error' });
    } else {
      broadcastMessage({
        type: 'agent_remove',
        agentId: id
      });
      res.json({ message: 'Agent deleted' });
    }
  });
});

app.post('/endpoint/agents/:id/command', (req, res) => {
  const agentId = req.params.id;
  const { command } = req.body;
  
  const task = {
    id: Date.now().toString(),
    agent_id: agentId,
    command: command,
    status: 'pending',
    output: '',
    created_at: new Date().toISOString()
  };
  
  db.run('INSERT INTO tasks (id, agent_id, command, status, output, created_at) VALUES (?, ?, ?, ?, ?, ?)',
    [task.id, task.agent_id, task.command, task.status, task.output, task.created_at],
    function(err) {
      if (err) {
        res.status(500).json({ error: 'Database error' });
      } else {
        broadcastMessage({
          type: 'task_update',
          task: task
        });
        res.status(201).json(task);
      }
    });
});

app.get('/endpoint/listeners', (req, res) => {
  db.all('SELECT * FROM listeners', (err, rows) => {
    if (err) {
      res.status(500).json({ error: 'Database error' });
    } else {
      res.json(rows);
    }
  });
});

app.post('/endpoint/listeners', (req, res) => {
  const listener = {
    name: req.body.name || Date.now().toString(),
    ...req.body,
    status: 'active'
  };
  
  db.run('INSERT OR REPLACE INTO listeners (name, type, protocol, host, port, status) VALUES (?, ?, ?, ?, ?, ?)',
    [listener.name, listener.type, listener.protocol, listener.host, listener.port, listener.status],
    function(err) {
      if (err) {
        res.status(500).json({ error: 'Database error' });
      } else {
        broadcastMessage({
          type: 'listener_new',
          listener: listener
        });
        res.status(201).json(listener);
      }
    });
});

app.delete('/endpoint/listeners/:name', (req, res) => {
  const name = req.params.name;
  
  db.run('DELETE FROM listeners WHERE name = ?', [name], function(err) {
    if (err) {
      res.status(500).json({ error: 'Database error' });
    } else {
      broadcastMessage({
        type: 'listener_remove',
        listenerName: name
      });
      res.json({ message: 'Listener deleted' });
    }
  });
});

app.get('/endpoint/tasks', (req, res) => {
  db.all('SELECT * FROM tasks', (err, rows) => {
    if (err) {
      res.status(500).json({ error: 'Database error' });
    } else {
      res.json(rows);
    }
  });
});

app.post('/endpoint/tasks', (req, res) => {
  const task = {
    id: Date.now().toString(),
    ...req.body,
    created_at: new Date().toISOString(),
    status: 'pending'
  };
  
  db.run('INSERT INTO tasks (id, agent_id, command, status, output, created_at) VALUES (?, ?, ?, ?, ?, ?)',
    [task.id, task.agent_id, task.command, task.status, task.output, task.created_at],
    function(err) {
      if (err) {
        res.status(500).json({ error: 'Database error' });
      } else {
        res.status(201).json(task);
      }
    });
});

app.get('/endpoint/downloads', (req, res) => {
  db.all('SELECT * FROM downloads', (err, rows) => {
    if (err) {
      res.status(500).json({ error: 'Database error' });
    } else {
      res.json(rows);
    }
  });
});

app.get('/endpoint/downloads/:id', (req, res) => {
  const id = req.params.id;
  
  db.get('SELECT * FROM downloads WHERE id = ?', [id], (err, row) => {
    if (err) {
      res.status(500).json({ error: 'Database error' });
    } else if (!row) {
      res.status(404).json({ error: 'File not found' });
    } else {
      res.setHeader('Content-Disposition', `attachment; filename=${row.filename}`);
      res.setHeader('Content-Type', 'application/octet-stream');
      res.send(row.content);
    }
  });
});

app.get('/endpoint/screenshots', (req, res) => {
  db.all('SELECT * FROM screenshots', (err, rows) => {
    if (err) {
      res.status(500).json({ error: 'Database error' });
    } else {
      res.json(rows);
    }
  });
});

app.get('/endpoint/credentials', (req, res) => {
  db.all('SELECT * FROM credentials', (err, rows) => {
    if (err) {
      res.status(500).json({ error: 'Database error' });
    } else {
      res.json(rows);
    }
  });
});

app.post('/endpoint/credentials', (req, res) => {
  const credential = {
    id: Date.now().toString(),
    ...req.body
  };
  
  db.run('INSERT INTO credentials (id, username, password, domain, type, host) VALUES (?, ?, ?, ?, ?, ?)',
    [credential.id, credential.username, credential.password, credential.domain, credential.type, credential.host],
    function(err) {
      if (err) {
        res.status(500).json({ error: 'Database error' });
      } else {
        broadcastMessage({
          type: 'credential_new',
          credential: credential
        });
        res.status(201).json(credential);
      }
    });
});

app.get('/endpoint/targets', (req, res) => {
  db.all('SELECT * FROM targets', (err, rows) => {
    if (err) {
      res.status(500).json({ error: 'Database error' });
    } else {
      res.json(rows);
    }
  });
});

app.post('/endpoint/targets', (req, res) => {
  const target = {
    id: Date.now().toString(),
    ...req.body
  };
  
  db.run('INSERT INTO targets (id, computer, domain, address, os, alive) VALUES (?, ?, ?, ?, ?, ?)',
    [target.id, target.computer, target.domain, target.address, target.os, target.alive],
    function(err) {
      if (err) {
        res.status(500).json({ error: 'Database error' });
      } else {
        broadcastMessage({
          type: 'target_new',
          target: target
        });
        res.status(201).json(target);
      }
    });
});

app.get('/endpoint/tunnels', (req, res) => {
  db.all('SELECT * FROM tunnels', (err, rows) => {
    if (err) {
      res.status(500).json({ error: 'Database error' });
    } else {
      res.json(rows);
    }
  });
});

app.post('/endpoint/tunnels', (req, res) => {
  const tunnel = {
    id: Date.now().toString(),
    ...req.body,
    status: 'active'
  };
  
  db.run('INSERT INTO tunnels (id, type, local_host, local_port, remote_host, remote_port, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
    [tunnel.id, tunnel.type, tunnel.local_host, tunnel.local_port, tunnel.remote_host, tunnel.remote_port, tunnel.status],
    function(err) {
      if (err) {
        res.status(500).json({ error: 'Database error' });
      } else {
        broadcastMessage({
          type: 'tunnel_new',
          tunnel: tunnel
        });
        res.status(201).json(tunnel);
      }
    });
});

app.get('/endpoint/chat', (req, res) => {
  db.all('SELECT * FROM chat_messages ORDER BY timestamp DESC LIMIT 100', (err, rows) => {
    if (err) {
      res.status(500).json({ error: 'Database error' });
    } else {
      res.json(rows);
    }
  });
});

app.post('/endpoint/chat', (req, res) => {
  const message = {
    id: Date.now().toString(),
    username: 'admin',
    content: req.body.content,
    type: 'user',
    timestamp: new Date().toISOString()
  };
  
  db.run('INSERT INTO chat_messages (id, username, content, type, timestamp) VALUES (?, ?, ?, ?, ?)',
    [message.id, message.username, message.content, message.type, message.timestamp],
    function(err) {
      if (err) {
        res.status(500).json({ error: 'Database error' });
      } else {
        broadcastMessage({
          type: 'chat_message',
          message: message
        });
        res.status(201).json(message);
      }
    });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>AdaptixC2 404</title>
      <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        h1 { color: #ff5722; }
      </style>
    </head>
    <body>
      <h1>AdaptixC2 404</h1>
      <p>Please enter correct connection details</p>
    </body>
    </html>
  `);
});

// Start server
app.listen(PORT, () => {
  console.log(`Oranolio C2 Server running on port ${PORT}`);
  console.log(`WebSocket server running on port 8080`);
});